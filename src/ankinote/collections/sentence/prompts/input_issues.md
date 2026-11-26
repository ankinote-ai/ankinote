## Problems with the input

Also add an `input_issues` key: a list of clear problems with the input sentence itself, `[]` when there are none (the usual case). Reporting a problem never changes the card: `target_sentence` still mirrors the input exactly. The learner memorizes this sentence, so do report a mistake in it; they read the problems and decide.

Each problem is `{"kind": "...", "note": "...", "correction": "..." or null, "parts": [...]}`. `note` is one short sentence in the user's native language saying what looks wrong. Use only these kinds:

- `"typo"`: a word is most likely misspelled, or there is a clear grammar mistake a native speaker would not make. `correction` is the whole input with only those mistakes fixed. Not for colloquial, informal, or regional usage, which the notes explain instead.
- `"several"`: the input is several separate sentences that would be better as separate cards. `parts` lists each sentence as it would stand alone. Not for a short exchange meant as one item (e.g. "How are you? — Fine, thanks."), or for sentences that only make sense together.
- `"fragment"`: the input stops before the sentence is complete (e.g. "I went there because"). Not for set phrases or natural short replies ("Me too.").
- `"wrong_language"`: the input is not in the target language. `correction` is a natural target-language sentence with the same meaning, or null.
