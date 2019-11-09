import time

import requests


API_URL = 'https://api.trakt.tv/'
CLIENT_ID = '60cc5c14c797ceae109e7a408f27914d83125b7ad0726cc382d98d57c923fb12'
CLIENT_SECRET = \
    '1934c60d541c9802e8186ae0c0a5d7b3244d69aa3bfe9031fecf9a55b96c6f3f'


def authenticate(code=None, expires=None):
    """Device authentication with Trakt.tv.

    Called with no args sets up new authentication. This method should
    be polled at 'interval' key supplying code as 'device_code' with
    expires set to None.

    Called with code set to 'device_code' will throw 400 until user has
    authenticated. After a user has authenticated method will return on
    sucess dict where the values for the keys 'access_token' and
    'refresh_token' at least are saved.
    It is advisable to save the sum of 'created_at' and 'expires_in' to
    later call this method providing that value as `expires` value.

    Called with code and expires set, if expires is greater than current
    time a new token will be obtained using `code` as the refresh_token,
    the same values as above should be retained.

    """

    if not code:
        result = requests.post(API_URL + 'oauth/device/code',
                               data={'client_id': CLIENT_ID})
        return result.json()
    if not expires:
        result = requests.post(API_URL + 'oauth/device/token',
                               data={
                                   'client_id': CLIENT_ID,
                                   'client_secret': CLIENT_SECRET,
                                   'code': code,
                               })
        return result.json()
    if expires >= time.time():
        result = requests.post(API_URL + 'oauth/token',
                               data={
                                   'client_id:': CLIENT_ID,
                                   'client_secret': CLIENT_SECRET,
                                   'refresh_token': code,
                                   'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
                                   'grant_type': 'refresh_token',
                               })
        return result.json()
    return False


def get_request(path, auth_token, **params):
    headers = {
        'Authorization': 'Bearer {}'.format(auth_token),
        'trakt-api-version': '2',
        'trakt-api-key': CLIENT_ID,
        'Content-Type': 'application/json',
    }
    return requests.get(API_URL + path, headers=headers, params=params).json()
