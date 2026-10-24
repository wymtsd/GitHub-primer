# Git - Quick Primer

A fast-paced introduction to version control and git.
If you want the full blown experience, see the git scm book: https://git-scm.com/book/en/v2

## What is version control
Version control is maintaining a detailed report of changes that happen to your codebase.
Good version control practice allows you to roll back mistakes, work on features in parallel, and combine them into a final product.

## How does Git record history?

* A Git **repository** stores objects (including commits), references (including branches and tags), and configuration.
* A **branch** is a movable reference to a commit. Commits form a directed history graph through their parent links, rather than a separate linear history for each branch.
* A **commit** records a snapshot, metadata, and parent links. Comparing snapshots shows *what changed*; an initial commit has no parent, and a merge commit can have multiple parents.
* Each **commit** has a unique hash that identifies it among all other commits.
* Changes are usually introducing or removing lines from a file, deleting a file, or renaming a file.

## How do I see the history?
Use `git log <branch> -- <files>` to see a list of commits on `branch` that edited `files` (or any files, if absent).

## The git workflow

1. Working set
   * The *working set* is the state of the files as they are on your machine, right now.
   * When you make changes with `vi` or `emacs`, you edit the working set, making those files *modified*
2. Staging area
   * The *staging area* (also called the index) is for files that you have finished editing and want to commit the next time `git commit` is run
   * A file can be both *staged* and *modified* if you change it after staging. Simply stage it again to update the staging area.
3. Committed files
   * Within `.git` directory, git holds data structures that describe what it currently believes the file should look like
   * You diverge from this state when editing, but then tell git about the changes by *committing*
   * `HEAD` is a reference that normally names the current branch. In detached HEAD mode it points directly to a commit. The index may contain staged changes that differ from that commit.

### Moving inside the workflow

| You want to       | Type           |
| ------------- |:-------------:|
| Restore selected files in both the index and working tree from a commit; using HEAD discards staged and unstaged changes to those files | `git checkout <commit-hash> -- <files>` |
| Move the current branch to a commit and reset the index, leaving working files unchanged; changes become unstaged or untracked as appropriate | `git reset <commit-hash>` |
| Move the current branch to a commit and reset the index and working tree. **Discards tracked uncommitted changes and may overwrite untracked files in the way.** Previous commits may be recoverable through reflog until pruned; uncommitted work usually is not. Back up first. | `git reset --hard <commit-hash>` |
| Check out a commit in detached HEAD mode to inspect it. Commits are possible, but create a branch to retain work before switching away | `git checkout <commit-hash>` |
| Switch to an existing branch and update the index and working tree as needed. Local edits may be carried over; Git refuses if they would be overwritten | `git checkout <branch>` |
| Stage files | `git add <files>` |
| Unstage selected files without changing working files | `git reset HEAD -- <files>` |
| Commit staged changes | `git commit -m "Your message"` |

### Working with remote servers
| You want to       | Type           |
| ------------- |:-------------:|
| Copy a remote git repo to your computer, creating a remote named `origin` for that URL | `git clone <repo-url>` |
| Make your local git aware of branches on the server, and their states. Use this to "refresh" a repo (note this does not change your local branches, but simply makes you aware of if yours are outdated or not) | `git fetch <remote-name>` |
| Fetch and remove stale remote-tracking references for branches deleted on the remote; ordinary local branches are not deleted | `git fetch <remote-name> --prune` |
| Create a remote branch, or update it when the push is a fast-forward (subject to permissions and branch rules) | `git push <remote-name> <branch-name>` |
| Fetch the named remote branch and integrate it into your current local branch using the selected merge/rebase strategy | `git pull <remote-name> <branch-name>` (this may cause merge conflicts!) |
| Delete a remote branch | `git push <remote-name> :<branch-name>` |

### Branching
| You want to       | Type           |
| ------------- |:-------------:|
| Make fork of the commit tree at your current HEAD. This could be any commit, so you could theoretically go back to an old commit and branch off that. | `git checkout -b <new-branch-name>` |
| Switch to an existing branch | `git checkout <branch-name>` |
| Delete a branch locally | `git branch -d <branch-name>` |
| Force-delete a local branch without checking whether it is merged; commits reachable only through it may later be pruned | `git branch -D <branch-name>` |
| Show local branches | `git branch` |
| Show remote-tracking branches | `git branch -r` |
| Show local and remote-tracking branches | `git branch -a` |
| Integrate a branch into the current branch; this may fast-forward or create a merge commit | `git merge <branch-name>` |

### Working with others
Note: you probably don't need this for CS439

Say we are on branch `master`. Alice makes some changes to `foo.txt`, and commits it. Bob makes some changes to the file and commits as well. 
One of them will push first, then the other will then have to pull then push.

There are two scenarios:
* Alice and Bob edited completely separate parts of the file.
    - Recall that commits are simply recordings of what's *changed* (diffs). For independent text edits, a merge will usually succeed automatically. A subsequent push may still fail if someone else pushes first.
* Alice and Bob edited the same region
    - When the pull uses a merge and the text edits cannot be combined automatically, Git stops in a **merge conflict state**. The affected text file normally gains markers to show the conflict. Rebase has a different continuation step.

```
This is sentence 1.
This is sentence 2.
<<<<<<< HEAD
This is the awesome and stupendous sentence 3.
=======
This is the amazing and glorious sentence 3.
>>>>>>> <remote>/<branch>
This is sentence 4.
```

If you are the person who has not pushed, you will need to look **carefully** at what is different. Your version is bounded by `<<<<<<< HEAD` and `=======`, their version is bounded by `=======` and `>>>>>>> <remote>/<branch>`. Do **not** just delete one side or the other blindly, you are erasing someone's changes!

You must consider, *semantically*, what the other person has changed, then incorporate both of your changes together into one copy. A resolved version of the above example would be as follows:

```
This is sentence 1.
This is sentence 2.
This is the awesome, stupendous, amazing and glorious sentence 3.
This is sentence 4.
```

For a merge, stage each resolved file with `git add <file>`, then run `git merge --continue` (or `git commit`) and push. To abandon the merge, use `git merge --abort`. If you chose rebase instead, stage the resolution and use `git rebase --continue`.

## Command references

- [git fetch](https://git-scm.com/docs/git-fetch)
- [git reset](https://git-scm.com/docs/git-reset)
- [git checkout](https://git-scm.com/docs/git-checkout)
- [git merge](https://git-scm.com/docs/git-merge)
