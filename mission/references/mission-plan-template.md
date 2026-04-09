# Mission Plan Template

Use this template when creating `.mission/plan.md`. Fill in every section. Leave nothing as TBD.

---

```markdown
# Mission: {title}

> {One-sentence description of the end state. What exists when this mission is done?}

## Context

- **Codebase**: {framework, language, key patterns observed}
- **Build command**: `{exact command}`
- **Test command**: `{exact command}`
- **Lint command**: `{exact command}`
- **Type-check command**: `{exact command}` (if applicable)

## Scope

**In scope:**
- {feature/change 1}
- {feature/change 2}
- ...

**Out of scope:**
- {explicitly excluded item 1}
- {explicitly excluded item 2}

## Milestones

### Milestone 1: {title}
**Size:** {S / M / L}
**Goal:** {What exists after this milestone that didn't before?}
**Files to touch:**
- `{path/to/file1}` — {what changes}
- `{path/to/file2}` — {what changes}

**Steps:**
1. {concrete step}
2. {concrete step}
3. {concrete step}

**Acceptance criteria:**
- [ ] `{verification command 1}` passes
- [ ] `{verification command 2}` passes
- [ ] {manual check if needed}

---

### Milestone 2: {title}
**Size:** {S / M / L}
**Depends on:** Milestone 1
**Goal:** {What exists after this milestone?}
**Files to touch:**
- `{path/to/file}` — {what changes}

**Steps:**
1. {concrete step}
2. {concrete step}

**Acceptance criteria:**
- [ ] `{verification command}` passes
- [ ] {specific behavior verified}

---

{Repeat for milestones 3-7}

---

### Final Milestone: Integration & Verification
**Size:** {S / M}
**Depends on:** All previous milestones
**Goal:** Everything works together end-to-end.

**Acceptance criteria:**
- [ ] Full test suite passes: `{test command}`
- [ ] Build succeeds: `{build command}`
- [ ] Lint clean: `{lint command}`
- [ ] Type-check clean: `{typecheck command}`
- [ ] {End-to-end behavior verified}

## Risk Register

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| {risk 1} | {low/med/high} | {what to do if it happens} |
| {risk 2} | {low/med/high} | {what to do if it happens} |

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| {e.g., "Use Drizzle over Prisma"} | {why} |
| {e.g., "REST over GraphQL"} | {why} |
```

---

## Template Rules

1. **Every milestone must have at least one runnable acceptance criterion.** A command that exits 0 on success.
2. **"Files to touch" must be specific paths**, not categories like "the API files."
3. **Steps must be concrete actions**, not vague descriptions. "Add a `users` table with columns id, email, name" not "set up the database."
4. **Size estimates are honest.** If you're unsure, size up. An M that takes L-time derails the schedule.
5. **The final milestone is always integration.** It runs ALL verification commands across the entire mission's work.
6. **Decisions are documented with rationale.** When you pick a library, pattern, or approach, say why. This helps if the user wants to change direction.
7. **The risk register is not optional.** Even a simple mission has risks (e.g., "external API might have rate limits"). Identifying them upfront prevents surprise escalations.
