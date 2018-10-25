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

def update_branch():
    branch = current_branch()
    c = delegator.run('git push --porcelain -u origin %s' % branch)
    
    if c.return_code != 0:
        raise RuntimeError(c.err)

    try:
        lines = c.out.split('\n')
        flag = lines[1].split('\t')[0]
        if flag == '=':
            return False
        elif flag == '!':
            raise RuntimeError(c.out)
        elif flag in ['*','-','+', ' ']:
            return True
        else:
            raise RuntimeError(c.out)
    except:
        raise RuntimeError(c.out)
    

def checkout_branch(branch):
    delegator.run('git stash')
    c = delegator.run('git checkout %s' % branch)
    delegator.run('git stash pop')
    if c.return_code!=0:
        raise RuntimeError(c.out)

def create_branch(branch_name):
    c = delegator.run('git checkout -b %s' % branch_name)
    if c.return_code!=0:
        raise RuntimeError(c.out)

def pull_branch(branch):
    c = delegator.run('git pull origin %s' % branch)
    if c.return_code!=0:
        raise RuntimeError(c.out)
    return c.out