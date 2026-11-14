# Rust API — CLAUDE.md

```markdown
# Rust API

## Stack
- Framework: Axum 0.7
- Database: sqlx + PostgreSQL
- Async: Tokio
- Testing: cargo test + testcontainers

## Folder Layout
\`\`\`
src/
├── main.rs
├── routes/     # Axum router definitions
├── handlers/   # Request handlers
├── models/     # DB structs
├── services/   # Business logic
└── error.rs    # AppError enum
\`\`\`

## Error Handling
\`\`\`rust
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("Not found")]
    NotFound,
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}

impl IntoResponse for AppError { ... }
\`\`\`

## Run
\`\`\`bash
cargo run
cargo test
cargo clippy -- -D warnings
\`\`\`

## Key Rules
- No `.unwrap()` in production code — use `?` operator
- All DB queries via sqlx macros (compile-time checked)
- `#[deny(clippy::unwrap_used)]` in lib.rs
\`\`\`
