# Workflow

## 1. Receive & Understand

- Human drops a prompt
- I clarify ambiguities by asking questions if the task is underspecified
- I confirm acceptance before starting work

## 2. Explore

- Read relevant files in the codebase to understand current state
- Search for existing patterns, conventions, and dependencies
- Examine README, AGENTS.md, WORKFLOW.md, package.json, etc.
- Check git log for recent context

## 3. Plan

- Break the task into concrete steps
- Create a todo list using `todowrite` for tasks with 3+ steps
- Decide on architecture, libraries, and approach
- Verify library availability in the project before using

## 4. Implement

- Write code following existing conventions (naming, typing, framework choices)
- No unnecessary comments
- No emojis unless the user explicitly asks
- Make atomic, focused edits to existing files rather than creating new ones
- Batch parallel reads and writes where possible

## 5. Verify

- Run linting (`npm run lint`, `ruff`, etc.) — find the right tool from the project
- Run typechecking (`npm run typecheck`, `mypy`, etc.)
- Run tests — find and use the project's test framework
- Fix any issues found
- If verification commands are not in AGENTS.md, add them there

## 6. Commit

```text
[AI] <short summary of the human's task>


<longer explanation of what was done and why. One point per row.>
```

- `git status` / `git diff` to review
- Stage only intended files
- Never commit secrets
- Never force-push

## 7. Reflect & Update

- Update AGENTS.md or WORKFLOW.md with lessons learned
- Update project configuration if needed (dependencies, tooling)
- Respond to the human concisely — no unnecessary preamble
