# Go Microservice — CLAUDE.md

```markdown
# Go Microservice

## Stack
- Language: Go 1.22+
- HTTP: chi router
- Database: PostgreSQL via pgx
- Config: envconfig
- Testing: testify + httptest

## Folder Layout
\`\`\`
cmd/
  server/         # main entrypoint
internal/
  api/            # HTTP handlers
  service/        # business logic
  repository/     # DB access (interfaces + postgres impl)
  domain/         # types, errors
pkg/              # exported packages
\`\`\`

## Patterns
- Repository interfaces defined in `internal/domain/`
- Postgres implementations in `internal/repository/postgres/`
- Services receive repository interfaces — never concrete types
- All errors wrapped with `fmt.Errorf("context: %w", err)`

## Build
\`\`\`bash
go build ./...
go test -race ./...
golangci-lint run
\`\`\`

## Key Rules
- Context passed as first arg to all functions that do I/O
- No global mutable state
- Table-driven tests only
\`\`\`
