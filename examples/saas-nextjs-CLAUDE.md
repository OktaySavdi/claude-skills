# SaaS Next.js + Supabase + Stripe — CLAUDE.md

Place this in the root of your Next.js SaaS project.

```markdown
# SaaS App

## Stack
- Framework: Next.js 15 (App Router)
- Auth + DB: Supabase (PostgreSQL + Auth)
- Payments: Stripe Subscriptions
- Styling: Tailwind CSS + shadcn/ui
- Deploy: Vercel

## Folder Layout
\`\`\`
app/
├── (auth)/         # login, signup, forgot-password
├── (dashboard)/    # protected routes
├── api/            # route handlers
└── layout.tsx
lib/
├── supabase/       # client, server, middleware helpers
├── stripe/         # checkout, webhooks
└── utils.ts
components/
├── ui/             # shadcn components
└── ...             # app components
\`\`\`

## Auth Pattern
- Supabase SSR auth with `@supabase/ssr`
- Middleware refreshes session on every request
- Server Components read session from `createServerClient`
- Client Components use `createBrowserClient`

## Payments
- Stripe Checkout for subscription start
- Webhook at `/api/webhooks/stripe` handles events
- Subscription status stored in `profiles` table

## Key Rules
- Never expose `SUPABASE_SERVICE_ROLE_KEY` to client
- Validate Stripe webhook signatures — never trust raw POST body
- Use RLS on all Supabase tables
\`\`\`
