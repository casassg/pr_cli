import delegator

def current_branch():
    c = delegator.run('git rev-parse --abbrev-ref HEAD')
    return c.out.replace('/n','').strip()

def current_repo_url(remote='origin'):
    c = delegator.run('git config --get remote.{}.url'.format(remote))
    return c.out.replace('/n','').strip()

def current_sha():
    c = delegator.run('git rev-parse HEAD')
    return c.out.replace('/n','').strip()