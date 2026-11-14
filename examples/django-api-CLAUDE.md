# Django REST API — CLAUDE.md

```markdown
# Django REST API

## Stack
- Framework: Django 5.x + Django REST Framework
- Database: PostgreSQL via psycopg3
- Auth: JWT (djangorestframework-simplejwt)
- Testing: pytest-django + factory_boy

## Folder Layout
\`\`\`
config/         # settings, urls, wsgi
apps/
├── users/      # User model, auth
├── core/       # shared utilities, base models
└── <domain>/   # feature apps
\`\`\`

## Patterns
- Service layer in `apps/<domain>/services.py`
- Serializers only for I/O, not business logic
- Managers for reusable querysets
- Custom permissions in `apps/core/permissions.py`

## Run
\`\`\`bash
python manage.py runserver
pytest
black . && ruff check .
\`\`\`

## Key Rules
- Never put business logic in views or serializers
- Parameterized queries only — no raw SQL string formatting
- `select_related` / `prefetch_related` to prevent N+1
\`\`\`
