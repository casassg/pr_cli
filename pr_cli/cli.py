import json
import os

import click

import auth
import decorators

__version__ = 'None'

APP_NAME = 'pr_cli'


@click.group()
@click.option('--login', is_flag=True)
@click.pass_context
def pr_cli(ctx, login):
    ctx.obj = auth.login(APP_NAME, login)

@pr_cli.command()
@decorators.pass_client
def diff(client):
    click.echo(client.get_user().bio)
