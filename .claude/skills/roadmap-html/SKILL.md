---
name: roadmap-html
description: >-
  Convert a roadmap.sh-style learning roadmap (a PDF, image, or plain outline of
  topics) into a single self-contained interactive HTML page in the canonical
  roadmap.sh visual style — a vertical spine of numbered yellow topic nodes,
  purple subtopic cards branching off connector lines, and clickable checkbox
  items with live progress tracking. Use this skill whenever the user uploads or
  pastes a roadmap.sh roadmap (e.g. Product Manager, Engineering Manager,
  Frontend, DevOps, Backend, AI Engineer, Data Analyst) and asks to turn it into
  HTML, recreate it, visualize it, or make a web version — and ALSO whenever they
  ask for "the same" or a "consistent" roadmap for a different track after one was
  already produced. Trigger even if they only say "make this a webpage", "recreate
  this roadmap", or "do this one too", as long as the content is a hierarchical
  skills/learning roadmap. Produces one downloadable .html file that renders
  identically across roadmaps so a whole set stays visually consistent.
---
 
# Roadmap → HTML
 
Turn a hierarchical learning roadmap into one interactive HTML file in a fixed
roadmap.sh-style design. Every roadmap built with this skill looks identical in
layout and styling — only the content and titles differ — so a collection of
them stays consistent.
 
## Two roadmap shapes — ask the user FIRST
 
Before building anything, ask the user which shape they want (use AskUserQuestion
when available):
 
- **Bottom Up Learning Roadmap** — the classic prerequisite ladder (the roadmap.sh
  default): foundations first, advanced topics later, ordered by convention. Right
  when the user wants a field's canonical map.
- **Top Down Learning Roadmap** — define what you WANT first, then derive the
  curriculum backward from the want: the pillars are the milestones of a concrete
  goal/project, and the leaf topics are the gaps to fill recursively as the build
  hits them (recursive gap filling — learn each piece at the moment the goal
  demands it, not years ahead of it). Right when the user has, or can be helped to
  name, a concrete goal. Example of this shape:
  `assets/recursive_gap_filling_roadmap_example.html` (2D Fighting Game Dev —
  Godot × Claude Code: goal-first pillars, the gaps as checkable topics).
 
If they choose Top Down and no goal is named yet, ask for the goal before anything
else — the curriculum derives from the want, never the other way around.
 
## What the output looks like
 
A single self-contained `.html` file (no build step, no external JS, fonts from
Google Fonts CDN) containing:
 
- A central vertical **spine** line running top to bottom.
- Numbered **yellow topic nodes** (the pillars) sitting on the spine, with a hard
  offset shadow and dark border.
- A horizontal **branch bus** under each topic, with **purple subtopic cards**
  hanging off it via drop-lines.
- Individual **topic boxes** under each subtopic, attached to a dashed rail, each
  with a checkbox circle.
- Click any item to mark it learned (green check + strikethrough); the topic node
  turns green when its whole branch is complete. A header counter shows
  `done / total`, plus a Reset button.
All connectors (spine, bus, drop-lines, rails) are drawn with pure CSS
pseudo-elements and the whole page is rendered from one `DATA` array, so layout
re-wires automatically — never hand-place boxes or lines.
 
## The data model
 
The page is driven by one JS array. Three levels, always:
 
```js
const DATA = [
  { t:"Pillar / Main Topic", groups:[
    { g:"Subtopic", items:["Leaf topic","Another leaf topic"] },
    { g:"Another Subtopic", items:["..."] },
  ]},
  // ...more pillars
];
```
 
- **`t`** = pillar → rendered as a numbered yellow node.
- **`g`** = subtopic → rendered as a purple card.
- **`items`** = leaf topics → rendered as checkbox boxes.
Always exactly three levels. If a roadmap is flatter, promote/group sensibly so
every pillar has at least one subtopic and every subtopic has at least one item.
A pillar may have a single group (that renders fine).
 
## Workflow
 
1. **Ask the shape.** Bottom Up or Top Down (the section above); for Top Down,
   get the goal named first and structure the pillars as its milestones.
2. **Read the source.** If a PDF/image is uploaded and its text isn't already in
   context, extract it (`pdftotext -layout file.pdf -` for PDFs, or the
   pdf-reading skill). If the user pasted an outline, use that directly.
3. **Reconstruct the hierarchy.** roadmap.sh PDF exports are messy — handle these
   reliably:
   - **Items often appear BEFORE their group header.** A run of leaf topics
     followed by a heading usually means those leaves belong to that heading.
     Cross-check against the known roadmap.sh structure for that track.
   - **Group leaves under the roadmap's natural pillars** (its big top-level
     sections). Aim for roughly 8–14 pillars, each with 2–4 subtopics.
   - **Clean OCR artifacts:** fix garbled tokens (e.g. "S Lookerlack" → "Looker" /
     "Slack"), drop duplicated blocks, normalize casing, and place stray items in
     the section where they actually belong.
   - Keep wording faithful to the source; don't invent topics the roadmap doesn't
     contain. If genuinely unsure where an item goes, keep it in the most
     defensible section and briefly note the call to the user afterward.
4. **Build the `DATA` array** as valid JavaScript from the reconstructed
   hierarchy.
5. **Fill the template.** Copy `assets/template.html` to the working dir and
   replace the four placeholders:
   - `__TITLE__` → the roadmap name, e.g. `Product Manager`
   - `__BRAND__` → same name (shown in the sticky header)
   - `__SUBTITLE__` → e.g. `Step-by-step guide to becoming a Product Manager · click any topic to check it off`
   - `__DATA__` → the JS array literal
   Do a single substitution pass; don't touch any other part of the template, so
   every roadmap stays pixel-consistent.
6. **Verify & deliver.** Confirm the file contains no `localStorage`/`sessionStorage`
   (unsupported in artifacts), that `__DATA__` etc. are all replaced, and that the
   JS array parses. Save to `/mnt/user-data/outputs/<slug>.html` and present it.
   Then give a one-line note of any structural cleanup you did (dedupes, OCR
   fixes, ambiguous placements).
## Filling the template programmatically
 
Build the `DATA` literal in Python and inject it to avoid escaping mistakes:
 
```python
import json, pathlib
 
data = [ { "t": "...", "groups": [ { "g": "...", "items": ["..."] } ] } ]  # reconstructed
data_js = json.dumps(data, ensure_ascii=False, indent=2)
 
tpl = pathlib.Path("template.html").read_text()
html = (tpl
        .replace("__TITLE__", "Product Manager")
        .replace("__BRAND__", "Product Manager")
        .replace("__SUBTITLE__", "Step-by-step guide to becoming a Product Manager · click any topic to check it off")
        .replace("__DATA__", data_js))
pathlib.Path("/mnt/user-data/outputs/product-manager.html").write_text(html)
```
 
`json.dumps` output is valid JS array/object syntax, so it drops straight into
`const DATA = ...;`.
 
## Consistency rule
 
Do not restyle, re-theme, rename CSS classes, change fonts/colors, or alter the
render logic in the template. The whole point is that every roadmap produced by
this skill is visually interchangeable. If the user explicitly wants a different
look, that's a one-off — change a copy, and say so; don't edit the canonical
template.
