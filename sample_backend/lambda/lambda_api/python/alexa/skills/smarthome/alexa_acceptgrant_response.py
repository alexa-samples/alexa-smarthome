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


class AlexaAcceptGrantResponse:

    def __init__(self, **kwargs):

        self.namespace = kwargs.get('namespace', 'Alexa.Authorization')
        self.name = kwargs.get('name', 'AcceptGrant.Response')
        self.payload_version = kwargs.get('payload_version', "3")
        self.message_id = kwargs.get('message_id', str(uuid.uuid4()))
        self.type = kwargs.get('type', None)
        self.message = kwargs.get('message', None)

    def get_response(self):
        response = {}

        header = {}
        header['namespace'] = self.namespace
        header['name'] = self.name
        header['payloadVersion'] = self.payload_version
        header['messageId'] = self.message_id

        response['event'] = {}
        response['event']['header'] = header
        response['event']['payload'] = {}

        if self.type and self.message:
            response['event']['payload']['type'] = self.type
            response['event']['payload']['message'] = self.message

        return response
