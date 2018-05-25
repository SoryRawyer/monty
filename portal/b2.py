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
        self.account_id = env_vars['B2_ACCOUNT_ID']
        self.auth_stuff = self.get_auth_token(env_vars['B2_ACCOUNT_ID'],
                                              env_vars['B2_APPLICATION_KEY'])
        self._headers = {'Authorization' : self.auth_stuff['authorizationToken']}
        self._params = {'accountId' : self.account_id}

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

    def list_buckets(self) -> list:
        """
        list_buckets : return a list of bucket information
        """
        url = os.path.join(self.auth_stuff['apiUrl'], 'b2api', 'v1', 'b2_list_buckets')
        resp = requests.get(url, headers=self._headers, params=self._params)
        resp.raise_for_status()
        return resp.json()['buckets']

    def get_file_upload_url(self, bucket_id) -> dict:
        """
        get_file_upload_url : pretty self-explanatory
        """
        url = os.path.join(self.auth_stuff['apiUrl'], 'b2api', 'v1', 'b2_get_upload_url')
        params = {'bucketId' : bucket_id}
        resp = requests.get(url, headers=self._headers, params=params)
        resp.raise_for_status()
        return resp.json()

def main():
    b = BackBlaze()
    # print(b.auth_stuff)
    buckets = b.list_buckets()
    print(buckets)
    file_upload_spot = b.get_file_upload_url(buckets[0]['bucketId'])
    print(file_upload_spot)

if __name__ == '__main__':
    main()
