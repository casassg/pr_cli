import click
import git
import delegator

def check_uncommit_files(ignore=False):
    # Check if untracked or modified
    unt = list(filter(None, git.get_untracked_files()))
    mods = list(filter(None, git.get_modified_files()))
    if (unt or mods) and not ignore:
        if unt: click.echo('Untracked files:')
        for f in unt:
            click.echo('- %s' % f)
        if mods and unt: click.echo('')
        if mods: click.echo('Modified files:')
        for f in mods:
            click.echo('- %s' % f)
        click.echo('')
        click.echo('You have untracked and/or modified files.')
        if not click.confirm('Are you sure you want to continue?'):
            raise click.ClickException('Solve ignored/modified files before proceeding')

    # Check for files ready to be commited
    tbc = list(filter(None, git.get_to_be_commit_files()))
    if tbc:
        click.echo('To be commit files:')
        for f in tbc:
            click.echo('- %s' % f)
        if click.confirm('Would you like to commit the changes?'):
            cm = click.prompt('Commit message')
            c = delegator.run('git commit -m "%s"' % cm)
            if c.return_code != 0:
                click.echo(c.err)
                raise click.ClickException('Commit errored')

def update_branch():
    current_branch = git.current_branch()
    c = delegator.run('git push --porcelain -u origin %s' % current_branch)
    
    if c.return_code != 0:
        click.echo(c.err)
        raise click.ClickException(c.err)

    try:
        lines = c.out.split('\n')
        flag = lines[1].split('\t')[0]
        if flag == '=':
            return False
        elif flag == '!':
            raise click.ClickException("Branch was rejected. Pull branch: git pull origin %s" % current_branch)
        elif flag in ['*','-','+', ' ']:
            return True
        else:
            raise click.ClickException(c.out)
    except:
        raise click.ClickException(c.out)