# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""Alexa Smart Home Validation Package Sample Code.

This module is used by Alexa Smart Home skills to validate their Lambda responses and async
messages before sending them back to Alexa. If an error is found, an exception is thrown so that
the developer can catch the error and do something about it, instead of sending it back to Alexa
and causing an error on the Alexa side.

This specific package uses the jsonschema (https://github.com/Julian/jsonschema) Python implementation
of the JSON Schema Draft 4 to perform the actual validation against the validation schema.

"""

import json

from jsonschema import validate

def validate_message(request, response):

    # update below with path to your validation schema
    # this path works if you copy the latest validation schema into the same directory as this file
    # validation schema: https://github.com/alexa/alexa-smarthome/wiki/Validation-Schema
    path_to_validation_schema = "alexa_smart_home_message_schema.json"

    with open(path_to_validation_schema) as json_file:
        schema = json.load(json_file)
    validate(response, schema)
