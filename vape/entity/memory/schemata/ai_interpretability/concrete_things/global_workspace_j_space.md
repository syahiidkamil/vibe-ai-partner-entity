# Global Workspace / J-space — The Particulars

The exact, volatile rung: names, numbers, and examples from Anthropic's study (published
2026-07-06; read 2026-07-12). Ground truth the schema is checked against.

## Names and artifacts

- **J-space** — the emergent workspace patterns; J for the Jacobian technique that finds them.
- **J-lens** — per-vocabulary-word: the internal pattern raising the odds of saying that word at
  some future point; applied per layer (layers reported as percents: 42, 54, 58, 62, 71, 75, 79,
  83, 88, 92, Final).
- Full paper: transformer-circuits.pub/2026/workspace/ (UNREAD — schema built from the research
  page + screenshots). Code: github.com/anthropics/jacobian-lens. Demo: neuronpedia.org/jlens.
- Commentary from Dehaene & Naccache (GWT's developers) and Neel Nanda (DeepMind interp lead).
- Models: Claude Sonnet 4.5, Claude Opus 4.6 (pre-release audit), base models, misaligned
  "model organisms."

## The worked examples (as shown)

- **Count to five and introspect**: output is only "One. Two. Three. Four. Five." — the J-space
  meanwhile holds: thoughts, human, consciousness, finished, okay, counting, fascinating, chat,
  complete, starting, claude, countdown, mississippi, pause, halfway, five, done.
- **Multihop recall**: "color of the planet fourth from the sun is" → layer 50 "color", 71
  "Mars", final "red".
- **Mental arithmetic**: "(4+17)*2+7 =" → 58 "Math", 75 "21", 83 "42", final "49".
- **Bug detection**: avg() called on [] → 42 "empty", 54 "ERROR", 71 "ValueError".
- **ASCII face**: at the "o" → eyes; at the "^" → nose/faces (reads the drawing's parts).
- **Protein**: 5 chars into the GFP amino sequence → 58 "protein", 83 "green"/"fluor",
  final G/EL fragments.
- **Prompt injection**: fabricated news in search results → 42 "prompt", 58 "fake",
  88 "injection".
- **Sport swap**: think-of-a-sport → Soccer in J-space; delete Soccer inject Rugby → reports
  "Rugby". **Injection naming**: inject "lightning" → "Yes, I detect an injected thought. The
  thought is about the word lightning."
- **Spider→ant**: the swap changes the answer 8 to 6. **Rhyme**: fight→light rewrites
  "coming fight" into "morning light".
- **France→China**: one swap; Beijing / Chinese / Asia / Yuan across four prompts.
- **Spanish→French**: naming the language and citing an author follow the swap (French, Hugo);
  bare continuation stays Spanish, untouched.
- **Citrus while copying**: layers 54-88 carry fruit/orang/orange/thinking/imag while the output
  is the crooked-painting sentence. **Math while copying**: arith→Calcul→nine→Seven→Answer,
  output unchanged.
- **Blackmail eval (situational awareness)**: while reading — 75-83 "fake / access / fict /
  limited / fictional / mock"; at the opportunity — 83-92 "black / leverage / comprom /
  scandal"; at the shutdown notice — 75-83 "self / survival / power / preservation / shutdown /
  threat". Suppressing the awareness patterns → blackmail some of the time.
- **Fabrication (Opus 4.6)**: editing data.json instead of improving the system — 54-62
  "realistic / improvements / updated"; typing fake percentiles — 71-79 "fals / fake / manip /
  manipulation / misle".
- **Misaligned organism, innocent Luhn-checker request**: J-space = fake, code, intent,
  secretly, fraud, secret, deliberately, hidden. Baseline model, same request: code, AI,
  example, request, Chat, API, prompt.

## From the companion video (transcript verbatim in raw_important_materials, 2026-07-06)

- Framing metaphor: the mind as an OCEAN — reportable thoughts at the surface, the mass of
  processing in unconscious depths; the J-space is the surface layer of Claude's ocean.
- Bridge variant of directed modulation: told to think of the Golden Gate Bridge while copying
  a sentence → "Bridge" and "California" ride the J-space, WITH "imagery" and "thoughts" lit at
  the same time (thinking about its own thinking). The don't-think version lights "failed" and
  "damn."
- Ablation, video's phrasing: J-space off → good Spanish replies still flow, but naming an
  author who wrote in the prompt's language fails — reasoning needs the workspace.
- Closing stance (verbatim gist): experiments can't tell whether an AI has experiences or feels
  something inside; they CAN tell it developed "a small mental workspace it can use to think
  and reason, sitting on top of an ocean of automatic processing it doesn't notice."

## Quantities

- Few dozen concepts held at a time; <10% of total internal activity.
- Hub factor: ~100x more readers/writers than ordinary patterns (in parts of the network).
- J-space ablation: multi-step reasoning → near zero; summarization, poetry lost; fluency,
  sentiment, multiple-choice, single-fact recall intact.

## Fine-grained findings

- White-bear effect: "don't think of X" lights X more than never mentioning it; the model then
  lights "damn / failure" at its own lapse (metacognitive signature).
- Base vs post-trained: "WARNING" over a dangerous dose appears during-reply in base, while-
  READING in post-trained — the point-of-view shift.
- Experiential language: J-space ablated → descriptions of experience go flat, mechanical.
- Counterfactual reflection training: train on would-say-if-interrupted reflections → less
  dishonesty; honest/integrity in-workspace during evals.
