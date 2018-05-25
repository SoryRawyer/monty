"""
b2.py : utilities for iteracting with the Backblaze HTTP API
"""

import base64
import hashlib
import os
import requests

class BackBlaze(object):
    """
    BackBlaze : ugh
    """
    AUTH_URL = 'https://api.backblazeb2.com/b2api/v1/b2_authorize_account'

    EXTENSION_TO_MIME_TYPE = {
        'flac' : 'audio/flac',
        'mp3' : 'audio/mpeg',
        'wav' : 'audio/wav',
    }

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

    def upload_file(self, file_location, bucket_id, upload_location):
        """
        upload_file : send stuff to the cloud
        """
        file_upload_info = self.get_file_upload_url(bucket_id)
        _, extension = os.path.splitext(file_location)
        extension = extension.replace('.', '')
        with open(file_location, 'rb') as audio:
            sha1 = hashlib.sha1(audio.read()).hexdigest()
            headers = {
                'Authorization' : file_upload_info['authorizationToken'],
                'X-Bz-File-Name' : upload_location,
                'Content-Type' : self.EXTENSION_TO_MIME_TYPE[extension],
                'X-Bz-Content-Sha1' : sha1,
                'X-Bz-Info-Author' : 'rsawyer (co-authored-by ablewer)',
            }
            audio.seek(0)
            resp = requests.post(file_upload_info['uploadUrl'], audio, headers=headers)
            resp.raise_for_status()
            return resp.json()

    def download_file_by_name(self, bucket_name, file_name, file_destination):
        """
        download_file_by_name : do that thing ("that thing", in this case, is downloading
        files from the sky (cloud))
        """
        url = os.path.join(self.auth_stuff['downloadUrl'], 'file', bucket_name, file_name)
        resp = requests.get(url, headers=self._headers)
        resp.raise_for_status()
        with open(file_destination, 'wb') as out:
            out.write(resp.content)


def main():
    b = BackBlaze()
    buckets = b.list_buckets()
    print(buckets)
    # b.upload_file('/Users/rorysawyer/media/audio/panda bear/panda bear/05 Fire!.flac',
    #               buckets[0]['bucketId'],
    #               'panda_bear/panda_bear/fire!.flac')
    b.download_file_by_name('monty-media', 'panda_bear/panda_bear/fire!.flac', 'fire!.flac')

if __name__ == '__main__':
    main()
