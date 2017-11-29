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
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from jsonschema import validate, SchemaError, ValidationError

from alexa.skills.smarthome import AlexaAcceptGrantResponse, AlexaChangeReport, AlexaDiscoverResponse, AlexaError, AlexaPowerController, AlexaResponse
from .api_auth import ApiAuth

dynamodb_aws = boto3.client('dynamodb')
iot_aws = boto3.client('iot')


class ApiHandler:
    def __init__(self):
        self.directive = _Directive()
        self.event = _Event()
        self.endpoint = _Endpoint()


class _Directive:
    def process(self, request, client_id, client_secret, redirect_uri):
        print('LOG api.ApiHandler.directive.process.request:', request)

        response = None
        # Only process if there is an actual body to process otherwise return an ErrorResponse
        json_body = request['body']
        if json_body:
            json_object = json.loads(json_body)
            namespace = json_object['directive']['header']['namespace']

            if namespace == "Alexa.Authorization":
                grant_code = json_object['directive']['payload']['grant']['code']
                grantee_token = json_object['directive']['payload']['grantee']['token']

                # Spot the default from the Alexa.Discovery sample. Use as a default for development.
                if grantee_token == 'access-token-from-skill':
                    user_id = "0"  # <- Useful for development
                    response_object = {
                        'access_token': 'INVALID',
                        'refresh_token': 'INVALID',
                        'token_type': 'Bearer',
                        'expires_in': 9000
                    }
                else:
                    # Get the User ID
                    response_user_id = json.loads(ApiAuth.get_user_id(grantee_token).read().decode('utf-8'))
                    if 'error' in response_user_id:
                        print('ERROR api.ApiHandler.directive.process.discovery.user_id:', response_user_id['error_description'])
                    user_id = response_user_id['user_id']
                    print('LOG api.ApiHandler.directive.process.discovery.user_id:', user_id)

                    # Get the Access and Refresh Tokens
                    api_auth = ApiAuth()
                    response_token = api_auth.get_access_token(grant_code, client_id, client_secret, redirect_uri)
                    response_token_string = response_token.read().decode('utf-8')
                    print('LOG api.ApiHandler.directive.process.discovery.response_token_string:', response_token_string)
                    response_object = json.loads(response_token_string)

                # Store the retrieved from the Authorization Server
                access_token = response_object['access_token']
                refresh_token = response_object['refresh_token']
                token_type = response_object['token_type']
                expires_in = response_object['expires_in']

                # Calculate expiration
                expiration_utc = datetime.utcnow() + timedelta(seconds=(int(expires_in) - 5))

                # Store the User Information - This is useful for inspection during development
                # TODO Hash User Information
                table = boto3.resource('dynamodb').Table('SampleUsers')
                result = table.put_item(
                    Item={
                        'UserId': user_id,
                        'GrantCode': grant_code,
                        'GranteeToken': grantee_token,
                        'AccessToken': access_token,
                        'ClientId': client_id,
                        'ClientSecret': client_secret,
                        'ExpirationUTC': expiration_utc.strftime("%Y-%m-%dT%H:%M:%S.00Z"),
                        'RedirectUri': redirect_uri,
                        'RefreshToken': refresh_token,
                        'TokenType': token_type
                    }
                )

                if result['ResponseMetadata']['HTTPStatusCode'] == 200:
                    print('LOG SampleUsers.put_item:', result)
                    response = AlexaAcceptGrantResponse().get_response()
                else:
                    error_message = 'Error creating User'
                    print('LOG', error_message)
                    response = AlexaError(message=error_message).get_response()

            if namespace == "Alexa.Discovery":
                # Given the Access Token, get the User ID
                access_token = json_object['directive']['payload']['scope']['token']

                # Spot the default from the Alexa.Discovery sample. Use as a default for development.
                if access_token == 'access-token-from-skill':
                    print('WARN api.ApiHandler.directive.process.discovery.user_id: Using development user_id of 0')
                    user_id = "0"  # <- Useful for development
                else:
                    response_user_id = json.loads(ApiAuth.get_user_id(access_token).read().decode('utf-8'))
                    if 'error' in response_user_id:
                        print('ERROR api.ApiHandler.directive.process.discovery.user_id: ' + response_user_id['error_description'])
                    user_id = response_user_id['user_id']
                    print('LOG api.ApiHandler.directive.process.discovery.user_id:', user_id)

                alexa_discover_response = AlexaDiscoverResponse(json_object)

                # Get the list of endpoints to return for a User ID and add them to the response
                list_response = iot_aws.list_things(attributeName='user_id', attributeValue=user_id)
                for thing in list_response['things']:
                    alexa_discover_response.add_endpoint(thing)

                response = alexa_discover_response.get_response()

            if namespace == "Alexa.PowerController":
                value = json_object['directive']['header']['name']
                correlation_token = None
                if 'correlationToken' in json_object['directive']['header']:
                    correlation_token = json_object['directive']['header']['correlationToken']
                token = json_object['directive']['endpoint']['scope']['token']
                endpoint_id = json_object['directive']['endpoint']['endpointId']

                response_user_id = json.loads(ApiAuth.get_user_id(token).read().decode('utf-8'))
                if 'error' in response_user_id:
                    print('ERROR api.ApiHandler.directive.process.power_controller.user_id: ' + response_user_id['error_description'])
                user_id = response_user_id['user_id']
                print('LOG api.ApiHandler.directive.process.power_controller.user_id', user_id)

                power_state_value = 'OFF' if value == "TurnOff" else 'ON'
                try:
                    # Send the state to the Thing
                    response_update = iot_aws.update_thing(
                        thingName=endpoint_id,
                        # thingTypeName='SearchableEndpointSwitch',
                        attributePayload={
                            'attributes': {
                                'state': power_state_value,
                                'proactively_reported': 'True',
                                'user_id': user_id
                            }
                        }
                    )
                    print('LOG api.ApiHandler.directive.process.power_controller.response_update:', response_update)
                    alexa_power_controller = AlexaPowerController(value=value, token=token, correlation_token=correlation_token, endpoint_id=endpoint_id)
                    response = alexa_power_controller.get_response()
                except ClientError as e:
                    response = AlexaError(message=e).get_response()
        else:
            response = AlexaError().get_response()

        if response is None:
            response = AlexaError(message='No response processed').get_response()
        else:
            # Validate the Response
            if not self.validate_response(response):
                response = AlexaError(message='Failed to validate message against the schema').get_response()

        print('LOG api.ApiHandler.directive.response', response)
        return json.dumps(response)

    def validate_response(self, response):
        valid = False
        try:
            with open('alexa_smart_home_message_schema.json', 'r') as schema_file:
                json_schema = json.load(schema_file)
                validate(response, json_schema)
            valid = True
        except SchemaError as se:
            print('LOG validate_response: Invalid Schema')
        except ValidationError as ve:
            print('LOG validate_response: Invalid Content for ', response)

        return valid


class _Endpoint:
    def create(self, request):
        try:
            json_object = json.loads(request['body'])
            endpoint_user_id = json_object['event']['endpoint']['userId']  # Expect a Profile
            endpoint_name = json_object['event']['endpoint']['id']  # Expect a valid AWS IoT Thing Name
            endpoint_state = json_object['event']['endpoint']['state']  # Expect a state value, ex: ON or OFF
            endpoint_type = json_object['event']['endpoint']['type']  # Expect a meaningful type, ex: SWITCH

            # TODO Add endpoint_type into the Thing by assigning a ThingType for more attribute slots

            print("LOG api.ApiHandler.endpoint.create.endpoint_name:", endpoint_name)
            print("LOG api.ApiHandler.endpoint.create.endpoint_state:", endpoint_state)

            # Create the thing
            # NOTE Hard coding the endpoints to be proactivelyReported
            try:
                response = iot_aws.create_thing(
                    thingName=endpoint_name,
                    # thingTypeName='SearchableEndpointSwitch',
                    attributePayload={
                        'attributes': {
                            'state': endpoint_state,
                            'proactively_reported': 'True',
                            'user_id': endpoint_user_id
                        }
                    }
                )
                print('LOG api.ApiHandler.endpoint.create.create_thing ' + str(response))
                return response

            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                    print('WARN iot resource already exists, trying update')
                    response = iot_aws.update_thing(
                        thingName=endpoint_name,
                        # thingTypeName='SearchableEndpointSwitch',
                        attributePayload={
                            'attributes': {
                                'state': endpoint_state,
                                'proactively_reported': 'True',
                                'user_id': endpoint_user_id
                            }
                        }
                    )
                    return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    def read(self, request):
        try:
            response = {}
            resource = request['resource']
            if resource == '/endpoints':
                list_response = iot_aws.list_things()
                status = list_response['ResponseMetadata']['HTTPStatusCode']
                if 200 <= int(status) < 300:
                    things = list_response['things']
                    response = []
                    for thing in things:
                        response.append(thing)
            else:
                path_parameters = request['pathParameters']
                endpoint_name = path_parameters['endpoint_name']
                response = iot_aws.describe_thing(thingName=endpoint_name)

            print('LOG api.ApiHandler.endpoint.read ' + str(response))
            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)


class _Event:
    def create(self, request):
        print("LOG api.ApiHandler.event.create.request:", request)

        try:
            json_object = json.loads(request['body'])
            endpoint_user_id = json_object['event']['endpoint']['userId']  # Expect a Profile
            endpoint_name = json_object['event']['endpoint']['id']  # Expect a valid AWS IoT Thing Name
            endpoint_state = json_object['event']['endpoint']['state']  # Expect a state value, ex: ON or OFF
            endpoint_type = json_object['event']['endpoint']['type']  # Expect a meaningful type, ex: SWITCH

            try:
                # Update the IoT Thing
                response = iot_aws.update_thing(
                    thingName=endpoint_name,
                    attributePayload={
                        'attributes': {
                            'state': endpoint_state,
                            'proactively_reported': 'True',
                            'user_id': endpoint_user_id
                        }
                    }
                )
                print('LOG api.ApiHandler.event.create.iot_aws.update_thing.response:', str(response))

                # Update Alexa with a Proactive State Update
                if endpoint_user_id == 0:
                    print('LOG PSU: Not sent for user_id of 0')
                else:
                    response_psu = self.send_psu(endpoint_user_id, endpoint_name, endpoint_state)
                    print('LOG PSU response:', response_psu)

            except ClientError as e:
                response = AlexaError(message=e).get_response()

            return response

        except KeyError as key_error:
            return "KeyError: " + str(key_error)

    def is_token_expired(self, expiration_utc):
        now = datetime.utcnow().replace(tzinfo=None)
        then = datetime.strptime(expiration_utc, "%Y-%m-%dT%H:%M:%S.00Z")
        is_expired = now > then
        if is_expired:
            return is_expired
        seconds = (now - then).seconds
        is_soon = seconds < 30  # Give a 30 second buffer for expiration
        return is_soon

    def send_psu(self, endpoint_user_id, endpoint_id, endpoint_state):

        # Get the User Information
        table = boto3.resource('dynamodb').Table('SampleUsers')
        result = table.get_item(
            Key={
                'UserId': endpoint_user_id
            },
            AttributesToGet=[
                'UserId',
                'AccessToken',
                'ClientId',
                'ClientSecret',
                'ExpirationUTC',
                'RedirectUri',
                'RefreshToken',
                'TokenType'
            ]
        )

        # Get the Token
        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('LOG api.ApiHandler.event.create.send_psu.SampleUsers.get_item:', str(result))

            if 'Item' in result:
                expiration_utc = result['Item']['ExpirationUTC']
                token_is_expired = self.is_token_expired(expiration_utc)
                print('LOG api.ApiHandler.event.create.send_psu.token_is_expired:', token_is_expired)
                if token_is_expired:
                    # The token has expired so get a new access token using the refresh token
                    refresh_token = result['Item']['RefreshToken']
                    client_id = result['Item']['ClientId']
                    client_secret = result['Item']['ClientSecret']
                    redirect_uri = result['Item']['RedirectUri']

                    api_auth = ApiAuth()
                    response_refresh_token = api_auth.refresh_access_token(refresh_token, client_id, client_secret, redirect_uri)
                    response_refresh_token_string = response_refresh_token.read().decode('utf-8')
                    response_refresh_token_object = json.loads(response_refresh_token_string)

                    # Store the new values from the refresh
                    access_token = response_refresh_token_object['access_token']
                    refresh_token = response_refresh_token_object['refresh_token']
                    token_type = response_refresh_token_object['token_type']
                    expires_in = response_refresh_token_object['expires_in']

                    # Calculate expiration
                    expiration_utc = datetime.utcnow() + timedelta(seconds=(int(expires_in) - 5))

                    print('access_token', access_token)
                    print('expiration_utc', expiration_utc)

                    result = table.update_item(
                        Key={
                            'UserId': endpoint_user_id
                        },
                        UpdateExpression="set AccessToken=:a, RefreshToken=:r, TokenType=:t, ExpirationUTC=:e",
                        ExpressionAttributeValues={
                            ':a': access_token,
                            ':r': refresh_token,
                            ':t': token_type,
                            ':e': expiration_utc.strftime("%Y-%m-%dT%H:%M:%S.00Z")
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                    print('LOG api.ApiHandler.event.create.send_psu.SampleUsers.update_item:', str(result))

                    # TODO Return an error here if the token could not be refreshed

                else:
                    # Use the stored access token
                    access_token = result['Item']['AccessToken']
                    print('LOG Using stored access_token:', access_token)

                alexa_change_report = AlexaChangeReport(endpoint_id=endpoint_id, token=access_token)
                payload = json.dumps(alexa_change_report.get_response())
                print('LOG AlexaChangeReport.get_response:', payload)

                # TODO Map to correct endpoint for Europe: https://api.eu.amazonalexa.com/v3/events
                # TODO Map to correct endpoint for Far East: https://api.fe.amazonalexa.com/v3/events
                alexa_event_gateway_uri = 'api.amazonalexa.com'
                connection = http.client.HTTPSConnection(alexa_event_gateway_uri)
                headers = {
                    'content-type': "application/json;charset=UTF-8",
                    'cache-control': "no-cache"
                }
                connection.request('POST', '/v3/events', payload, headers) # preload_content=False
                code = connection.getresponse().getcode()
                return 'LOG PSU HTTP Status code: ' + str(code)
