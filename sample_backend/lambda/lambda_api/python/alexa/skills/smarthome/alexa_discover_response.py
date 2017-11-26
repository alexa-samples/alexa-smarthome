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

import random
import uuid

from .alexa_utils import get_utc_timestamp


class AlexaDiscoverResponse:

    def __init__(self, request):
        self.message_id = str(uuid.uuid4())
        self.name = 'Discover.Response'
        self.payload_version = request["directive"]["header"]["payloadVersion"]
        self.endpoints = []

    def add_endpoint(self, thing):
        # Translate the AWS IoT Thing attributes
        endpoint_id_value = thing['thingName']
        # HACK Using the thing name as the friendly name!
        friendly_name_value = thing['thingName'].replace('_', ' ')
        # NOTE SWITCH is currently hardcoded into the endpoint
        self.endpoints.append(self.create_endpoint(endpoint_id=endpoint_id_value, friendly_name=friendly_name_value, display_categories=['SWITCH']))

    def create_capability(self, **kwargs):
        capability = {}
        capability['type'] = kwargs.get('type', 'AlexaInterface')
        capability['interface'] = kwargs.get('interface', 'Alexa')
        capability['version'] = kwargs.get('version', '3')
        supported = kwargs.get('supported', None)  # [{"name": "powerState"}]
        if supported:
            capability['properties'] = {}
            capability['properties']['supported'] = supported
            capability['properties']['proactivelyReported'] = kwargs.get('proactively_reported', True)
            capability['properties']['retrievable'] = kwargs.get('retrievable', True)

        return capability

    def create_endpoint(self, **kwargs):
        endpoint = {}
        endpoint['endpointId'] = kwargs.get('endpoint_id', 'endpoint_' + "%0.6d" % random.randint(0, 999999))
        endpoint['friendlyName'] = kwargs.get('friendly_name', 'Endpoint')
        endpoint['description'] = kwargs.get('description', 'Endpoint Description')
        endpoint['manufacturerName'] = kwargs.get('manufacturer_name', 'Unknown Manufacturer')
        endpoint['displayCategories'] = kwargs.get('display_categories', ['OTHER'])

        # NOTE: These capabilities are hardcoded, how might we expose them differently?
        endpoint['capabilities'] = []
        endpoint['capabilities'].append(self.create_capability())
        endpoint['capabilities'].append(self.create_capability(interface='Alexa.PowerController', supported=[{"name": "powerState"}]))
        endpoint['capabilities'].append(self.create_capability(interface='Alexa.EndpointHealth', supported=[{"name": "connectivity"}]))
        return endpoint

    def create_property(self, **kwargs):
        p = {}
        p['namespace'] = kwargs.get('namespace', 'Alexa')
        p['name'] = 'powerState'
        p['value'] = 'ON'
        p['timeOfSample'] = get_utc_timestamp()
        p['uncertaintyInMilliseconds'] = kwargs.get('uncertainty_in_milliseconds', 0)
        return p

    def get_response(self):
        response = {}
        # context = {}
        event = {}

        # properties = []
        # properties.append(self.create_property(namespace='Alexa.PowerController'))
        # context['properties'] = properties

        header = {}
        header['namespace'] = 'Alexa.Discovery'
        header['name'] = self.name
        header['payloadVersion'] = self.payload_version
        header['messageId'] = self.message_id

        # self.endpoints.append(self.create_endpoint())

        payload = {}
        payload['endpoints'] = self.endpoints

        event['header'] = header
        event['payload'] = payload

        # response['context'] = context
        response['event'] = event

        return response
