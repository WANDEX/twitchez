#!/usr/bin/env python3
# coding=utf-8

from .data import write_private_data
from random import randint
import requests


def generate_nonce(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(randint(0, 9)) for _ in range(length)])


def get_user_id(token, c_id):
    """Get user id by access token."""
    url = "https://api.twitch.tv/helix/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": c_id
    }
    try:
        r = requests.get(url, headers=headers)
    except Exception as err:
        raise Exception(err)
    return(r.json()['data'][0]['id'])


def get_auth_token():
    """Read more here:
    'https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#oauth-implicit-code-flow'
    """
    client_id = "dadsrpg93f0tvvq8zhbno69m2e3spr"  # this application client id
    redirect_uri = "https://localhost"
    scope = "user:read:follows"
    state = generate_nonce()  # against simple CSRF attacks
    url = "".join((
        "https://id.twitch.tv/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&response_type=token"
        f"&scope={scope}"
        f"&state={state}"
    ))
    try:
        r = requests.get(url)
    except Exception as err:
        raise Exception(err)
    if state in r.url:  # for safety check that 'state' is substring in response url
        bold = "\033[1m"
        end = "\033[0;0m"
        print("1) Open following url in your browser.")
        print("2) If asked to login into twitch, you are required to do so, in order to get 'access_token' only known by twitch, and now also known by YOU! B)")
        print(f"{bold}After successful login, page is not existing! ALL WORK AS EXPECTED!{end}")
        print("3) Copy from url 'access_token' content (from '=' to first '&' excluding those symbols!) and paste that as input here.")
        print(f"'{r.url}'")
        access_token = input("access_token=")
        # try to get user_id by new access_token & validate that user put right access_token
        user_id = get_user_id(access_token, client_id)
        # write to private file for using in further requests
        write_private_data(user_id, access_token, client_id)
        print("SUCCESS")
    else:
        print(f"original state: '{state}' not matches state in response!")
        print("^ because of that - to prevent possible 'CSRF attack' on you, application was stopped, so nobody could harm you!")
        exit(666)


if __name__ == "__main__":
    # execute when ran directly
    get_auth_token()
