# Git - Quick Primer

A fast-paced introduction to version control and git.
If you want the full blown experience, see the git scm book: https://git-scm.com/book/en/v2

## What is version control
Version control is maintaining a detailed report of changes that happen to your codebase.
Good version control practice allows you to roll back mistakes, work on features in parallel, and combine them into a final product.

## How does Git record history?

* A git **repository** consists of a collection of **branches**.
* Each **branch** is a sequential series of **commits**.
* An individual **commit** describes *what changed* since the last commit.
* Each **commit** has a unique hash that identifies it among all other commits.
* Changes are usually introducing or removing lines from a file, deleting a file, or renaming a file.

## How do I see the history?
Use `git log <branch> <files>` to see a list of commits on `branch` that edited `files` (or any files, if absent).

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
   * `HEAD` is a special tag that indicates the commit the index currently represents. Most of the time this points to a branch, but can potentially not be pointing at a branch (see below)

### Moving inside the workflow

| You want to       | Type           |
| ------------- |:-------------:|
| Make your working copy of a file look like how it used to in some past commit (pass `HEAD` to essentially drop modified or staged changes) | `git checkout <commit-hash> <files>`|
| Reset the working copy and `HEAD` to this commit, retaining files changed since that commit in *modified* state | `git reset <commit-hash>`|
| Reset the working copy and `HEAD` to a prior commit, **PERMANENTLY ERASING ALL CHANGES SINCE THAT COMMIT** (this is useful if you want to drop all modified and staged files versus the last commit by resetting to `HEAD` itself, but otherwise you should **NOT** run this willy-nilly. Ask someone experienced before you do this.) | `git reset --hard <commit-hash>` |
| Reset the working copy and `HEAD` to a prior commit, allowing you explore the repo as it was at this point in time. This is *detached HEAD* mode, meaning `HEAD` is not pointing to the latest commit of a branch. Thus, do not make changes. Create a branch off of the commit if you need an actual working copy. | `git checkout <commit-hash>` |
| Reset the working copy and `HEAD` to the latest commit of a branch | `git checkout <branch>`
| Stage a file | `git add <files>`
| Unstage a staged file | `git reset HEAD <files>` (note how this is a special case of reset above) |
| Commit all staged files | `git commit -m <Message>` (please use commit messages) |

### Working with remote servers
| You want to       | Type           |
| ------------- |:-------------:|
| Copy a remote git repo to your computer, setting `repo-url` to the remote name `origin` | `git clone <repo-url>`
| Make your local git aware of branches on the server, and their states. Use this to "refresh" a repo (note this does not change your local branches, but simply makes you aware of if yours are outdated or not) | `git fetch <remote-name>` |
| Same, but delete all local branches that have since been deleted on the remote | `git fetch <remote-name> --prune` |
| Update a remote branch doesn't exist or is directly behind yours | `git push <remote-name> <branch-name>` |
| Update your local branch with commits the remote branch has but yours doesn't | `git pull <remote-name> <branch-name>` (this may cause merge conflicts!) |
| Delete a remote branch | `git push <remote-name> :<branch-name>` |

### Branching
| You want to       | Type           |
| ------------- |:-------------:|
| Make fork of the commit tree at your current HEAD. This could be any commit, so you could theoretically go back to an old commit and branch off that. | `git checkout -b <new-branch-name>` |
| Switch to an existing branch | `git checkout <branch-name>` |
| Delete a branch locally | `git branch -d <branch-name>` |
| Force-delete an unmerged branch locally (has commits that will be lost by the delete) | `git branch -D <branch-name>` |
| Show all branches | `git branch` |
| Show all branches including remote | `git branch -r` |
| Combine a branch with the current one, merging its commit tree directly into the current one | `git merge <branch-name>` |

### Working with others
Note: you probably don't need this for CS439

Say we are on branch `master`. Alice makes some changes to `foo.txt`, and commits it. Bob makes some changes to the file and commits as well. 
One of them will push first, then the other will then have to pull then push.

There are two scenarios:
* Alice and Bob edited completely separate parts of the file.
    - Recall that commits are simply recordings of what's *changed* (diffs). If the two commit do not overlap, then it will cleanly be pulled and then the push will succeed.
* Alice and Bob edited the same region
    - On pull, we enter what is called a **merge conflict state**. The affected file will gain some markers to guide you to the problem and how to fix it.

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

If you are the person who has not pushed, you will need to look **carefully** at what is different. Your version is bounded by `<<<<<<` and `======`, their version is bounded by `=======` and `>>>>>>`. Do **not** just delete one side or the other blindly, you are erasing someone's changes!

You must consider, *semantically*, what the other person has changed, then incorporate both of your changes together into one copy. A resolved version of the above example would be as follows:

```
This is sentence 1.
This is sentence 2.
This is the awesome, stupendous, amazing and glorious sentence 3.
This is sentence 4.
```

Then, you must stage and commit the fixed file. Finally, push it.
