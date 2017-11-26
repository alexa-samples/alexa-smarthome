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
from .alexa_utils import get_utc_timestamp


class AlexaChangeReport:

    def __init__(self, **kwargs):
        self.namespace = kwargs.get('namespace', 'Alexa')
        self.name = kwargs.get('name', 'ChangeReport')
        self.payload_version = kwargs.get('payload_version', '3')
        self.message_id = kwargs.get('message_id', str(uuid.uuid4()))

        self.type = "BearerToken"
        self.token = kwargs.get('token', 'INVALID')

        self.endpoint_id = kwargs.get('endpoint_id', 'INVALID')

        self.cause_type = kwargs.get('cause_type', 'PHYSICAL_INTERACTION')

    def create_property(self, **kwargs):
        p = {}
        p['namespace'] = kwargs.get('namespace', 'Alexa')
        p['name'] = kwargs.get('name', 'powerState')
        p['value'] = kwargs.get('value', 'ON')
        p['timeOfSample'] = get_utc_timestamp()
        p['uncertaintyInMilliseconds'] = kwargs.get('uncertainty_in_milliseconds', 0)
        return p

    def get_response(self):
        response = {}
        response['context'] = {}
        response['context']['properties'] = []
        response['context']['properties'].append(self.create_property(namespace='Alexa.PowerController', name='powerState', value='ON'))
        response['context']['properties'].append(self.create_property(namespace='Alexa.EndpointHealth', name='connectivity', value={'value': 'OK'}))
        response['event'] = {}
        response['event']['header'] = {}
        response['event']['header']['namespace'] = self.namespace
        response['event']['header']['name'] = self.name
        response['event']['header']['payloadVersion'] = self.payload_version
        response['event']['header']['messageId'] = self.message_id
        response['event']['endpoint'] = {}
        response['event']['endpoint']['scope'] = {}
        response['event']['endpoint']['scope']['type'] = self.type
        response['event']['endpoint']['scope']['token'] = self.token
        response['event']['endpoint']['endpointId'] = self.endpoint_id
        response['event']['payload'] = {}
        response['event']['payload']['change'] = {}
        response['event']['payload']['change']['cause'] = {}
        response['event']['payload']['change']['cause']['type'] = self.cause_type
        response['event']['payload']['change']['properties'] = []
        response['event']['payload']['change']['properties'].append(self.create_property(namespace='Alexa.BrightnessController', name='brightness', value=65))

        return response
