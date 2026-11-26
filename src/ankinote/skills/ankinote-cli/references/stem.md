# STEM cards

`stem` takes any question, concept, or problem, in any language, and has no
`--native`/`--target`.

- `--type [auto|concept|formula|procedure|example]`: `auto` (default) spends
  one extra AI call classifying the request. Pick a type when it's obvious:
  `example` for a problem to solve, `formula` for a law or equation,
  `procedure` for "how do I…", `concept` for "what is…".
- `--image <file>` (`add` only): a photographed problem for the AI to solve
  from. Needs a vision-capable text model; with `--type example` it's the
  usual way to turn a homework or textbook problem into a card.
- `--thinking` defaults to `medium` for STEM (a custom endpoint keeps its
  model's default; off for language cards). Use `high` for hard problems.
- Diagrams use the image profile; `--image-size` sets the square size.

```bash
ankinote stem add "What is a derivative?"
ankinote stem add "Solve the problem in this photo" --type example --image problem.jpg
ankinote stem batch --file topics.txt --type concept
```
