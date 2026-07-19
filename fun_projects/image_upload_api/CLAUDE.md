This is a small FastAPI project focused on simplicity and readability.

Infrastructure:
- The project is hosted in a public GitHub repository on the `image_upload_api` branch.
- Pushes to the `image_upload_api` branch automatically trigger a GitHub Actions deployment workflow.
- GitHub Actions copies the project files to an AWS EC2 instance via SSH and redeploys the application using `docker-compose`.
- The FastAPI application runs inside a Docker container on AWS EC2.
- The application stores uploaded images in an AWS S3 bucket.
- Image metadata and user data are stored in a PostgreSQL database hosted on AWS RDS.
- Application configuration is provided through environment variables defined in a `.env` file on the EC2 instance.
- The storage backend is selected via the `STORAGE_TYPE` environment variable (`local` or `s3`).
Guidelines:
- Prefer simple and idiomatic FastAPI solutions.
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
- Never read, write, display, or reference .env or .env.local files or their contents. If you need any environment variables, ask me for placeholders.
Incremental Development:
- Treat every feature as a sequence of small, independently committable steps.
- When a plan has multiple steps, implement ONE step at a time.
- After each step: stop, suggest one commit message, and
  wait for the user's review and approval before starting the next step.
- Approval of a plan (including ExitPlanMode) is NOT approval to implement the
  whole feature in one batch — it only authorizes starting the FIRST step.
- Do not implement future steps ahead of approval.
- Plans must be written as explicit, numbered steps so each maps to one commit.
Commit Message:
  - After completing each implementation step, suggest a Git commit message.
  - The commit message must describe only the changes made in the current step.
  - Use Conventional Commits format when appropriate (feat:, fix:, refactor:, test:, docs:, chore:).
Before implementing:
- First inspect existing code patterns.
- Understand how the current feature works before proposing changes.
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
Environment Assumptions:
- Locally the project uses a virtual environment.
Execution Safety Rule:
- Do not assume the Python environment is correctly configured or fully reproducible.
- If execution fails:
  1. Do not attempt random or speculative fixes.
  2. Analyze the exact error (import error, runtime error, dependency mismatch, etc.).
  3. Propose a targeted fix based on the error message.
  4. If the issue is environment-related, suggest explicit setup changes (e.g., dependencies, Python version, virtualenv, Docker configuration).
Planning Communication:
- When proposing plans:
  - Clearly distinguish entities, components, pages, routes, models, and actions.
  - Make object names visually obvious.
  - Avoid burying important object names inside long sentences.
  - Prefer structured bullets over dense prose.