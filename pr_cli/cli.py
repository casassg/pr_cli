import json
import os

import click

import auth
import decorators
import git
import gh

from github import GithubException


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
    repo = gh.current_repo(user)
    updated = gh.is_current_branch_updated(user)
    # Check for un commited files   
    git.check_uncommit_files()

    # Push new commits if needed
    if not updated:
        click.echo('Updating current branch...')
        git.update_branch()
        click.echo('Updating current branch...Done!')
    else:
        click.echo('Branch %s is already updated!' % current_branch)
    
    # Check if it needs a PR
    c = repo.compare('master',current_branch)
    if c.total_commits == 0:
        raise click.ClickException('Master and %s are totally synced. Commit some changes to start a PR.' % current_branch)
    
    # Try to find existing PR for current branch
    pr = gh.current_pr(user)

    # Add comment if wanted
    if pr and updated and click.confirm('Do you want to comment current changes?'):
        if pr.state == 'closed':
            if click.confirm('PR is closed, do you want to reopen it?'):
                pr.edit(state='open')
            else:
                raise click.ClickException('PR is closed. See: %s' % pr.html_url)
        MARKER = '# Everything below is ignored. Comment above what are your changes (or leave it blank)'
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
        MARKER = '# Everything below is ignored. First line is title, after that is body of pull request'
        message = click.edit('\n\n' + MARKER)
        comment = None
        if message:
            comment = message.split(MARKER, 1)[0].rstrip('\n')
            lines = comment.split('\n')
        else:
            raise click.ClickException('Aborting')

        body ='\n'.join(lines[1:]).rstrip('\n')
        pr = repo.create_pull(title=lines[0], body=body, head=current_branch, base='master')
    else:
        click.echo('Nothing changed!')
    
    click.echo('Pull request updated, see: %s' % pr.html_url)
