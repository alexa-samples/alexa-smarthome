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

import json
import os
from endpoint_cloud import ApiHandler, ApiResponse, ApiResponseBody


def get_api_url(api_id, aws_region, resource):
    return 'https://{0}.execute-api.{1}.amazonaws.com/prod/{2}'.format(api_id, aws_region, resource)


def handler(request, context):
    """
    Main Lambda Handler
    :param request Incoming API Request
    :param context Context for the Request
    """

    print("LOG api.index.handler.request:", request)

    # An API Handler to handle internal operations to the endpoints
    api_handler = ApiHandler()

    # An API Response crafted to return to the caller - in this case the API Gateway
    # The API Gateway expects a specially formatted response
    api_response = ApiResponse()

    try:
        # Get the Environment Variables, these are used to dynamically compose the API URI and pass Alexa Skill Messaging credentials

        # Get the Region
        env_aws_default_region = os.environ.get('AWS_DEFAULT_REGION', None)
        if env_aws_default_region is None:
            print("ERROR skill.index.handler.aws_default_region is None default to us-east-1")
            env_aws_default_region = 'us-east-1'

        # Get the API ID, Client ID, and Client Secret
        env_api_id = os.environ.get('api_id', None)
        env_client_id = os.environ.get('client_id', None)
        env_client_secret = os.environ.get('client_secret', None)
        if env_api_id is None or env_client_id is None or env_client_secret is None:
            api_response.statusCode = 403
            api_response.body = ApiResponseBody(result="ERR", message="Environment variable is not set: api_id:{0} client_id:{1} client_secret:{2}".format(env_api_id, env_client_id, env_client_secret))
            return api_response.create()

        # Reject the request if it isn't from our API
        api_id = request['requestContext']['apiId']
        if api_id != env_api_id:
            api_response.statusCode = 403
            api_response.body = ApiResponseBody(result="ERR", message="api_id did not match")
            return api_response.create()

        # Route the inbound request by evaluating for the resource and HTTP method
        resource = request["resource"]
        http_method = request["httpMethod"]

        # POST to directives : Process an Alexa Directive - This will be used to implement Endpoint behavior and state
        if http_method == 'POST' and resource == '/directives':
            response = api_handler.directive.process(request, env_client_id, env_client_secret, get_api_url(env_api_id, env_aws_default_region, 'auth-redirect'))
            print('LOG api.index.handler.request.api_handler.directive.process.response:', response)
            response_name = json.loads(response)
            if response_name['event']['header']['name'] == 'ErrorResponse':
                api_response.statusCode = 500
            else:
                api_response.statusCode = 200
            api_response.body = response

        # POST to endpoints : Create an Endpoint
        if http_method == 'POST' and resource == '/endpoints':
            response = api_handler.endpoint.create(request)
            api_response.statusCode = 200
            api_response.body = json.dumps(response)

        # GET endpoints : List Endpoints
        if http_method == 'GET' and resource == '/endpoints':
            response = api_handler.endpoint.read(request)
            api_response.statusCode = 200
            api_response.body = json.dumps(response)

        # DELETE endpoints : Delete an Endpoint
        if http_method == 'DELETE' and resource == '/endpoints':
            response = api_handler.endpoint.delete(request)
            api_response.statusCode = 200
            api_response.body = json.dumps(response)

        # POST to event : Create an Event - This will be used to trigger a Proactive State Update
        if http_method == 'POST' and resource == '/events':
            response = api_handler.event.create(request)
            print('LOG api.index.handler.request.api_handler.event.create.response:', response)
            api_response.statusCode = 200
            api_response.body = json.dumps(response)

    except KeyError as key_error:
        # For a key Error, return an error message and HTTP Status of 400 Bad Request
        message_string = "KeyError: " + str(key_error)
        api_response.statusCode = 400
        api_response.body = ApiResponseBody(result="ERR", message=message_string)

    return api_response.create()
