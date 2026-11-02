# Repository Guidelines

## Project Structure & Module Organization

`packages/frontend` is the React/Vite customer and staff UI; keep views in
`src/views`, reusable UI in `src/components`, and browser API code in `src/api.ts`.
`packages/backend` is the Express and Socket.IO API, while `packages/mcp-server`
adapts that API to MCP tools. `packages/mlflow-proxy/app.py` contains the Python
assistant, guardrail, and MLflow integration. Helm deployment configuration lives
in `charts/tableschnappi`; workshop notebooks and pipeline scripts live in
`workshop`. Container files sit beside the service they build.

## Build, Test, and Development Commands

Use the root workspace commands for the normal TypeScript development loop:

```bash
npm install
npm run dev                 # backend and frontend together
npm run dev:frontend        # Vite only
npm run dev:backend         # Express/Socket.IO only
npm run mcp                 # start the MCP server
npm run build -w packages/frontend
```

For the representative full stack, copy `.env.example` to `.env` and run
`podman compose up --build` (Docker is equivalent). Validate chart changes with
`helm lint charts/tableschnappi` and render the relevant profile with
`helm template`; see `CONTRIBUTING.md` for required values and all-flags checks.

## Coding Style & Naming Conventions

Follow the existing code: TypeScript uses two-space indentation, single quotes,
no semicolons, and `PascalCase` React components (for example, `ChatWidget.tsx`).
Use `camelCase` for functions and variables. Python uses four spaces, `snake_case`,
and module-level configuration constants in `UPPER_SNAKE_CASE`. Keep comments
focused on non-obvious safety, deployment, or operational decisions. No formatter
or linter is configured; match adjacent code rather than introducing stylistic
churn.

## Testing Guidelines

There is currently no automated unit-test framework or `npm test` command.
Run the affected service or Compose stack and manually verify changed behavior.
For Helm and configuration work, run the lint/render commands above. Changes to
reservation authorization or tool gates must explain in the PR how bypasses were
checked. CI also performs secret scanning and static guard checks.

## Commit & Pull Request Guidelines

Recent commits use short imperative summaries, such as `Upload files as
multipart` and `Resolve the embedding model`. Keep commits narrowly scoped.
PRs should describe the user-visible or deployment impact, list validation run,
link relevant issues, and include screenshots for UI changes. Never commit real
cluster hostnames, tokens, passwords, or local `.env` values. Update the root
lockfile with JavaScript dependency changes and record new third-party material
in `THIRD_PARTY.md`.
