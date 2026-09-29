# Model routing

Use the user's explicit model choice and current host/repository policy first.
These defaults cover bounded work when no more specific routing policy exists;
they do not replace the host's choices for complex or consequential work.
Choose by the actual task rather than the skill name.

## Bounded work defaults

Checked on 2026-09-29:

| Host | Model | Reasoning effort | Work |
| --- | --- | --- | --- |
| Claude Code | `sonnet` (Sonnet 5.5 on Anthropic) | `medium` | Task contracts, ordinary implementation and fixes, focused tests, short status and handoffs |
| Codex | `gpt-6.1-sol` | `medium` | Task contracts, ordinary implementation and fixes, focused tests, routine design reviews |

Raise effort for careful integration or verification when needed. Preserve
existing routes for read-only work, architecture, security, difficult root
causes, and visual production. An updated bounded-work model does not move
every workflow or delegate onto that model.

## Claude Code

Keep skill and agent entries on `model: sonnet`. On Anthropic, the current
alias resolves to Sonnet 5.5 (`claude-sonnet-5-5`), which requires Claude Code
2.1.284 or later. Run `claude update` when the installed client is older, then
restart existing sessions. Other providers can resolve the alias differently;
check the provider's supported mapping before selecting an exact model ID.

## Codex

Confirm `gpt-6.1-sol` in the running host's model catalog before selecting it
for a new task or an already authorized delegate. A Codex `SKILL.md` does not
switch the active conversation's model, and Claude `model:` frontmatter is
not a Codex model pin. Keep variable-complexity workflows on the model chosen
for their actual work. Do not create a task or agent solely to change models.

## Verification and sources

The Sonnet mapping and minimum version were checked against
[Claude Code model configuration](https://code.claude.com/docs/en/model-config).
The Sol ID was verified in the installed Codex host's model catalog and
[OpenAI's model guidance](https://learn.chatgpt.com/docs/models).
These are configuration checks, not measured workflow benchmarks or a
guarantee that either model is available to every account or provider.
