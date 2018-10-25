import click
import delegator

def current_branch():
    c = delegator.run('git rev-parse --abbrev-ref HEAD')
    return c.out.replace('\n','').strip()

def current_repo_url(remote='origin'):
    c = delegator.run('git config --get remote.{}.url'.format(remote))
    return c.out.replace('\n','').strip()

def current_sha():
    c = delegator.run('git rev-parse HEAD')
    return c.out.replace('\n','').strip()

def get_untracked_files():
    c = delegator.run('git ls-files . --exclude-standard --others')
    return c.out.strip().split('\n')

def get_modified_files():
    c = delegator.run('git ls-files .  --modified')
    return c.out.strip().split('\n')

def get_to_be_commit_files():
    c = delegator.run('git diff --cached --name-only --raw')
    return c.out.strip().split('\n')


    

    