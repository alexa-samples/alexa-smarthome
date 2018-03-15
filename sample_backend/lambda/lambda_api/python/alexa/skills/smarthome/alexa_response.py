# -*- coding: utf-8 -*-

# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import uuid

from .alexa_utils import get_utc_timestamp


class AlexaResponse:

    def __init__(self, **kwargs):

        self.correlation_token = kwargs.get('correlation_token', None)
        self.cookies = {}
        self.include_endpoint = kwargs.get('include_endpoint', True)
        self.payload = {}
        self.properties = []

        # Set up the event structure
        self.event = {
            'header': {
                'namespace': kwargs.get('namespace', 'Alexa'),
                'name': kwargs.get('name', 'Response'),
                'messageId': str(uuid.uuid4()),
                'payloadVersion': kwargs.get('payload_version', '3')
            },
            'endpoint': {
                "scope": {
                    "type": "BearerToken",
                    "token": kwargs.get('token', 'INVALID')
                },
                "endpointId": kwargs.get('endpoint_id', 'INVALID')
            },
            'payload': {}
        }

    def add_cookie(self, key, value):
        self.cookies[key] = value

    def add_property(self, **kwargs):
        self.properties.append(self.create_property(**kwargs))

    def create_property(self, **kwargs):
        p = {}
        p['namespace'] = kwargs.get('namespace', 'Alexa.EndpointHealth')
        p['name'] = kwargs.get('name', 'connectivity')
        p['value'] = kwargs.get('value', 'OK')
        p['timeOfSample'] = get_utc_timestamp()
        p['uncertaintyInMilliseconds'] = kwargs.get('uncertainty_in_milliseconds', 0)
        return p

    def get(self):

        response = {
            'event': self.event
        }
        response['event']['payload'] = self.payload

        if self.correlation_token is not None:
            response['event']['header']['correlationToken'] = self.correlation_token

        if self.include_endpoint:
            if len(self.cookies) > 0:
                response['event']['endpoint']['cookie'] = self.cookies
        else:
            response['event'].pop('endpoint')

        if len(self.properties) > 0:
            response['context'] = {}
            response['context']['properties'] = self.properties

        return response

    def set_payload(self, payload):
        self.payload = payload
