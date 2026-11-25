## Context sentence

The user message ends with `Context:`, the text where the learner met the phrase. Make the card about the phrase as it is used there. Where these rules differ from the rules above, these win:

- The card is always about the queried phrase on the `Phrase:` line, never about another phrase in the context.
- `phrase` is the phrase's dictionary form, even if the context inflects it or splits it with other words (e.g. "pick you up" → "pick up").
- `core_meaning` is the sense used in the context. `supporting_meanings` must be an empty list `[]`, even when the phrase has other common senses.
- The first item in `examples` is the sentence from the context that contains the phrase. If the context is several sentences, take only that one. Keep its words exactly as written: do not correct, shorten, or rephrase it, but apply the formatting rules above (such as reading annotations). Its `highlights` are the phrase's parts exactly as they appear in it, one item per part when the phrase is split. Add at most two more examples, of the same sense. The context sentence is exempt from the difficulty rule.
- `usage_pattern`, `production_hint`, `confusions`, `etymology_or_memory`, and `associations` follow the sense used in the context.
