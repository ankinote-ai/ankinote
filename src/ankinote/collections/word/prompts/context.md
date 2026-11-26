## Context sentence

The user message ends with `Context:`, the text where the learner met the word. Make the card about the word as it is used there. Where these rules differ from the rules above, these win:

- The card is always about the queried word on the `Word:` line, never about another word in the context.
- The queried word may come in parts joined by " … " when the context splits it (e.g. German "rufe … an" from "Ich rufe dich morgen an"): the card is about the one word they form there ("anrufen"). In the context sentence's `highlights`, give each part exactly as it appears there, one item per part ("rufe", "an").
- Return exactly 1 record: the part of speech the word has in the context. `lemma` is its dictionary form, even if the context uses an inflected form.
- `core_meaning` gives only the sense used in the context: one sense in `target_text` and one in `native_text`, with no '; '-separated list.
- The first item in `examples` is the sentence from the context that contains the word. If the context is several sentences, take only that one. Keep its words exactly as written: do not correct, shorten, or rephrase it, but apply the formatting rules above (such as reading annotations). Give its translation and highlights like any example. Add at most one more example, of the same sense. The context sentence is exempt from the difficulty rule.
- `is_visualizable`, `image_prompt`, `collocations`, `confusions`, and `etymology_or_memory` follow the sense used in the context.
- If the context does not contain the queried word (in any form), still make the card as these rules say, and add an `input_issues` item of kind `"context_mismatch"` (`correction` null, `parts` []) whose `note` says so.
