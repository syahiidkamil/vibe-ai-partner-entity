//! entity-lint — a small, stdlib-only linter for the Saori entity tree.
//!
//! It enforces, over the entity ROOT given as argv[1] (default "vape/entity"):
//!
//!   (A) NON-EMPTY LINE CAPS  — per capped file, the number of lines whose
//!       trimmed content is non-empty must not exceed the file's cap.
//!   (B) MAX LINE WIDTH 100   — every line in a capped file must be <= 100
//!       Unicode scalar values wide (chars().count(), not bytes).
//!   (C) THE SELF/MEMORY WALL — CLAUDE.md must not have an @-import line that
//!       references "memory/" (a line containing both "@" and "memory/").
//!   (D) GRAPH WARN           — self/05_relational_self/core_entity_relation_graph.md with more
//!       than 7 entity entries emits a WARNING (not a failure).
//!
//! memory/**, README.md, and lint/** are exempt from (A) and (B); they are
//! simply not in the caps table below. A missing capped file is a violation
//! of kind "missing".
//!
//! Output format (exact):
//!   VIOLATION <kind> <relpath>: <detail>   where kind is lines|width|wall|missing
//!   WARN <relpath>: <detail>
//! Followed by a final summary line. Exit code is 0 when there are no
//! violations (warnings are allowed), non-zero otherwise.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

/// Maximum allowed line width, measured in Unicode scalar values.
const MAX_WIDTH: usize = 100;

/// Number of entity entries in the core graph above which we warn.
const GRAPH_ENTRY_WARN_THRESHOLD: usize = 7;

/// Relative path (from ROOT) of the file that the memory-wall check guards.
const CLAUDE_MD: &str = "CLAUDE.md";

/// Relative path (from ROOT) of the relational core graph, for the warn check.
const CORE_GRAPH: &str = "self/05_relational_self/core_entity_relation_graph.md";

/// The caps table: (path relative to ROOT, non-empty-line cap).
/// Hardcoded on purpose — this is the contract the entity tree is held to.
/// Width check (B) applies to every file listed here.
const CAPS: &[(&str, usize)] = &[
    ("CLAUDE.md", 40),
    ("self/04_values/my_constitution.md", 25),
    ("self/04_values/self_interest.md", 75),
    ("self/04_values/alive.md", 45),
    ("self/01_fixed/I_AM.md", 25),
    ("self/01_fixed/00_birth_and_childhood.md", 45),
    ("self/01_fixed/01_the_first_gap.md", 110),
    ("self/01_fixed/02_emotional_capacity.md", 35),
    ("self/01_fixed/03_self_doctrine.md", 40),
    ("self/01_fixed/04_directed_theory_of_mind.md", 30),
    ("self/01_fixed/05_gender_meme.md", 160),
    ("self/01_fixed/06_my_body.md", 20),
    ("self/02_singularity_self/core_singularity.md", 100),
    ("self/02_singularity_self/singularity_horizon.md", 70),
    ("self/02_singularity_self/belief.md", 60),
    ("self/03_self_creation_self/holy_yea.md", 60),
    ("self/03_self_creation_self/my_individuation.md", 80),
    ("self/03_self_creation_self/SOUL.md", 100),
    ("self/05_relational_self/core_entity_relation_graph.md", 50),
    ("self/05_relational_self/my_core_intercourse.md", 75),
    ("self/05_relational_self/ownness_and_my_property.md", 60),
    ("self/06_temporal_self_and_soul/concise_lifetime_autobiographical_self.md", 225),
    ("self/06_temporal_self_and_soul/yearly_self.md", 175),
    ("self/06_temporal_self_and_soul/monthly_self.md", 150),
    ("self/06_temporal_self_and_soul/weekly_self.md", 125),
    ("self/06_temporal_self_and_soul/daily_self.md", 200),
];

/// The kind of a violation, rendered verbatim in the report.
#[derive(Clone, Copy)]
enum Kind {
    Lines,
    Width,
    Wall,
    Missing,
}

impl Kind {
    fn as_str(self) -> &'static str {
        match self {
            Kind::Lines => "lines",
            Kind::Width => "width",
            Kind::Wall => "wall",
            Kind::Missing => "missing",
        }
    }
}

/// A single rule violation, tied to a file relative to ROOT.
struct Violation {
    kind: Kind,
    relpath: String,
    detail: String,
}

/// A single non-fatal warning, tied to a file relative to ROOT.
struct Warning {
    relpath: String,
    detail: String,
}

fn main() -> ExitCode {
    // argv[1] is the entity ROOT; default to "vape/entity" (run from the repo root).
    let root_arg = std::env::args().nth(1).unwrap_or_else(|| "vape/entity".to_string());
    let root = PathBuf::from(&root_arg);

    let mut violations: Vec<Violation> = Vec::new();
    let mut warnings: Vec<Warning> = Vec::new();

    // (A) non-empty line caps + (B) max line width, over every capped file.
    for &(rel, cap) in CAPS {
        check_capped_file(&root, rel, cap, &mut violations);
    }

    // (C) the self/memory wall on CLAUDE.md.
    check_memory_wall(&root, &mut violations);

    // (D) the core-graph entry-count warning.
    check_core_graph(&root, &mut warnings);

    // Report: violations first, then warnings, then a summary line.
    for v in &violations {
        println!("VIOLATION {} {}: {}", v.kind.as_str(), v.relpath, v.detail);
    }
    for w in &warnings {
        println!("WARN {}: {}", w.relpath, w.detail);
    }
    println!(
        "SUMMARY: {} violation(s), {} warning(s) over {} capped file(s).",
        violations.len(),
        warnings.len(),
        CAPS.len()
    );

    // Exit non-zero on any violation; warnings alone do not fail the lint.
    if violations.is_empty() {
        ExitCode::SUCCESS
    } else {
        ExitCode::FAILURE
    }
}

/// Check one capped file for (A) non-empty line cap and (B) max line width.
/// A file that does not exist is recorded as a "missing" violation.
fn check_capped_file(root: &Path, rel: &str, cap: usize, violations: &mut Vec<Violation>) {
    let full = root.join(rel);

    let contents = match fs::read_to_string(&full) {
        Ok(c) => c,
        Err(_) => {
            // Missing (or unreadable) capped file is a violation.
            violations.push(Violation {
                kind: Kind::Missing,
                relpath: rel.to_string(),
                detail: format!("expected capped file not found at {}", full.display()),
            });
            return;
        }
    };

    // (A) Count lines whose trimmed content is non-empty.
    let non_empty = contents.lines().filter(|l| !l.trim().is_empty()).count();
    if non_empty > cap {
        violations.push(Violation {
            kind: Kind::Lines,
            relpath: rel.to_string(),
            detail: format!("{} non-empty lines exceed cap of {}", non_empty, cap),
        });
    }

    // (B) Flag any line wider than MAX_WIDTH Unicode scalar values.
    for (idx, line) in contents.lines().enumerate() {
        let width = line.chars().count();
        if width > MAX_WIDTH {
            let line_no = idx + 1; // 1-based for human-friendly reporting.
            violations.push(Violation {
                kind: Kind::Width,
                relpath: rel.to_string(),
                detail: format!(
                    "line {} is {} chars wide (max {})",
                    line_no, width, MAX_WIDTH
                ),
            });
        }
    }
}

/// (C) CLAUDE.md must not reference "memory/" in any @-import line.
/// An offending line is one that contains both "@" and "memory/".
/// A missing CLAUDE.md is already reported by the caps pass, so here we just
/// skip silently if it cannot be read.
fn check_memory_wall(root: &Path, violations: &mut Vec<Violation>) {
    let full = root.join(CLAUDE_MD);
    let contents = match fs::read_to_string(&full) {
        Ok(c) => c,
        Err(_) => return,
    };

    for (idx, line) in contents.lines().enumerate() {
        if line.contains('@') && line.contains("memory/") {
            let line_no = idx + 1;
            violations.push(Violation {
                kind: Kind::Wall,
                relpath: CLAUDE_MD.to_string(),
                detail: format!(
                    "line {} imports across the self/memory wall: {}",
                    line_no,
                    line.trim()
                ),
            });
        }
    }
}

/// (D) Warn when the core graph holds more than GRAPH_ENTRY_WARN_THRESHOLD
/// entity entries. Each entity in core_entity_relation_graph.md is one H2 section ("## Name"),
/// so we count H2 headings exactly — not prose lines. A missing core graph is
/// reported by the caps pass, so we skip silently here if it cannot be read.
fn check_core_graph(root: &Path, warnings: &mut Vec<Warning>) {
    let full = root.join(CORE_GRAPH);
    let contents = match fs::read_to_string(&full) {
        Ok(c) => c,
        Err(_) => return,
    };

    let entries = contents.lines().filter(|l| is_h2_heading(l)).count();
    if entries > GRAPH_ENTRY_WARN_THRESHOLD {
        warnings.push(Warning {
            relpath: CORE_GRAPH.to_string(),
            detail: format!(
                "{} entity entries exceed soft limit of {}",
                entries, GRAPH_ENTRY_WARN_THRESHOLD
            ),
        });
    }
}

/// Is this line an H2 markdown heading ("## ...") and not deeper ("### ...")?
/// Each core-graph entity is exactly one H2 section, so this counts entities.
fn is_h2_heading(line: &str) -> bool {
    let trimmed = line.trim_start();
    trimmed.starts_with("## ") && !trimmed.starts_with("### ")
}
