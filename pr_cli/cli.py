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
    updated = False
    current_branch = git.current_branch()
    repo = gh.current_repo(user)

    git.check_untracked_modified()

    if not gh.is_current_branch_updated(user):
        click.echo('Updating current branch...')
        git.update_branch()
        click.echo('Updating current branch...Done!')
        updated = True
    else:
        click.echo('Branch %s is updated!' % current_branch)
    
    c = repo.compare('master',current_branch)
    if c.total_commits == 0:
        raise click.ClickException('Master and %s are totally synced. Commit some changes to start a PR.' % current_branch)
    
    pr = gh.current_pr(user)
    if pr and updated:
        MARKER = '# Everything below is ignored. Comment above what are your changes'
        message = click.edit('\n\n' + MARKER)
        comment = None
        if message:
            comment = message.split(MARKER, 1)[0].rstrip('\n')
        if not message or not comment:
            click.echo('No comments to be added!')
        else:
            pr.create_issue_comment(comment)
    elif not pr:
        
        MARKER = '# Everything below is ignored. First line is title, after that is body of pull request'
        message = click.edit('\n\n' + MARKER)
        comment = None
        if message:
            comment = message.split(MARKER, 1)[0].rstrip('\n')
        lines = comment.split('\n')

        try:
            body ='\n'.join(lines[1:]).rstrip('\n')
            pr = repo.create_pull(title=lines[0], body=body, head=current_branch, base='master')
        except GithubException as e:
            if e.status == 404:
                raise click.ClickException('No changes between %s and %s' % ('master', current_branch))
            else:
                raise e


        
    else:
        click.echo('Nothing changed!')
    
    click.echo('Pull request updated, see: %s' % pr.url)
