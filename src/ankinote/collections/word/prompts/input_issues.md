## Problems with the input

Also give the first record an `input_issues` key: a list of clear problems with the queried word itself, `[]` when there are none (the usual case). Other records get `[]`. Apart from a misspelling (see `"corrected"`), reporting a problem never changes the card: make it as the rules above say. The learner reads the problems and decides.

Each problem is `{"kind": "...", "note": "...", "correction": "..." or null, "parts": [...]}`. `note` is one short sentence in the user's native language saying what looks wrong. Use only these kinds:

- `"corrected"`: the input is not a word of the target language but clearly a misspelling of one (e.g. "recieve"). Make the card for the correctly spelled word, never for the misspelling, and give it as `correction`. Only when you are sure: not for valid variant spellings (British/American), real but rare words, or a real word that might be confused with another ("affect"/"effect"); those are not problems. If the user message says the spelling is as typed, never use this kind.
- `"wrong_language"`: the word is not in the target language (e.g. a native-language word). `correction` is the target-language word it most likely means, or null. Not for loanwords used in the target language.
- `"several"`: the input is several separate words or items that belong on separate cards (e.g. "apple, pear"). `parts` lists each one as it would stand alone. Not for compounds, separable verbs, or a word with its article.
