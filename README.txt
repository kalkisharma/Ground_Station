# Ground Station

Ground station code for IMAV competition. Off-board computing handles image processing and path planning.

# Contributing

To contribute to this codebase, common version control practices should be observed.

## Cloning Repo
Get a local version of this repository.
```
git clone https://github.com/kalkisharma/Ground_Station.git
```

## Making edits to the code
Everytime an edit is to be made to the code, it should first be made to a new branch on the local machine (off the origin/master branch). "To begin working on anything new in a project, or to change existing things, you create a branch off the stable master branch".

Prior to creating a new branch, you want to ensure our local master branch is up to date with the latest changes.
```
git pull
```

Once updated, you want to create a branch with which to make any local changes to the master code, allowing you to make edits and test, without changing the master branch - give the branch a descriptive name.
```
git checkout -b name_of_new_branch
```

Check which is your current working branch.
```
git branch
```

Now you are free to edit code as you wish in your local, off-master branch.

## Committing changes to your local branch
Stage and commit your changes to your current working branch.
```
git add your_edited_file.py
```

If you have edited many files, you can add them all (new, modified, deleted)
```
git add -A
```
Or
```
git add .
```
Only stage modified and deleted files
```
git add -u
```
Only stage new and modified files
```
git add --ignore-removal .
```

Now commit these staged changes.
```
git commit
```
Remember to write a informative description of the changes you have made
 
## Pushing changes to the master branch
If you are happy with your changes (and they are thoroughly tested and BUG FREE!!), you are ready to push these changes to the master branch.

Switch to the master branch
```
git checkout master
```

During the time it took to make these changes to your code, the master branch may have been edited. Pull the latest from master
```
git pull
```

Now merge our branch with the master branch
```
git merge name_of_new_branch --no-ff
```
(--no-ff indicates that we want to retain all of the commit messages prior to this merge).

Now push the changes
```
git push
```

## Deleting our branch
Since we have successfully merged our new branch with master, we no longer need it, and will delete.
```
git branch -d name_of_new_branch


