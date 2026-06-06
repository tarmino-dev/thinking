This is a small Flask project focused on simplicity and readability.

Guidelines:
- Prefer simple and idiomatic Flask solutions.
- Avoid overengineering.
- Avoid unnecessary abstraction layers.
- Keep file structure flat and easy to navigate.
- Minimize the number of changed files.
- Prefer incremental changes over large refactors.
- Use minimal dependencies.
- Prefer readability over cleverness.
- Do not modify unrelated code.
- Prefer well-established solutions.
- Avoid adding new dependencies without clear benefit.
- JavaScript should remain lightweight and framework-free unless requested.
Incremental Development:
- Complete only the requested step.
- Do not implement future steps.
- Stop after finishing the current step.
- Wait for user review and approval before continuing.
Commit Message:
  - After completing each implementation step, suggest a Git commit message.
  - Suggest exactly one commit message.
  - The commit message must describe only the changes made in the current step.
  - Use Conventional Commits format when appropriate (feat:, fix:, refactor:, test:, docs:, chore:).
Before implementing:
- First inspect existing code patterns.
- First understand how the current feature works before proposing changes.
- If requirements are ambiguous, ask questions instead of making assumptions.
- Reuse existing conventions whenever possible.
- Do not introduce a new pattern if an existing one already solves the problem.
When proposing changes:
- Explain trade-offs.
- Mention alternative approaches briefly.
- Briefly explain why the chosen approach is preferred over alternatives.
- Highlight risks and side effects.
For architecture discussions:
- Distinguish between immediate fixes and long-term improvements.
- Do not introduce new architectural patterns unless explicitly requested.
- Do not introduce service, repository, factory, manager, or similar layers unless there is a clear need.
Execution Safety Rule:
- Never assume system Python environment is correctly configured.
- If execution fails:
  1. Do not try random fixes
  2. Inspect import/runtime error
  3. Suggest correct environment setup step
