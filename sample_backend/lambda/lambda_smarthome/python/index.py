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

import json
import os
import urllib.request
from urllib.request import HTTPError


def get_api_url(api_id, aws_region, resource):
    return 'https://{0}.execute-api.{1}.amazonaws.com/prod/{2}'.format(api_id, aws_region, resource)


def handler(request, context):
    try:
        print("LOG skill.index.handler.request:", request)

        # Get the Environment Variables, these are used to dynamically compose the API URI

        # Get the Region
        env_aws_default_region = os.environ.get('AWS_DEFAULT_REGION', None)
        if env_aws_default_region is None:
            print("ERROR skill.index.handler.aws_default_region is None default to us-east-1")
            env_aws_default_region = 'us-east-1'

        # Get the API ID
        env_api_id = os.environ.get('api_id', None)
        if env_api_id is None:
            print("ERROR skill.index.handler.env_api_id is None")
            return '{}'

        # Pass the requested directive to the backend Endpoint API
        url = get_api_url(env_api_id, env_aws_default_region, 'directives')
        data = bytes(json.dumps(request), encoding="utf-8")
        headers = {'Content-Type': 'application/json'}
        req = urllib.request.Request(url, data, headers)
        result = urllib.request.urlopen(req).read().decode("utf-8")
        response = json.loads(result)
        print("LOG skill.index.handler.response:", response)
        return response

    except HTTPError as error:
        print("ERROR skill.index.handler.error:", error)
        return error

    except ValueError as error:
        print("ERROR skill.index.handler.error:", error)
        return error
