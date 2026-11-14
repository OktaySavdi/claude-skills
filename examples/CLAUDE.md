# Example Project CLAUDE.md

Copy this to your project root as `CLAUDE.md` and customize for your project.

```markdown
# Project Name

## What This Project Does
Brief description of the project purpose and domain.

## Stack
- Language: TypeScript / Python / Go
- Framework: Next.js / Django / Gin
- Database: PostgreSQL
- Infrastructure: Kubernetes on AKS
- CI/CD: Azure DevOps / GitHub Actions

## Folder Layout
\`\`\`
src/
├── api/         # API route handlers
├── services/    # Business logic
├── models/      # Data models / DB access
├── utils/       # Shared utilities
└── types/       # Shared TypeScript types
tests/
  unit/
  integration/
\`\`\`

## Build & Run
\`\`\`bash
npm install
npm run dev       # development server
npm run build     # production build
npm test          # run tests
\`\`\`

## Key Conventions
- All API errors return `{ error: string, code: string }`
- Authentication via JWT in `Authorization: Bearer <token>` header
- Database: use Prisma ORM, never raw SQL strings

## Important Constraints
- Do NOT add features beyond what was asked
- Tests required for every new function
- Never commit `.env` files
\`\`\`
