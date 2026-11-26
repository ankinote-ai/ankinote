## Problems with the input

Also add an `input_issues` key: a list of clear problems with the queried phrase itself, `[]` when there are none (the usual case). Apart from a misspelling (see `"corrected"`), reporting a problem never changes the card: follow the rules above for the phrase as given. The learner reads the problems and decides.

Each problem is `{"kind": "...", "note": "...", "correction": "..." or null, "parts": [...]}`. `note` is one short sentence in the user's native language saying what looks wrong. Use only these kinds:

- `"corrected"`: a word in the phrase is clearly misspelled, or the fixed expression is clearly misremembered (e.g. "piece of cack"). Make the card for the correct phrase, never for the mistaken one, and give the whole corrected phrase as `correction`. Only when you are sure: not for valid variants of an expression or a phrase that is correct but less common. If the user message says the spelling is as typed, never use this kind.
- `"wrong_language"`: the phrase is not in the target language. `correction` is the target-language phrase it most likely means, or null. Not for loanwords used in the target language.
- `"several"`: the input is several separate phrases that belong on separate cards (e.g. "give up; look after"). `parts` lists each one as it would stand alone. Not for one expression with alternatives or optional words ("make (both) ends meet").
