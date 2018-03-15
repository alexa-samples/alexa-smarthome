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

import boto3
import json

from .api_auth import ApiAuth
from .api_handler_endpoint import ApiHandlerEndpoint
from alexa.skills.smarthome import AlexaDiscoverResponse, AlexaResponse
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from jsonschema import validate, SchemaError, ValidationError

dynamodb_aws = boto3.client('dynamodb')
iot_aws = boto3.client('iot')


class ApiHandlerDirective:

    @staticmethod
    def get_db_value(value):
        if 'S' in value:
            value = value['S']
        return value

    def process(self, request, client_id, client_secret, redirect_uri):
        print('LOG directive.process.request:', request)

        response = None
        # Process an Alexa directive and route to the right namespace
        # Only process if there is an actual body to process otherwise return an ErrorResponse
        json_body = request['body']
        if json_body:
            json_object = json.loads(json_body)
            namespace = json_object['directive']['header']['namespace']

            if namespace == "Alexa":
                name = json_object['directive']['header']['name']
                correlation_token = json_object['directive']['header']['correlationToken']
                endpoint_id = json_object['directive']['endpoint']['endpointId']
                if name == 'ReportState':
                    # TODO Get the User ID from the access_token
                    # TODO Lookup the endpoint and get state
                    print('Sending StateReport for endpoint', endpoint_id)
                    alexa_reportstate_response = AlexaResponse(name='StateReport', endpoint_id=endpoint_id, correlation_token=correlation_token)
                    response = alexa_reportstate_response.get()

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
                        print('ERROR directive.process.authorization.user_id:', response_user_id['error_description'])
                    user_id = response_user_id['user_id']
                    print('LOG directive.process.authorization.user_id:', user_id)

                    # Get the Access and Refresh Tokens
                    api_auth = ApiAuth()
                    response_token = api_auth.get_access_token(grant_code, client_id, client_secret, redirect_uri)
                    response_token_string = response_token.read().decode('utf-8')
                    print('LOG directive.process.authorization.response_token_string:', response_token_string)
                    response_object = json.loads(response_token_string)

                # Store the retrieved from the Authorization Server
                access_token = response_object['access_token']
                refresh_token = response_object['refresh_token']
                token_type = response_object['token_type']
                expires_in = response_object['expires_in']

                # Calculate expiration
                expiration_utc = datetime.utcnow() + timedelta(seconds=(int(expires_in) - 5))

                # Store the User Information - This is useful for inspection during development
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
                    print('LOG directive.process.authorization.SampleUsers.put_item:', result)
                    alexa_accept_grant_response = AlexaResponse(namespace='Alexa.Authorization', name='AcceptGrant.Response')
                    response = alexa_accept_grant_response.get()

                else:
                    error_message = 'Error creating User'
                    print('ERR directive.process.authorization', error_message)
                    alexa_error_response = AlexaResponse(name='ErrorResponse')
                    alexa_error_response.set_payload({'type': 'INTERNAL_ERROR', 'message': error_message})
                    response = alexa_error_response.get()

            if namespace == "Alexa.Cooking":
                name = json_object['directive']['header']['name']
                correlation_token = json_object['directive']['header']['correlationToken']
                token = json_object['directive']['endpoint']['scope']['token']
                endpoint_id = json_object['directive']['endpoint']['endpointId']
                if name == "SetCookingMode":
                    alexa_error_response = AlexaResponse(endpoint_id=endpoint_id, correlation_token=correlation_token, token=token)
                    response = alexa_error_response.get()

            if namespace == "Alexa.Discovery":
                # Given the Access Token, get the User ID
                access_token = json_object['directive']['payload']['scope']['token']

                # Spot the default from the Alexa.Discovery sample. Use as a default for development.
                if access_token == 'access-token-from-skill':
                    print('WARN directive.process.discovery.user_id: Using development user_id of 0')
                    user_id = "0"  # <- Useful for development
                else:
                    response_user_id = json.loads(ApiAuth.get_user_id(access_token).read().decode('utf-8'))
                    if 'error' in response_user_id:
                        print('ERROR directive.process.discovery.user_id: ' + response_user_id['error_description'])
                    user_id = response_user_id['user_id']
                    print('LOG directive.process.discovery.user_id:', user_id)

                alexa_discover_response = AlexaDiscoverResponse(json_object)

                # Get the list of endpoints to return for a User ID and add them to the response
                # Use the AWS IoT entries for state but get the discovery details from DynamoDB
                # HACK Boto3 1.4.8 attributeName and attributeValue stopped working, raw list_things() works however
                # Not Working: list_response = iot_aws.list_things(attributeName='user_id', attributeValue=user_id)
                list_response = iot_aws.list_things()
                for thing in list_response['things']:
                    if 'user_id' in thing['attributes']:
                        if thing['attributes']['user_id'] == user_id:
                            endpoint_details = ApiHandlerEndpoint.EndpointDetails()
                            endpoint_details.id = str(thing['thingName'])  # Add attribute endpoint_id to free thingName?
                            print('LOG directive.process.discovery: Found:', endpoint_details.id, 'for user:', user_id)
                            result = dynamodb_aws.get_item(TableName='SampleEndpointDetails', Key={'EndpointId': {'S': endpoint_details.id}})
                            capabilities_string = self.get_db_value(result['Item']['Capabilities'])
                            endpoint_details.capabilities = json.loads(capabilities_string)
                            endpoint_details.description = self.get_db_value(result['Item']['Description'])
                            endpoint_details.display_categories = json.loads(self.get_db_value(result['Item']['DisplayCategories']))
                            endpoint_details.friendly_name = self.get_db_value(result['Item']['FriendlyName'])
                            endpoint_details.manufacturer_name = self.get_db_value(result['Item']['ManufacturerName'])
                            endpoint_details.sku = self.get_db_value(result['Item']['SKU'])
                            endpoint_details.user_id = self.get_db_value(result['Item']['UserId'])
                            alexa_discover_response.add_endpoint(endpoint_details)

                response = alexa_discover_response.get_response()

            if namespace == "Alexa.PowerController":
                name = json_object['directive']['header']['name']
                correlation_token = None
                if 'correlationToken' in json_object['directive']['header']:
                    correlation_token = json_object['directive']['header']['correlationToken']
                token = json_object['directive']['endpoint']['scope']['token']
                endpoint_id = json_object['directive']['endpoint']['endpointId']

                response_user_id = json.loads(ApiAuth.get_user_id(token).read().decode('utf-8'))
                if 'error' in response_user_id:
                    print('ERROR directive.process.power_controller.user_id: ' + response_user_id['error_description'])
                user_id = response_user_id['user_id']
                print('LOG directive.process.power_controller.user_id', user_id)

                # Convert to a local stored state
                power_state_value = 'OFF' if name == "TurnOff" else 'ON'
                try:
                    # Send the state to the Thing
                    response_update = iot_aws.update_thing(
                        thingName=endpoint_id,
                        attributePayload={
                            'attributes': {
                                'state': power_state_value,
                                'user_id': user_id
                            }
                        }
                    )
                    print('LOG directive.process.power_controller.response_update:', response_update)
                    alexa_power_controller_response = AlexaResponse(
                        token=token,
                        correlation_token=correlation_token,
                        endpoint_id=endpoint_id)

                    alexa_power_controller_response.add_property(
                        namespace='Alexa.PowerController',
                        name='powerState',
                        value=power_state_value)

                    alexa_power_controller_response.add_property()

                    response = alexa_power_controller_response.get()

                except ClientError as e:
                    response = AlexaResponse(name='ErrorResponse', message=e).get()

        else:
            response = AlexaResponse(name='ErrorResponse').get()

        if response is None:
            # response set to None indicates an unhandled directive, review the logs
            response = AlexaResponse(name='ErrorResponse', message='Empty Response: No response processed').get()
        # else:
            # TODO Validate the Response once the schema is updated
            # if not self.validate_response(response):
            #     response = AlexaError(message='Failed to validate message against the schema').get_response()

        # print('LOG directive.process.response', response)
        return json.dumps(response)

    @staticmethod
    def validate_response(response):
        valid = False
        try:
            with open('alexa_smart_home_message_schema.json', 'r') as schema_file:
                json_schema = json.load(schema_file)
                validate(response, json_schema)
            valid = True
        except SchemaError as se:
            print('LOG directive.validate_response: Invalid Schema')
        except ValidationError as ve:
            print('LOG directive.validate_response: Invalid Content for ', response)

        return valid

