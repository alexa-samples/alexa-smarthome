# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import http.client
from urllib.parse import urlencode


class ApiAuth:

    def post_to_api(self, payload):
        connection = http.client.HTTPSConnection("api.amazon.com")
        headers = {
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
        }
        connection.request('POST', '/auth/o2/token', urlencode(payload), headers)
        return connection.getresponse()

    def get_access_token(self, code, client_id, client_secret, redirect_uri):
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        return self.post_to_api(payload)

    @staticmethod
    def get_user_id(access_token):
        connection = http.client.HTTPSConnection('api.amazon.com')
        connection.request('GET', '/user/profile?access_token=' + access_token)
        return connection.getresponse()

    def refresh_access_token(self, refresh_token, client_id, client_secret, redirect_uri):
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        return self.post_to_api(payload)


