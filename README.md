# Git & GitHub Primer

Learn Git through one small change: create a branch, edit one file, commit,
push, and open a pull request.

## Contents

- [Choose your starting point](#choose-your-starting-point)
- [Before you begin](#prerequisites)
- [Git basics](#git-basics)
- [Sign in for HTTPS pushes](#authentication)
- [Complete practice](#practice)
  - [1. Create and clone your practice repository](#1-create-and-clone-your-practice-repository)
  - [2. Set your commit identity](#2-set-your-commit-identity)
  - [3. Create a branch before changing files](#3-create-a-branch-before-changing-files)
  - [4. Create and review one file](#4-create-and-review-one-file)
  - [5. Commit and push the same branch](#5-commit-and-push-the-same-branch)
  - [6. Open and review a pull request](#6-open-and-review-a-pull-request)
  - [7. Update locally and clean up](#7-update-locally-and-clean-up)
- [Fork workflow](#fork-workflow)
- [Team workflow](#team-workflow)
- [Branches and merging](#branches-merging)
  - [Resolve a merge conflict](#resolve-a-merge-conflict)
  - [Move unfinished work to a new branch](#move-unfinished-work-to-a-new-branch)
- [Common problems](#troubleshooting)
- [Documentation checks](#documentation-checks)
- [References](#references)

## Choose your starting point

| Your goal | Start here |
| --- | --- |
| Learn Git for the first time | [Git basics](#git-basics), then [complete practice](#practice) |
| Contribute without write access | [Fork workflow](#fork-workflow) |
| Collaborate in a shared repository | [Team workflow](#team-workflow) |
| Look up a command | [Command reference](gitprimer.md) |
| Fix a problem | [Common problems](#troubleshooting) |

This guide is for beginners and occasional contributors. Read the practice in
order, then use the command reference as a reminder. Advanced history rewriting,
deployment, and GitHub Actions programming are outside this tutorial's scope.

<a name="prerequisites"></a>

## Before you begin

* Install [Git](https://git-scm.com/downloads) and confirm `git --version` works.
  The `switch` and `restore` commands require Git 2.23 or later.
* Use Git Bash on Windows, or a shell such as Bash on macOS or Linux.
  Shell commands such as `printf` below are written for those environments,
  rather than PowerShell or Command Prompt.
* Create a GitHub account. For this exercise, create your own repository.
* Copy commands only, not output. Text such as `YOUR-USERNAME` is a placeholder:
  replace it before running the command.
* Git commit names and email addresses become part of commit history. Configure
  the identity you want to publish. A GitHub username alone does not authenticate Git.

## Git basics

Git records version history on your computer. GitHub hosts repositories and
provides collaboration features such as issues and pull requests.

* A *commit* records a snapshot, author information, a message, and parent links.
  Comparing snapshots shows the differences between versions.
* The *working tree* is your checked-out files.
* The *staging area* (index) holds the content intended for the next commit.
  Editing a file again after staging does not update its staged content.
* A *branch* is a movable reference to a commit. Histories can merge, so the
  history is a graph rather than a separate linear chain for every branch.
* `HEAD` normally refers to the current branch. In detached HEAD mode, it refers
  directly to a commit.
* A *remote* is a named repository URL, such as `origin`.
* A GitHub *Fork* is a separate repository under another owner. Creating a Git
  branch does not create a GitHub Fork.
* *Clone* copies a repository locally; *commit* records a local snapshot;
  *push* sends commits to a remote; a *pull request* proposes integration on GitHub.

A normal clone has repository history, but shallow or partial clones can omit
history or objects. You can commit locally without an internet connection.

<a name="authentication"></a>

## Sign in for HTTPS pushes

Public repositories can normally be cloned without signing in. Pushing requires
authentication and permission to write to the destination.

Use Git Credential Manager's browser sign-in when prompted. Alternatively,
install [GitHub CLI](https://cli.github.com/) and run:

```bash
gh auth login
```

Select GitHub.com, HTTPS, and browser authentication. If asked whether to
authenticate Git with your GitHub credentials, answer yes. GitHub account
passwords are not accepted as passwords for Git HTTPS operations. Do not put
tokens in clone URLs, commands saved in documentation, or committed files.

See [GitHub's credential setup guide](https://docs.github.com/en/get-started/git-basics/caching-your-github-credentials-in-git).
For a private repository, authenticate before cloning.

<a name="practice"></a>

## Complete practice: one file, one branch, one pull request

This example consistently uses the repository `git-practice`, branch
`docs/first-note`, and file `practice-note.txt`. Use a disposable repository,
not a production project.

### 1. Create and clone your practice repository

On GitHub, create a repository named `git-practice` in your account and select
the option to add a README. This gives the repository an initial commit.
The example assumes the default branch is `main`; substitute your actual
default branch if different.

```bash
git clone https://github.com/YOUR-USERNAME/git-practice.git
cd git-practice
git status
git remote -v
```

`origin` should point to your own repository. If you cloned someone else's
repository and cannot push, use the [Fork workflow](#fork-workflow) instead.

### 2. Set your commit identity

```bash
git config user.name "YOUR-PUBLIC-NAME"
git config user.email "YOUR-GITHUB-COMMIT-EMAIL"
```

These settings apply to this repository only. Replace both values before
committing. For email privacy, copy your exact GitHub-provided no-reply address
from your [GitHub email settings](https://github.com/settings/emails).
Do not assume everyone has the same no-reply address format.

### 3. Create a branch before changing files

```bash
git switch main
git pull --ff-only origin main
git switch -c docs/first-note
```

`--ff-only` updates only when a fast-forward is possible. If it refuses,
inspect your branch history instead of forcing an update.

The branch now points to the same commit as `main`. Creating a branch makes a
separate line of work possible; reviews and checks help keep the main branch
stable.

### 4. Create and review one file

```bash
printf 'My first Git practice note.\n' > practice-note.txt
git status --short
```

Before staging, the new file should appear as `?? practice-note.txt`.
`git diff` does not display the contents of an untracked file. Open it in
your editor, then stage exactly that file:

```bash
git add practice-note.txt
git diff --cached -- practice-note.txt
git status --short
```

The status should now show `A  practice-note.txt`. Review the staged diff
before committing. `git add` stages eligible changes and respects ignore
rules for untracked files. Git does not track empty directories.

A `.gitignore` entry such as `node_modules/` prevents ordinary additions of
matching untracked files. It does not stop tracking files already committed.

### 5. Commit and push the same branch

```bash
git commit -m "docs: add first practice note"
git log -1 --oneline
git push -u origin docs/first-note
```

The commit records only the staged file. The push creates or updates
`origin/docs/first-note` and sets it as the branch's upstream.
Later pushes from this branch can use `git push`.

`git commit -a` automatically stages modifications and deletions of tracked
files, alongside existing staged changes. It does not add untracked files.

### 6. Open and review a pull request

On your GitHub repository, use *Compare & pull request*, or open *Pull requests*
and choose *New pull request*.

* Base repository: your `git-practice` repository.
* Base branch: `main`.
* Compare branch: `docs/first-note`.

Describe the change, review *Files changed*, and create the pull request.
A commit or push does not automatically submit a pull request.
Ask a collaborator to review it when working with a team. For this disposable
exercise, inspect and merge your own pull request if repository rules allow it.

GitHub may offer merge, squash, or rebase options depending on repository
settings. In the simple exercise, use the available permitted method and
check that `practice-note.txt` appears on `main`.

### 7. Update locally and clean up

After the pull request has been merged on GitHub:

```bash
git switch main
git pull --ff-only origin main
git fetch --prune origin
git branch -d docs/first-note
```

You may also use GitHub's *Delete branch* button to remove the remote feature
branch. Pruning removes stale remote-tracking references, not ordinary local
branches.

If `git branch -d` refuses after a squash or rebase merge, verify that the
intended changes are present on `main`. You can leave the local branch in place.
Do not force-delete it without checking for work you still need.

<a name="fork-workflow"></a>

## Fork workflow: contribute without write access

1. On the source repository, choose *Fork* and create the copy in your account.
1. Clone your Fork. `origin` should point to your account.
1. Configure your identity as above and create a feature branch.
1. Make, review, stage, commit, and push changes to your Fork.
1. Open a pull request with the *original repository* as base and your Fork's
   feature branch as head. Its maintainers decide whether to merge it.

To keep track of the original repository, add a second remote. Replace the
example URL with the original project's actual URL:

```bash
git remote add upstream https://github.com/UPSTREAM-OWNER/PROJECT.git
git remote -v
git fetch upstream
```

To update an unchanged local default branch, assuming it is named `main`:

```bash
git switch main
git merge --ff-only upstream/main
git push origin main
```

Commit or stash unfinished changes first. If your Fork's `main` has diverged
from upstream, this fast-forward-only command stops; inspect the differences
and choose a merge or rebase intentionally. Do not use force push as a default fix.
Synchronizing your Fork does not modify the original repository.

<a name="team-workflow"></a>

## Team workflow: collaborate with write access

Clone the shared repository, create your own feature branch, and push it to
that shared repository. The pull request's base and head repositories are the
same, unlike the Fork workflow. Branch protection may require reviews or checks
before merging.

An issue can describe a bug, feature, or task. Use *Labels* to categorize it,
and assign it to yourself if repository permissions allow. You do not need
an issue for every change unless the project's contribution rules require one.

Use a descriptive branch such as `docs/first-note` or `fix/login-error`.
After pushing, open a pull request, address review feedback with more commits,
and merge only after the required checks and approvals.

<a name="branches-merging"></a>

## Branches and merging

A fast-forward moves the current branch reference to a descendant commit,
without adding a merge commit. When both branches have their own commits,
an ordinary successful merge creates a commit with multiple parents.

```text
Before:
A---B---C  main
     \
      D    docs/first-note

After merging the feature branch into main:
A---B---C---M  main
     \     /
      D---+
      ^
      docs/first-note (still points to D)
```

After the merge, `main` points to `M`; `docs/first-note` still points to `D`.
This example shows a merge commit. GitHub squash and rebase merges produce
different histories.

### Resolve a merge conflict

Incompatible edits to the same text region may cause a conflict; not every
overlapping change conflicts. Files can also conflict through deletion or
renaming. Git reports conflicts; it does not always launch an editor.

For an ordinary text conflict, edit the file and remove the markers after
deciding what the combined content should be:

```text
<<<<<<< HEAD
My current branch's text
=======
The incoming branch's text
>>>>>>> other-branch
```

Then stage each resolved file and complete the merge:

```bash
git add practice-note.txt
git merge --continue
```

Use `git status` to see what remains unresolved. To abandon the merge,
use `git merge --abort`. Start merges with a clean working tree, since aborting
may not recover unrelated uncommitted changes perfectly.

A rebase is different: after resolving and staging a file, use
`git rebase --continue`, or `git rebase --abort` to abandon it.
During a rebase, do not assume the meaning of "ours" and "theirs" matches an
ordinary merge.

### Move unfinished work to a new branch

If you started editing on the wrong branch, first inspect `git status`.
For a new branch starting at the current commit, your edits can usually stay
in place while you run `git switch -c new-branch`.

To set work aside before switching to a different existing branch:

```bash
git stash push -u -m "unfinished practice note"
git switch existing-branch
git stash pop
```

Replace `existing-branch` with a branch that actually exists.
`-u` includes untracked files, but not ignored files. Applying the stash can
conflict; Git retains the stash entry if `pop` fails.

<a name="troubleshooting"></a>

## Common problems

| Symptom | What to check |
| --- | --- |
| Authentication failed | Use browser sign-in through a credential manager or GitHub CLI. A GitHub account password is not a Git HTTPS password. |
| Permission denied or HTTP 403 on push | Check `git remote -v`, the signed-in account, and repository permissions. Push to your Fork if you lack write access. Repository rules may restrict direct pushes. |
| Non-fast-forward rejection | Fetch and inspect `git log --oneline --graph --all`. Integrate the remote work with an intentional merge or rebase before retrying; do not blindly force push. |
| Current branch has no upstream | For this exercise, use `git push -u origin docs/first-note` from the feature branch. |
| Nothing to commit | Run `git status`. Check whether the file was saved and staged, or ignored. |
| Branch switch would overwrite changes | Commit or stash the work first. Do not discard it just to make the command succeed. |
| Pull with --ff-only refuses | Local and remote histories have diverged. Inspect the commits and choose how to integrate them. |
| Detached HEAD | You checked out a commit instead of a branch. Use `git switch -c keep-work` to retain any work before leaving that position. |

## Documentation checks

GitHub Actions discovers all tracked Markdown files on pushes and pull requests.
It checks local links and section anchors, image paths and alternative text,
table column counts, fenced code blocks, and source formatting. It also renders
each document to HTML with a Markdown parser and checks the rendered links and
headings. This validates document structure; it is not a browser screenshot or
a guarantee of identical styling on GitHub.

The rendered HTML files are available in the run's **rendered-docs** artifact
for visual inspection. Authentication-only links are explicitly excluded in
[the checker](scripts/check_docs.py). HTTP failures such as rate limits and
temporary server errors are reported as **unverified**, separately from broken
links, in the Actions summary.

To run the same checks locally, install Python 3.12 or later and the pinned
documentation dependencies:

```bash
python -m pip install -r requirements-docs.txt
python -m unittest discover -s tests
python scripts/check_docs.py --render-dir work/rendered-docs
```

Add `--external` to check public HTTP links as well.

## References

* [Pro Git](https://git-scm.com/book/en/v2)
* [git pull](https://git-scm.com/docs/git-pull)
* [git fetch](https://git-scm.com/docs/git-fetch)
* [git commit](https://git-scm.com/docs/git-commit)
* [git switch](https://git-scm.com/docs/git-switch)
* [git restore](https://git-scm.com/docs/git-restore)
* [git merge](https://git-scm.com/docs/git-merge)
* [git stash](https://git-scm.com/docs/git-stash)

