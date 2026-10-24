# Git command reference

Start with the [full tutorial](README.md) for setup and a complete exercise.

Examples use Git 2.23 or later. Replace placeholders before running commands.
Commands with a file path affect that file; branch operations affect the current
branch unless stated otherwise.

## Core concepts

- A commit records a snapshot, metadata, and parent links. Diffs compare snapshots.
- A branch is a movable reference to a commit; history is a graph.
- HEAD normally refers to the current branch, or directly to a detached commit.
- The working tree contains checked-out files. The index holds staged content.
- A GitHub Fork is a separate hosted repository. A branch is a reference within
  a repository; it is not a GitHub Fork.
- Clone gets a local copy; commit saves locally; push sends commits to a remote.
  A pull request proposes integrating changes on GitHub.

## Inspect your work

| Goal | Command |
| --- | --- |
| Show staged, modified, and untracked files | `git status` |
| Show unstaged tracked changes | `git diff` |
| Show staged changes | `git diff --cached` |
| Show recent history | `git log --oneline --graph --all` |
| Show commits affecting a file | `git log main -- practice-note.txt` |
| Show configured remote URLs | `git remote -v` |
| Show the latest commit | `git log -1 --oneline` |

Untracked file contents do not appear in ordinary `git diff`. Open the file
directly, then stage it and review `git diff --cached`.

## Stage and commit

| Goal | Command |
| --- | --- |
| Stage one file's current contents | `git add practice-note.txt` |
| Unstage it while preserving working files | `git restore --staged -- practice-note.txt` |
| Commit staged changes | `git commit -m "docs: add first practice note"` |
| Include tracked modifications and deletions automatically | `git commit -a -m "docs: update practice note"` |
| Set this repository's public author name | `git config user.name "YOUR-PUBLIC-NAME"` |
| Set this repository's commit email | `git config user.email "YOUR-GITHUB-COMMIT-EMAIL"` |

The `-a` flag does not include untracked files. A .gitignore rule does not stop
tracking files already in Git. Commit identity is public metadata, not sign-in.

## Branches

| Goal | Command |
| --- | --- |
| Create and switch to a branch at HEAD | `git switch -c docs/first-note` |
| Switch to an existing local branch | `git switch main` |
| Create a local branch tracking a fetched remote branch | `git switch --track origin/docs/first-note` |
| Show local branches | `git branch` |
| Show remote-tracking branches | `git branch -r` |
| Show both | `git branch -a` |
| Delete a local branch with Git's merge-safety check | `git branch -d docs/first-note` |
| Inspect an old commit without moving a branch | `git switch --detach COMMIT` |
| Keep work made at a detached commit | `git switch -c keep-work` |

Switching can carry compatible local edits, but Git refuses when they would be
overwritten. Commit or stash before a switch if unsure. A branch may not pass
the deletion check after a squash/rebase merge; inspect before forcing deletion.

## Remotes and collaboration

| Goal | Command |
| --- | --- |
| Clone your practice repository | `git clone https://github.com/YOUR-USERNAME/git-practice.git` |
| Discover remote commits without integrating them | `git fetch origin` |
| Also remove stale remote-tracking references | `git fetch --prune origin` |
| First push, setting the feature branch's upstream | `git push -u origin docs/first-note` |
| Push the current branch once its upstream is configured | `git push` |
| Fetch main and integrate it into the current branch only if fast-forward is possible | `git pull --ff-only origin main` |
| Integrate a local feature branch into the current branch | `git merge docs/first-note` |
| Fetch and integrate a remote-tracking feature branch into the current branch | Run `git fetch origin`, then `git merge origin/docs/first-note` |
| Delete a remote feature branch after checking it is no longer needed | `git push origin --delete docs/first-note` |

Fetch does not update ordinary local branches. Prune does not delete them.
Pull updates the **current branch**, so switch to main first if that is the
branch you intend to update. A plain pull may merge or rebase depending on
configuration and options; no extra checkout of HEAD is needed.

A local branch such as `docs/first-note` is separate from the remote-tracking
reference `origin/docs/first-note`. Fetch updates the latter, not the former.

Before merging a feature branch, switch to the intended base and check
`git status`. A merge may fast-forward or create a merge commit.
Pushes require authentication, write access, and compliance with branch rules.
See [sign-in setup](README.md#authentication) and
[the Fork workflow](README.md#fork-workflow) if you do not have write access.

## Conflicts and unfinished work

When a merge stops on a conflict:

1. Run `git status` and inspect the affected files.
2. Resolve the content and remove conflict markers.
3. Stage each resolved file, such as `git add practice-note.txt`.
4. Run `git merge --continue`, or `git merge --abort` to abandon the merge.

During a rebase, use `git rebase --continue` or `git rebase --abort` instead.
Overlapping edits may conflict, but a conflict is not inevitable.

To move unfinished work to a different existing branch:

```bash
git stash push -u -m "unfinished practice note"
git switch existing-branch
git stash pop
```

Replace existing-branch with a branch that exists. The -u flag includes
untracked files, not ignored files. Applying a stash can conflict; if pop
fails, its stash entry remains available.

## Restore and undo: read before running

| Goal | Command and consequence |
| --- | --- |
| Discard unstaged edits to one tracked file | `git restore -- practice-note.txt` restores from the index; staged content remains |
| Restore both staged and working versions of a file from HEAD | `git restore --source=HEAD --staged --worktree -- practice-note.txt` discards both sets of edits to that file |
| Restore a file's working version from an older commit | `git restore --source=COMMIT -- practice-note.txt` changes the working file, not HEAD or the index |
| Reverse an ordinary published commit with a new commit | `git revert COMMIT` can conflict; merge commits need additional choices |
| Move the current branch and index to an earlier commit, retaining working files | `git reset COMMIT` unstages changes; some files may become untracked |
| Move the branch, index, and working tree to an earlier commit | `git reset --hard COMMIT` discards tracked uncommitted changes and may overwrite untracked files in the way |
| Force-delete an unchecked local branch | `git branch -D BRANCH` removes its reference without verifying it is merged |

Back up work before destructive commands. Old commits may be recoverable
through reflog until pruned; uncommitted edits generally are not. Prefer revert
for ordinary commits already shared with others. Do not force push as a routine
response to a rejected push.

## Older checkout equivalents

Use switch and restore above to keep branch switching separate from restoring
files. Older tutorials may use:

| Older command | Meaning |
| --- | --- |
| `git checkout -b BRANCH` | Create and switch to a branch |
| `git checkout BRANCH` | Switch to an existing branch |
| `git checkout COMMIT` | Inspect a commit with detached HEAD |
| `git checkout COMMIT -- FILE` | Replace both the index and working file from a commit |

## Official references

- [Pro Git](https://git-scm.com/book/en/v2)
- [git switch](https://git-scm.com/docs/git-switch)
- [git restore](https://git-scm.com/docs/git-restore)
- [git fetch](https://git-scm.com/docs/git-fetch)
- [git pull](https://git-scm.com/docs/git-pull)
- [git reset](https://git-scm.com/docs/git-reset)
- [git revert](https://git-scm.com/docs/git-revert)
- [git merge](https://git-scm.com/docs/git-merge)

