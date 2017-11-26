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


class AlexaPowerController:

    def __init__(self, **kwargs):
        self.namespace = kwargs.get('namespace', 'Alexa')
        self.name = kwargs.get('name', 'Response')
        self.payload_version = kwargs.get('payload_version', '3')
        self.message_id = kwargs.get('message_id', str(uuid.uuid4()))
        self.correlation_token = kwargs.get('correlation_token', None)

        self.type = "BearerToken"
        self.token = kwargs.get('token', None)

        self.endpoint_id = kwargs.get('endpoint_id', 'INVALID')

        self.value = kwargs.get('value', 'TurnOff')

    def create_property(self, **kwargs):
        p = {}
        p['namespace'] = kwargs.get('namespace', 'Alexa.EndpointHealth')
        p['name'] = kwargs.get('name', 'connectivity')
        p['value'] = kwargs.get('value', {'value': 'OK'})
        p['timeOfSample'] = get_utc_timestamp()
        p['uncertaintyInMilliseconds'] = kwargs.get('uncertainty_in_milliseconds', 0)
        return p

    def get_response(self):

        powerStateValue = 'OFF' if self.value == "TurnOff" else 'ON'

        properties = []
        properties.append(self.create_property(namespace='Alexa.PowerController', name='powerState', value=powerStateValue))
        properties.append(self.create_property(namespace='Alexa.EndpointHealth', name='connectivity', value={'value': 'OK'}))

        header = {}
        header['namespace'] = 'Alexa'
        header['name'] = 'Response'
        header['payloadVersion'] = self.payload_version
        header['messageId'] = self.message_id
        header['correlationToken'] = self.correlation_token

        endpoint = {}
        endpoint['scope'] = {}
        endpoint['scope']['type'] = 'BearerToken'
        endpoint['scope']['token'] = self.token
        endpoint['endpointId'] = self.endpoint_id

        payload = {}

        response = {}

        response['context'] = {}
        response['context']['properties'] = properties

        response['event'] = {}
        response['event']['header'] = header
        response['event']['endpoint'] = endpoint
        response['event']['payload'] = payload

        return response