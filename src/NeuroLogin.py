"""Module for setting up connection with Neurosteer API"""

import requests
import json
import sys
if sys.version_info.major == 2:
    from urlparse import (urlparse, parse_qs)  # python2
else:
    from urllib.parse import (urlparse, parse_qs)  # python3



class NeuroLogin:
    """A class that retrieves access token from api.neurosteer.com

       Args:
            email: user's email for api.neurosteer.com/signin
            password: user's password for api.neurosteer.com/signin
            sensor id: user's sensor
    """
    def __init__(self, email, password, sensor):
        self.email = email
        self.password = password
        self._sensor = sensor
        return

    def get_token(self):
        try:
            r = requests.post("https://api.neurosteer.com/signin",
                              data={'email': self.email, 'password':  self.password})
            data = json.loads(r.text)
            response_url = data[u'url']
            parsed = urlparse(response_url)
            access_token = parse_qs(parsed.query)['access_token'][0]
            self.token = access_token
            print("token successfully retrieved")
        except KeyError:
            print("Invalid email or password")
            print("Please re-enter email:")
            self.email = str(input())
            print("Please re-enter password:")
            self.password = str(input())
            self.get_token()
        return

    def update_description(self, description):
        r = requests.put("https://api.neurosteer.com/api/v1/sensors/" + self._sensor + "/latest/description",
                     headers={'Authorization': 'Bearer ' + self.token,
                              "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                     data={u'description': description})

        if r.status_code == 200:
            print('updated description')
