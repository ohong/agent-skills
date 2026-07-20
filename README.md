# ohong-skills

Reusable Claude Code plugins and Codex skills that add scripts, external retrieval, or durable specialist workflows.

## Claude Code

Add the marketplace, then install the plugins you want:

```text
/plugin marketplace add ohong/agent-skills
/plugin install save2md@ohong-skills
```

## Marketplace plugins

| Plugin | Description |
|---|---|
| [audit-and-improve](audit-and-improve/) | Audits a repository and produces a prioritized improvement plan. |
| [capture-design](capture-design/) | Saves reference visuals as a reusable design-system swipefile. |
| [distill-taste](distill-taste/) | Distills a person's publicly shared taste into an ask-* advisor skill. |
| [fast-wifi](fast-wifi/) | Diagnoses macOS Wi-Fi and internet problems with measured checks. |
| [mission](mission/) | Runs file-backed milestone planning and execution for long-horizon work. |
| [name-it](name-it/) | Runs a structured brand or product naming and validation process. |
| [post-walk](post-walk/) | Turns an Apple Voice Memo into project notes, tasks, todos, and drafts. |
| [save2md](save2md/) | Saves articles, X posts, and YouTube transcripts as local Markdown. |
| [search-x](search-x/) | Finds a remembered X post from fuzzy clues and verifies it live. |

## Standalone skills

| Skill | Description |
|---|---|
| [delegate](delegate/) | Delegates substantial work through a structured multi-agent implementation and review loop. |
| [explain](explain/) | Produces teaching-oriented explanations of code and changes. |
| [press-release-faq](press-release-faq/) | Writes an Amazon-style Working Backwards PR/FAQ grounded in the current project. |
| [spring-cleaning](spring-cleaning/) | Produces a measured, prioritized runbook for safely freeing disk space on a Mac. |
| [vibe-security-audit](vibe-security-audit/) | Audits application security risks across authentication, data, and deployment boundaries. |

## Codex

Each standalone plugin keeps its canonical skill under `skills/<name>/`. Copy or symlink that folder into a Codex skill directory:

```bash
mkdir -p ~/.agents/skills
ln -s /path/to/agent-skills/save2md/skills/save2md ~/.agents/skills/save2md
```

Restart Claude Code or Codex, or start a fresh task, after installing or updating skills.
