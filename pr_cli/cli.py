import json
import os

import click

import auth
import decorators
import git
import gh
import actions

__version__ = 'None'

APP_NAME = 'pr_cli'


@click.group()
@click.option('--login', is_flag=True, help='Forces login with username and password.')
@click.pass_context
def pr_cli(ctx, login):
    ctx.obj = auth.login(APP_NAME, login).get_user()


@pr_cli.command()
@decorators.pass_client
def diff(user):
    current_branch = git.current_branch()

    # Check if we are on master and warn user
    if current_branch == 'master' and not click.confirm('You are on master branch, are you sure you want to continue?'):
        raise click.ClickException("Switch branches before continuing")

    # Check for un commited files   
    actions.check_uncommit_files()

    # Push new commits if needed
    try:
        updated = git.update_branch()
    except RuntimeError as e:
        raise click.ClickException(str(e))
    if updated:
        click.echo('Pushed changes to remote!')
    else:
        click.echo('Branch %s is already updated!' % current_branch)

    # Check if on master and exit in that case
    if current_branch == 'master':
        click.echo('No pull request as you are on master already')
        return

    # Try to find existing PR for current branch
    pr = gh.current_pr(user)

    # Add comment if wanted
    if pr and updated and click.confirm('Do you want to add comment about current changes in PR?'):

        MARKER = '# Everything below is ignored. Comment above what are your changes (or leave it blank to skip)'
        message = click.edit('\n\n' + MARKER)
        comment = None
        if message:
            comment = message.split(MARKER, 1)[0].rstrip('\n')
        if not comment:
            click.echo('No comments to be added!')
        else:
            pr.create_issue_comment(comment)

    # Create new Pull request
    elif not pr:
        repo = gh.current_repo(user)

        # Check if it needs a PR
        c = repo.compare('master', current_branch)
        if c.total_commits == 0:
            raise click.ClickException(
                'Master and %s are totally synced. Commit some changes to start a PR.' % current_branch)

        # Get PR title and body
        MARKER = '# Everything below is ignored. First line is title, after that is body of pull request'
        message = click.edit('\n\n' + MARKER)
        comment = None
        if message:
            comment = message.split(MARKER, 1)[0].rstrip('\n')
            lines = comment.split('\n')
        else:
            raise click.ClickException('Aborting')

        body = '\n'.join(lines[1:]).rstrip('\n')
        pr = repo.create_pull(title=lines[0], body=body, head=current_branch, base='master')

    # Print current PR URL for user
    click.echo('Pull request updated, see: %s' % pr.html_url)
