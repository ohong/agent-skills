---
name: spring-cleaning
description: >
  Mac disk space cleanup skill. Trigger this skill whenever the user mentions
  running low on disk space, wanting to free up space on their Mac, doing
  "spring cleaning", or any similar context (e.g. "I'm almost out of space",
  "my Mac is full", "let's do a storage cleanup", "help me free up disk space").
  This skill generates a prioritized, step-by-step runbook with exact terminal
  commands tailored to the user's actual storage report. Use it proactively even
  if the user just pastes a storage screenshot without explicitly asking — the
  intent is clear.
---

# Spring Cleaning — Mac Disk Space Cleanup

A skill for generating a safe, prioritized, step-by-step runbook to free up
local disk space on a Mac. Before recommending offloading or deletion, confirm
the user's backup, cloud-sync, and external-storage setup. Useful optional tools
include DaisyDisk, `ncdu`, `dust`, `fdupes`, and `brew`.

---

## Step 1 — Get a Storage Snapshot

Before generating the runbook, the agent needs a storage report. Accept any of the
following (in order of detail/usefulness):

| Report Type | How to Get It | Detail Level |
|---|---|---|
| `dust` output | `dust -d 4 /Users/<name> 2>/dev/null` | ✅ Good |
| DaisyDisk screenshot | Scan Macintosh HD, share screenshot | ✅ Good |
| `ncdu` filtered output | See command below | ✅✅ Best |
| System Settings > Storage screenshot | Built-in macOS storage view | ⚠️ Low (ask for more) |

**ncdu filtered command (recommend this if user hasn't run anything yet):**
```bash
ncdu / -o /tmp/ncdu_out.json 2>/dev/null && python3 << 'EOF'
import json
with open('/tmp/ncdu_out.json') as f:
    data = json.load(f)
def walk(node, path='', threshold=200*1024*1024):
    if isinstance(node, list):
        info = node[0]
        name = info.get('name', '')
        full = f"{path}/{name}".replace('//', '/')
        size = info.get('asize', 0)
        if size > threshold:
            print(f"{size // 1024 // 1024}MB\t{full}")
        for child in node[1:]:
            walk(child, full, threshold)
    elif isinstance(node, dict):
        name = node.get('name', '')
        full = f"{path}/{name}".replace('//', '/')
        size = node.get('asize', 0)
        if size > threshold:
            print(f"{size // 1024 // 1024}MB\t{full}")
root = data[2]
walk(root, threshold=200*1024*1024)
EOF
```

**If the user only provides a high-level screenshot** (e.g. macOS Storage view
showing category totals), ask for a DaisyDisk scan or `dust` output before
generating the runbook — the category-level view isn't granular enough to write
safe, targeted commands.

**If the user provides DaisyDisk screenshots of subcategories** (e.g. drilling
into Caches, Messages, Library), accept those as supplementary detail.

---

## Step 2 — Analyse the Report

Before writing the runbook, mentally categorise every large item into one of:

- 🔴 **Delete now** — safe to remove, will auto-regenerate (caches, build
  artifacts, old backups)
- 🟠 **Delete with caution** — safe but won't regenerate (old projects, iOS
  backups, duplicate folders)
- 🟡 **Offload to external SSD** — needed occasionally but not daily
- 🟢 **Leave alone** — system files, active app data, iCloud sync metadata

Key things to identify in the report:
- **Trash** — often huge and forgotten; always check first
- **node_modules** — scattered across dev projects, safe to delete and reinstall
- **iOS backups** — `~/Library/Application Support/MobileSync/Backup`
- **Photos Library** — can be moved to external SSD
- **VM bundles** — Claude Code, Docker, UTM, Parallels image files
- **App caches** — Arc, Notion, Chrome, Electron apps balloon over time
- **.bun, .codex, .lmstudio** — large hidden dotfolders
- **Duplicate iCloud folders** — "Documents - MacBook Pro 2" patterns
- **Old git worktrees** — `~/.codex/worktrees`, `~/dev/` archived projects
- **Homebrew / pip / npm cache** — safe to purge fully

---

## Step 3 — Generate the Runbook

Output the runbook in-chat as structured markdown (no file download unless the
user asks). Follow this structure:

### Runbook structure

```
## 🧹 Mac Spring Cleaning Runbook
### Overview
[1-2 sentence summary of current state and total estimated recovery]

> ⚠️ BEFORE YOU START: Make sure you have a recent backup (Time Machine or
> otherwise) before running any delete commands. Steps marked 🔴 are
> irreversible once Trash is emptied.

---

### Quick Wins (< 5 min, highest leverage)
[Steps ordered by GB recovered, largest first]

---

### Medium Effort
[Steps requiring more care — duplicate cleanup, project archival]

---

### Offload to External SSD
[Files/folders to move rather than delete]

---

### Optional / Advanced
[Docker pruning, symlink tricks, cron jobs for recurring maintenance]
```

### Per-step format

Each step should include:
- **What it is** — one sentence explaining what this file/folder is
- **Why it's safe** — brief justification for why deleting/moving is safe
- **Estimated space** — grounded in the report the user provided
- **Command(s)** — exact, copy-pasteable terminal commands
- **Verification** — how to confirm it worked (optional but helpful for big steps)

**Example step:**
```
#### 1. Empty Trash — ~23 GB
Your Trash contains a deleted Photos Library. This is the single biggest
win and takes 5 seconds.
**Safe because:** Items in Trash are already marked for deletion.
```bash
rm -rf ~/.Trash/*
```
Or: right-click the Trash icon in your Dock → Empty Bin.
```

---

## Runbook Content Reference

These are the categories to cover, with commands. Include only what's relevant
to the user's actual report — don't pad the runbook with steps that don't apply.

### 🗑️ Trash
```bash
rm -rf ~/.Trash/*
```

### 📱 iOS Backups (~10–30 GB typical)
```bash
# View what's there
du -sh ~/Library/Application\ Support/MobileSync/Backup/*

# Delete all local iOS backups
rm -rf ~/Library/Application\ Support/MobileSync/Backup/*
```
After deleting: make sure iPhone backs up to iCloud instead.
(iPhone Settings → [Your Name] → iCloud → iCloud Backup → On)

### 🖼️ Photos Library → External SSD
1. Quit Photos
2. In Finder, drag `~/Pictures/Photos Library.photoslibrary` to the external SSD
3. Hold `⌘` while opening Photos to choose the new library location
4. In Photos: Settings → General → "Use as System Photo Library"

### 💬 Messages Attachments (~1–5 GB typical)
Enable iCloud Messages first (Messages → Settings → iMessage tab → Enable
Messages in iCloud), then:
```bash
rm -rf ~/Library/Messages/Attachments/*
```

### 📦 node_modules (scattered, often 5–15 GB total)
```bash
# Interactive cleanup across all projects
npx npkill
# Arrow keys to navigate, space to delete
```

### 🍺 Homebrew cache
```bash
brew cleanup --prune=all
```

### 🐍 pip cache
```bash
pip cache purge --break-system-packages
```

### 📦 npm cache
```bash
npm cache clean --force
```

### 🐇 Bun cache
```bash
rm -rf ~/.bun/install/cache
```

### 🤖 Claude Code VM bundle (~9 GB)
Only delete if not actively using Claude Code computer-use features:
```bash
rm -rf ~/Library/Application\ Support/Claude/vm_bundles
```
Regenerates automatically if needed.

### 🐳 Docker
```bash
# Remove stopped containers, unused images, dangling volumes
docker system prune -a --volumes
```
⚠️ This removes all images not tied to a running container. Re-pull as needed.

### 🌿 Git worktrees / Codex worktrees
```bash
# Codex CLI worktrees
rm -rf ~/.codex/worktrees

# List and prune stale git worktrees in a repo
git worktree list
git worktree prune
```

### 🧠 LM Studio models → External SSD
```bash
mv ~/.lmstudio /Volumes/YourSSD/.lmstudio
ln -s /Volumes/YourSSD/.lmstudio ~/.lmstudio
```

### 🗂️ App Caches (safe to delete — all rebuild automatically)
```bash
rm -rf ~/Library/Caches/Arc
rm -rf ~/Library/Caches/Google
rm -rf ~/Library/Caches/ms-playwright   # only if not actively using Playwright
rm -rf ~/Library/Caches/notion.id.ShipIt
rm -rf ~/Library/Caches/notionmail-updater
rm -rf ~/Library/Caches/@lineardesktop-updater
rm -rf ~/Library/Caches/superhuman-updater
rm -rf ~/Library/Caches/node-gyp
```

### 📓 Notion Service Worker cache (~2–4 GB, regrows over time)
```bash
rm -rf ~/Library/Application\ Support/Notion/Partitions/notion/Service\ Worker/CacheStorage
```

### 🗄️ Duplicate iCloud folders ("X 2" pattern)
When iCloud sync conflicts create duplicate folders:
```bash
# Install fdupes
brew install fdupes

# Compare a pair to find true duplicates
fdupes -r ~/Documents/"Folder Name" ~/Documents/"Folder Name 2"

# Check sizes before deciding
du -sh ~/Documents/"Folder Name"
du -sh ~/Documents/"Folder Name 2"
```
Only delete the "2" folder after confirming it contains no unique files.
Fix any underlying iCloud sync error first (`killall bird` or re-sign into iCloud).

### 🗃️ Dev project archive → External SSD
For projects not touched in 3+ months:
```bash
# Move to external SSD
mv ~/dev/old-project /Volumes/YourSSD/archive/

# Optional: keep a symlink so old paths still resolve
ln -s /Volumes/YourSSD/archive/old-project ~/dev/old-project
```

### 📥 Downloads folder
```bash
# See what's big
dust -d 2 ~/Downloads

# Open interactively to review before deleting
open ~/Downloads
```
Don't bulk-delete — review first. Move anything worth keeping to archive on SSD.

---

## Tone & Style Notes

- Lead with the summary table showing total estimated recovery upfront — users
  want to know the payoff before they commit to the steps
- Be specific about GB estimates — ground them in the actual report, don't
  use vague language like "could save significant space"
- Keep warnings tight — one callout at the top about backups is enough, don't
  repeat safety warnings on every step
- Don't include steps that don't apply to this user's report — a lean runbook
  gets followed; a padded one gets ignored
- If the user says they've already done a step (e.g. "I already cleared the
  Trash"), skip it without comment and move on
