import click
import os
import json
from github import Github
from github.Authorization import Authorization
from github.GithubException import BadCredentialsException, TwoFactorException, GithubException
from github.PaginatedList import PaginatedList


def _get_token_otp(app_name, user):
    otp = click.prompt('2FA code (SMS or Authenticator app)')
    request_header = {'X-GitHub-OTP': otp}
    try:
        auths = PaginatedList(
            Authorization,
            user._requester,
            "/authorizations",
            None,
            headers=request_header
        )
        auth = [auth for auth in auths if auth.note == app_name][0]
        auth._requester.requestJsonAndCheck(
            "DELETE",
            auth.url,
            headers=request_header
        )

        return user.create_authorization(note=app_name, scopes=['repo', 'gist'], onetime_password=otp)
    except BadCredentialsException:
        raise click.ClickException('Bad credentials, make sure your username, password and 2FA code are correct')


def _get_token(app_name):
    user = click.prompt('GitHub Email/GitHub Username')
    password = click.prompt('Password', hide_input=True)
    g = Github(user, password)

    user = g.get_user()

    try:
        auth = [auth for auth in user.get_authorizations() if auth.note == app_name][0]
        auth.delete()
        auth = user.create_authorization(note=app_name, scopes=['repo', 'gist'])
    except BadCredentialsException:
        raise click.ClickException('Bad credentials, make sure your username and password are correct')
    except TwoFactorException:
        auth = _get_token_otp(app_name, user)

    return auth.token


def login(app_name, login):
    folder = click.get_app_dir(app_name)
    conf_filename = os.path.join(folder, 'config.json')
    if not os.path.exists(conf_filename):
        os.makedirs(folder)
        with open(conf_filename, 'w') as f:
            json.dump({}, f)
    with open(conf_filename, 'r') as f:
        conf = json.load(f)
    token = conf.get('token', None)
    if not token or login:
        token = _get_token(app_name)
    try:
        Github(token).get_user()
    except GithubException:
        click.echo('Authentification expired')
        token = _get_token(app_name)
    conf.update({'token': token})
    with open(conf_filename, 'w') as f:
        json.dump(conf, f)
    return Github(token)
