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
import http.client
import json

from .api_auth import ApiAuth
from alexa.skills.smarthome import AlexaResponse
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

dynamodb_aws = boto3.client('dynamodb')
iot_aws = boto3.client('iot')


class ApiHandlerEvent:
    def create(self, request):
        print("LOG event.create.request:", request)

        try:
            json_object = json.loads(request['body'])
            endpoint_user_id = json_object['event']['endpoint']['userId']  # Expect a Profile
            endpoint_name = json_object['event']['endpoint']['id']  # Expect a valid AWS IoT Thing Name
            endpoint_state = json_object['event']['endpoint']['state']  # Expect a state value, ex: ON or OFF
            sku = json_object['event']['endpoint']['sku']  # Expect a meaningful type, ex: SW00

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
                print('LOG event.create.iot_aws.update_thing.response:', str(response))

                # Update Alexa with a Proactive State Update
                if endpoint_user_id == 0:
                    print('LOG PSU: Not sent for user_id of 0')
                else:
                    response_psu = self.send_psu(endpoint_user_id, endpoint_name, endpoint_state)
                    print('LOG PSU response:', response_psu)

            except ClientError as e:
                alexa_response = AlexaResponse(name='ErrorResponse', message=e)
                alexa_response.set_payload(
                    {
                        'type': 'INTERNAL_ERROR',
                        'message': e
                    }
                )
                response = alexa_response.get()

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

        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('LOG event.create.send_psu.SampleUsers.get_item:', str(result))

            if 'Item' in result:
                expiration_utc = result['Item']['ExpirationUTC']
                token_is_expired = self.is_token_expired(expiration_utc)
                print('LOG event.create.send_psu.token_is_expired:', token_is_expired)
                if token_is_expired:
                    # The token has expired so get a new access token using the refresh token
                    refresh_token = result['Item']['RefreshToken']
                    client_id = result['Item']['ClientId']
                    client_secret = result['Item']['ClientSecret']
                    redirect_uri = result['Item']['RedirectUri']

                    api_auth = ApiAuth()
                    response_refresh_token = api_auth.refresh_access_token(refresh_token, client_id, client_secret,
                                                                           redirect_uri)
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
                    print('LOG event.create.send_psu.SampleUsers.update_item:', str(result))

                    # TODO Return an error here if the token could not be refreshed
                else:
                    # Use the stored access token
                    access_token = result['Item']['AccessToken']
                    print('LOG Using stored access_token:', access_token)

                alexa_changereport_response = AlexaResponse(name='ChangeReport', endpoint_id=endpoint_id, token=access_token)
                alexa_changereport_response.set_payload(
                    {
                        'change': {
                            'cause': {
                                'type': 'PHYSICAL_INTERACTION'
                            },
                            "properties": [
                                alexa_changereport_response.create_property(namespace='Alexa.PowerController', name='powerState', value='ON')
                            ]
                        }
                    }
                )
                payload = json.dumps(alexa_changereport_response.get())
                print('LOG AlexaChangeReport.get_response:', payload)

                # TODO Map to correct endpoint for Europe: https://api.eu.amazonalexa.com/v3/events
                # TODO Map to correct endpoint for Far East: https://api.fe.amazonalexa.com/v3/events
                alexa_event_gateway_uri = 'api.amazonalexa.com'
                connection = http.client.HTTPSConnection(alexa_event_gateway_uri)
                headers = {
                    'content-type': "application/json;charset=UTF-8",
                    'cache-control': "no-cache"
                }
                connection.request('POST', '/v3/events', payload, headers)
                code = connection.getresponse().getcode()
                return 'LOG PSU HTTP Status code: ' + str(code)
