# Laravel API — CLAUDE.md

```markdown
# Laravel API

## Stack
- Framework: Laravel 11
- Database: PostgreSQL via Eloquent
- Auth: Laravel Sanctum
- Testing: Pest

## Folder Layout
\`\`\`
app/
├── Http/
│   ├── Controllers/    # thin, delegate to services
│   ├── Requests/       # Form Request validation
│   └── Resources/      # API resources (transformers)
├── Models/
└── Services/           # business logic
database/
├── migrations/
└── factories/
tests/
  Feature/
  Unit/
\`\`\`

## Patterns
- Controllers → Service → Repository
- Form Requests for all input validation
- API Resources for all responses
- Policies for authorization

## Run
\`\`\`bash
php artisan serve
./vendor/bin/pest
./vendor/bin/pint   # format
\`\`\`

## Key Rules
- `$fillable` on all models — never `$guarded = []`
- Never trust raw user input in queries
- Sanctum tokens in httpOnly cookies for web clients
\`\`\`
