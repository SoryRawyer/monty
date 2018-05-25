"""
b2.py : utilities for iteracting with the Backblaze HTTP API
"""

import base64
import os
import requests

class BackBlaze(object):
    """
    BackBlaze : ugh
    """
    AUTH_URL = 'https://api.backblazeb2.com/b2api/v1/b2_authorize_account'

    def __init__(self):
        # non-standard way of storing/accessing b2 creds, I guess
        env_vars = os.environ
        self.auth_stuff = self.get_auth_token(env_vars['B2_ACCOUNT_ID'],
                                              env_vars['B2_APPLICATION_KEY'])

    def get_auth_token(self, account_id, application_key):
        """
        get_auth_token : call the auth endpoint to get the url and token and suff
        """
        auth_string = '{}:{}'.format(account_id, application_key).encode('utf-8')
        header = {'Authorization' : 'Basic {}'.format(str(base64.b64encode(auth_string))[2:-1])}
        resp = requests.get(self.AUTH_URL, headers=header)
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(resp.content)
            raise err
        return resp.json()

def main():
    b = BackBlaze()
    print(b.auth_stuff)

if __name__ == '__main__':
    main()
