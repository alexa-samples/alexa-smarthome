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

import uuid


class AlexaResponse:

    def __init__(self, **kwargs):
        self.message_id = str(uuid.uuid4())
        self.name = 'Response'
        self.payload_version = kwargs.get('payload_version', '3')
        self.correlation_token = kwargs.get('correlation_token', None)
        self.endpoint_id = kwargs.get('endpoint_id', None)
        self.token = kwargs.get('token', None)

    def get_response(self):
        response = {}
        event = {}

        header = {}
        header['namespace'] = 'Alexa'
        header['name'] = self.name
        header['payloadVersion'] = self.payload_version
        header['messageId'] = self.message_id
        if self.correlation_token:
            header["correlationToken"] = self.correlation_token

        endpoint = {}
        if not self.endpoint_id:
            self.endpoint_id = "INVALID"
        endpoint['endpointId'] = self.endpoint_id

        # If this is an asynchronous response, include the token
        if self.token:
            scope = {}
            scope['type'] = 'BearerToken'
            scope['type'] = self.token
            endpoint['scope'] = scope

        event['header'] = header
        event['endpoint'] = endpoint
        event['payload'] = {}

        response['event'] = event

        return response
