import git
import click
from github import GithubException

def current_repo(user):
    url  = git.current_repo_url()
    return [repo for repo in user.get_repos() if repo.git_url == url or  repo.ssh_url == url][0]

def is_current_branch_updated(user):
    repo = current_repo(user)
    branch = git.current_branch()
    try:
        branch = repo.get_branch(branch)
    except GithubException:
        return False
    if not branch:
        return False
    local_sha = git.current_sha()
    return branch.commit.sha == local_sha

def current_pr(user, base='master'):
    repo = current_repo(user)
    branch = git.current_branch()
    for pr in repo.get_pulls():
        if pr.base.label == base and pr.head.label == git.current_branch():
            return pr
    return None
