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

def check_uncommit_files(ignore=False):
    unt = list(filter(None, get_untracked_files()))
    mods = list(filter(None, get_modified_files()))
    if (unt or mods) and not ignore:
        if unt: click.echo('Untracked files:')
        for f in unt:
            click.echo(f)
        if mods: click.echo('Modified files:')
        for f in mods:
            click.echo(f)
        click.echo('You have untracked and/or modified files.')
        if not click.confirm('Are you sure you want to continue?'):
            raise click.ClickException('Solve ignored/modified files before proceeding')
    tbc = list(filter(None, get_to_be_commit_files()))
    if tbc:
        click.echo('To be commit files:')
        for f in tbc:
            click.echo(f)
        if not click.confirm('Are you sure you want to continue?'):
            raise click.ClickException('Solve ignored/modified files before proceeding')
        if click.confirm('Would you like to commit the changes?'):
            cm = click.prompt('Commit message')
            c = delegator.run('git commit -m "%s"' % cm)
            if c.return_code != 0:
                click.echo(c.err)
                raise click.ClickException('Commit errored')



def update_branch():
    c = delegator.run('git push -u origin %s' % current_branch())
    click.echo(c.out)
    if c.return_code != 0:
        click.echo(c.err)
        raise click.ClickException('There was an error pushing the current branch')
    

    