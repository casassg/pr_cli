# GitHub Flow CLI

CLI that helps make the flow described at [GitHub Flow](https://guides.github.com/introduction/flow/). CLI interface inspired by [Phabricator's arcanist CLI](https://github.com/phacility/arcanist).

## Usage

- `gh diff`: Create a pull request for current branch to master. Recognizes if it's working from a fork if you want to do a pull request on original or fork. Loads pull request templates from repo files and loads to edit pull request. Checks for missing tracked files and pushes to branch on origin.
    - `--reviewers, -r`: GitHub reviewers. Prompted if not passed to command.
    - `--issue, -i`: Assign to a GitHub issue. Defaults to None.
    - `--base, -b`: Branch to be merged to. Defaults to `origin/master`.
    - `--milestone, -m`: Milestone to assign pull request. None if not used.
    - `--label, -l`: Add specific label to pull request. Optional. Multiple usage for multiple labels.
- `gh land`: Merges pull request created for current branch (if exists). Don't overwrite. Checks if local commit is updated and status are all successfull. Checks if Pull request has been merged already. Deletes local and remote branch and moves local to master (and pulls latest updates).
    - `--method`: Merge method can be either `merge`, `squash` or `rebase`. Default is `merge`.
- `gh status`: Shows current status for current commit. If branch has Pull request associated, then also show pull request information.
- `gh patch #<PR number>`: Creates local branch for specific PR code. Check out the code. Set up upstream branch if branch is modifiable by user, else it throws a warning.
    - `--name, -n`: Name for local branch. Defaults to upstream branch name. If fork, format is: `<username>/<branchname>`.
- `gh feature <name>`: Creates a local branch and checks it out. Uses github username to construct it like: `<username>/<name>`.
    - `--base, -b`: Branch to checkout the code from. Defaults to `master`.
- `gh paste`: Create github gist. Returns url for new gist
    - `--file, -f`: Add file to gist. If no file is defined, an empty editor will be opened and sent to creation.

## Development

Requirements: `python3.7`, `pipenv`

1. `pipenv install`
2. `pipenv run gh`
