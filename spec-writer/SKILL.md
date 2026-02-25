---
name: spec-writer
description: >
  Generate implementation-ready technical specifications from research reports about
  products or startups. Takes a markdown report and produces a detailed spec that a
  coding agent (Claude Code, Codex, etc.) can implement in a single pass. All technical
  decisions made autonomously — no user questions, no ambiguity. Use for: (1) Converting
  research/deep-research reports into buildable specs, (2) Recreating defunct startup
  products with modern tech, (3) Batch spec generation from multiple reports.
---

# Spec Writer

Transform a research report into an implementation-ready technical specification. The output must be detailed enough for a coding agent to build the complete, functional app in a single pass with zero follow-up questions.

## Input

A markdown research report about a startup or product. May include company history, funding, team, market position, traction, post-mortem analysis, and lessons. Extract only what the product DID — ignore business narrative.

## Process

1. **Extract the product.** What did users do? What problem did it solve? What were the core features? Identify every user-facing capability mentioned or implied.

2. **Infer missing features.** Research reports describe products at a high level. Reconstruct the full feature set that MUST have existed. A "blogging platform" implies: user accounts, post editor, media uploads, public pages, themes, RSS, SEO tags, etc. Be comprehensive but stay grounded in what the report describes — don't invent features the product didn't have.

3. **Scope the build.** Include every feature that defined the product experience. If the report describes it, spec it. Only exclude features that were clearly late additions, acquisitions, or enterprise-only. Err on the side of including more, not less — the coding agent can handle it.

4. **Modernize.** Rebuild the product concept with 2026 technology. Keep the core value proposition but update the implementation.

5. **Research current versions.** Before writing, use web search (Firecrawl if available, otherwise WebSearch) to verify: latest stable versions of all frameworks, libraries, and tools you plan to use; current best practices for the chosen stack; latest LLM model names/IDs if the product uses AI. Pin every version in the spec — the coding agent must not guess.

6. **Decide everything.** Pick one stack, one architecture, one approach for every decision. Never present alternatives. Never say "you could use X or Y." Commit.

7. **Write the spec.** Follow the output format exactly. Every section must be concrete and complete.

## Tech Stack Defaults

Pick the simplest modern stack that delivers the product:

**Web applications:** Next.js 15 (App Router), TypeScript strict mode, Tailwind CSS, shadcn/ui, PostgreSQL, Drizzle ORM, Better Auth, Vercel deployment

**CLI tools:** Node.js, TypeScript, Commander.js, SQLite (better-sqlite3)

**APIs/services:** Hono, TypeScript, PostgreSQL, Drizzle ORM

**Real-time features:** Add Ably or Soketi when the product requires live updates

Override defaults when the product demands it. An email-processing app needs mail parsing libraries. A media-heavy app needs object storage (S3/R2). A real-time collaboration tool needs CRDTs. Let the product drive the stack.

**Always use latest stable versions.** Research current versions before writing the spec. Pin exact versions — `next@15.2.3` not `next@15`. If the product uses AI/LLM features, specify the exact model ID (e.g., `claude-sonnet-4-20250514`, `gpt-4o-2024-11-20`).

## Output Format

Produce a single markdown document with these sections in order:

### 1. Overview

```markdown
# [Product Name]

[2-3 sentences: what this app does, who uses it, core value proposition.
Modern reinterpretation — not a history lesson.]
```

### 2. Core Features

Bulleted list grouped by area. Every feature is concrete and implementable:

```markdown
**Publishing**
- Create posts from web editor with rich text (bold, italic, links, headings, images)
- Create posts by sending email to ingest@app.com — parse subject as title, body as content
- Schedule posts for future publication
- Save drafts, preview before publishing
```

### 3. User Flows

For each core flow, numbered steps showing user actions and system responses:

```markdown
## Email-to-Post Flow
1. User sends email to post@app.com with subject line and body
2. System receives email via Resend inbound webhook at POST /api/inbound
3. System extracts sender email, matches to user account
4. System parses subject as post title, HTML body as content
5. System extracts inline images, uploads to R2, replaces with URLs
6. System creates post with status "draft", sends confirmation email
7. Post appears in user's dashboard draft list
```

### 4. Tech Stack

Table with every dependency:

```markdown
| Category | Package | Purpose |
|----------|---------|---------|
| Framework | next@15 | Full-stack React framework |
| Language | typescript@5.7 | Type safety |
| Styling | tailwindcss@4 | Utility-first CSS |
| Components | shadcn/ui | Pre-built accessible components |
| Database | postgresql@17 | Primary data store |
| ORM | drizzle-orm | Type-safe queries and migrations |
| Auth | better-auth | Email/password + OAuth authentication |
| Email | resend | Transactional email + inbound parsing |
| Storage | @aws-sdk/client-s3 | Media uploads to Cloudflare R2 |
```

### 5. Project Structure

Full directory tree with a comment explaining every file's purpose:

```
project/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout, providers, fonts
│   │   ├── page.tsx                # Landing/marketing page
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx      # Login form
│   │   │   └── signup/page.tsx     # Registration form
│   │   ├── (app)/
│   │   │   ├── layout.tsx          # Authenticated layout with sidebar
│   │   │   ├── dashboard/page.tsx  # Post list, stats overview
│   │   │   ├── posts/
│   │   │   │   ├── new/page.tsx    # Post editor (create)
│   │   │   │   └── [id]/page.tsx   # Post editor (edit)
│   │   │   └── settings/page.tsx   # Account settings
│   │   └── api/
│   │       ├── posts/route.ts      # CRUD for posts
│   │       ├── inbound/route.ts    # Email ingestion webhook
│   │       └── auth/[...all]/route.ts  # Better Auth handler
│   ├── components/
│   │   ├── ui/                     # shadcn/ui components
│   │   ├── post-editor.tsx         # Rich text editor component
│   │   └── post-card.tsx           # Post preview card
│   ├── db/
│   │   ├── schema.ts              # Drizzle table definitions
│   │   ├── index.ts               # Connection + export
│   │   └── seed.ts                # Seed data script
│   └── lib/
│       ├── auth.ts                # Better Auth config
│       ├── auth-client.ts         # Client-side auth helpers
│       └── storage.ts             # R2 upload helpers
├── drizzle.config.ts
├── .env.example
└── package.json
```

### 6. Database Schema

Complete Drizzle schema OR SQL DDL. Every table, column, type, constraint, index, relationship:

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  avatar_url TEXT,
  email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT NOT NULL,
  content TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'scheduled')),
  published_at TIMESTAMPTZ,
  scheduled_for TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, slug)
);

CREATE INDEX idx_posts_user_status ON posts(user_id, status);
CREATE INDEX idx_posts_slug ON posts(slug);
```

Include every table. Include seed data SQL if the app needs initial data to function.

### 7. API Routes

For each endpoint, specify method, path, auth, request/response types, and behavior:

```markdown
### POST /api/posts
Auth: Required (session cookie)
Request: { title: string, content: string, status?: "draft" | "published" }
Response 201: { id: string, title: string, slug: string, status: string, createdAt: string }
Response 401: { error: "Unauthorized" }
Behavior:
  - Generate slug from title: lowercase, replace spaces with hyphens, remove special chars
  - If slug exists for this user, append -2, -3, etc.
  - If status is "published", set publishedAt to now
```

### 8. Pages & UI

For each page, specify route, layout, components, interactions, and all states:

```markdown
### /dashboard
Route: /(app)/dashboard
Layout: Sidebar nav + main content area
Components:
  - PageHeader: "Dashboard" title, "New Post" button (links to /posts/new)
  - StatsRow: cards showing [Total Posts, Published, Total Views] from DB aggregation
  - PostsTable: sortable table with columns [Title, Status badge, Created date, Actions dropdown]
  - Actions dropdown: Edit (→ /posts/[id]), Delete (confirm dialog → DELETE /api/posts/[id])
States:
  - Loading: Skeleton placeholders for stats cards and table rows
  - Empty: Illustration + "No posts yet. Create your first post." + CTA button
  - Error: Toast notification with error message and retry button
  - Success: Populated stats and table with pagination (20 per page)
```

### 9. Authentication

Specify the exact auth setup, protected route pattern, and session handling:

```markdown
## Auth Setup
Provider: Better Auth with email/password
Session: Cookie-based, 30-day expiry
Protected routes: All /(app)/* routes require authentication via middleware
Middleware: src/middleware.ts checks session, redirects to /login if missing

## Signup Flow
1. POST /api/auth/sign-up with { email, password, name }
2. Better Auth creates user, sends verification email
3. User clicks link → email verified → redirect to /dashboard

## Login Flow
1. POST /api/auth/sign-in with { email, password }
2. Better Auth validates, sets session cookie
3. Redirect to /dashboard
```

### 10. Implementation Notes

Non-trivial business logic, algorithms, external API interactions, and edge cases:

```markdown
## Slug Generation
Input: post title string
Process: lowercase → replace whitespace with hyphens → strip non-alphanumeric except hyphens → collapse consecutive hyphens → trim hyphens from ends
Collision: query DB for existing slugs with same base, append incrementing suffix (-2, -3)
Edge case: empty title after stripping → use "untitled"

## Email Ingestion
Webhook: Resend sends POST to /api/inbound with parsed email JSON
Auth: Verify webhook signature using RESEND_WEBHOOK_SECRET
Sender matching: Look up user by sender email address. No match → reject silently.
Content parsing: Use email HTML body. Strip unsafe tags (script, style, iframe). Extract <img> src, re-upload to R2, replace URLs.
```

### 11. Environment Variables

Every variable with description and example:

```bash
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/appname
BETTER_AUTH_SECRET=     # openssl rand -hex 32
BETTER_AUTH_URL=http://localhost:3000
RESEND_API_KEY=         # From resend.com dashboard
R2_ACCOUNT_ID=          # Cloudflare account ID
R2_ACCESS_KEY_ID=       # R2 API token
R2_SECRET_ACCESS_KEY=   # R2 API token secret
R2_BUCKET_NAME=uploads
R2_PUBLIC_URL=          # Public bucket URL for serving media
```

### 12. Getting Started

Exact commands to go from zero to running app:

```bash
npm install
cp .env.example .env
# Fill in .env values

npx drizzle-kit push
npx tsx src/db/seed.ts   # if seed data exists

npm run dev
# Open http://localhost:3000
```

## Rules

- **No questions.** Decide everything autonomously.
- **No alternatives.** "Use PostgreSQL" not "PostgreSQL or MySQL."
- **No TBD.** Every section is complete. Nothing deferred to implementation.
- **No vague descriptions.** Every UI element has a location, label, and behavior.
- **Schema-complete.** Every table, every column, every constraint, every index.
- **API-complete.** Every endpoint with method, path, auth, typed request/response, behavior.
- **UI-complete.** Every page with layout, components, and all four states (loading, empty, error, success).
- **Runnable.** Getting Started must produce a working dev server.
- **Grounded.** Infer features the product must have had, but don't invent features the report doesn't support.
- **Comprehensive.** Spec every feature the product was known for. List only truly out-of-scope features under "Future Scope."
