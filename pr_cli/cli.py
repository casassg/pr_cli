import json
import os

import click

import auth
import decorators
import git
import gh

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
    click.echo(user.bio)
    click.echo(git.current_branch())
    click.echo(gh.is_current_branch_updated(user))
