import json
import os

import click

import auth
import decorators
import git
import gh
import actions

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
    updated = False
    current_branch = git.current_branch()

    # Check for un commited files   
    actions.check_uncommit_files()

    # Push new commits if needed
    updated = actions.update_branch()
    if updated:
        click.echo('Pushed changes to remote!')
    else:
        click.echo('Branch %s is already updated!' % current_branch)
    
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
        c = repo.compare('master',current_branch)
        if c.total_commits == 0: 
            raise click.ClickException('Master and %s are totally synced. Commit some changes to start a PR.' % current_branch)

        # Get PR title and body
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
    
    # Print current PR URL for user
    click.echo('Pull request updated, see: %s' % pr.html_url)
