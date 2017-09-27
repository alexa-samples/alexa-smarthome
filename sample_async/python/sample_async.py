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

"""Alexa Smart Home Asynchronous Messaging Sample Code.

This file demonstrates some key concepts when working with the Alexa Smart Home, as well as
Login with Amazon (LWA) in order to establish authentication and authorization, so your skill
can send proactive state updates and change reports to Alexa on behalf of the customer.

This sample stores access and refresh tokens in a file, and shows the flow for requesting a new
access token and refreshing existing and/or expired access tokens. It also shows how to use a valid
access token to send a proactive change or state report. You would ideally store access and
refresh tokens in a more appropriate persistence like DynamoDB.

Basic usage of this file is as follows:

1. fill in the CLIENT_ID and CLIENT_SECRET constants
2. with a user in the Alexa App, enable your skill, and receive an AcceptGrant directive
3. get the auth code from that AcceptGrant directive, and fill in the CODE constant
4. update main() with a change or state report that is appropriate for your user and skill
5. run this file and see how it works for the first time
6. change PREEMPTIVE_REFRESH_TTL_IN_SECONDS to a large number to force token refresh as needed
"""

import logging
import sys
import time
import datetime
import json
import uuid
import os
import requests

# constants
UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.00Z"
LWA_TOKEN_URI = "https://api.amazon.com/auth/o2/token"
LWA_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
}
ALEXA_URI = "https://api.amazonalexa.com/v3/events" # update to appropriate URI for your region
ALEXA_HEADERS = {
    "Content-Type": "application/json;charset=UTF-8"
}

# setup logger
logging.basicConfig(stream=sys.stdout)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

# LWA constants
CODE = "<code>" # auth code from AcceptGrant directive, update whenever you disable/enable the skill
CLIENT_ID = "<client id>" # copy from Developer Console
CLIENT_SECRET = "<client secret>" # copy from Developer Console
PREEMPTIVE_REFRESH_TTL_IN_SECONDS = 300 # used to preemptively refresh access token if 5 mins from expiry

TOKEN_FILENAME = CODE + ".txt" # everytime a new auth code is used, we store tokens in a new file

# utility functions
def get_utc_timestamp(seconds=None):
    return time.strftime(UTC_FORMAT, time.gmtime(seconds))

def get_utc_timestamp_from_string(string):
    return datetime.datetime.strptime(string, UTC_FORMAT)

def get_uuid():
    return str(uuid.uuid4())

# authentication functions
def get_need_new_token():
    """Checks whether the access token is missing or needed to be refreshed"""
    need_new_token_response = {
        "need_new_token": False,
        "access_token": "",
        "refresh_token": ""
    }

    if os.path.isfile(TOKEN_FILENAME):
        # if token file exists, then we've already gotten the first access token for this user skill enablement
        with open(TOKEN_FILENAME, 'r') as infile:
            last_line = infile.readlines()[-1] # THIS IS TOTALLY INEFFICIENT

        token = last_line.split("***")
        token_received_datetime = get_utc_timestamp_from_string(token[0])
        token_json = json.loads(token[1])
        token_expires_in = token_json["expires_in"] - PREEMPTIVE_REFRESH_TTL_IN_SECONDS
        token_expires_datetime = token_received_datetime + datetime.timedelta(seconds=token_expires_in)
        current_datetime = datetime.datetime.utcnow()

        need_new_token_response["need_new_token"] = current_datetime > token_expires_datetime
        need_new_token_response["access_token"] = token_json["access_token"]
        need_new_token_response["refresh_token"] = token_json["refresh_token"]
    else:
        # else, we've never gotten an access token for this user skill enablement
        need_new_token_response["need_new_token"] = True

    return need_new_token_response

def get_access_token():
    """Performs access token or token refresh request as needed and returns valid access token"""

    need_new_token_response = get_need_new_token()
    access_token = ""

    if need_new_token_response["need_new_token"]:
        if os.path.isfile(TOKEN_FILENAME):
            # access token already retrieved the first time, so this should be a token refresh request
            with open(TOKEN_FILENAME, 'a') as outfile:
                outfile.write("\n")

            lwa_params = {
                "grant_type" : "refresh_token",
                "refresh_token": need_new_token_response["refresh_token"],
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
            LOGGER.debug("Calling LWA to refresh the access token...")
        else:
            # access token not retrieved yet for the first time, so this should be an access token request
            lwa_params = {
                "grant_type" : "authorization_code",
                "code": CODE,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
            LOGGER.debug("Calling LWA to get the access token for the first time...")
            LOGGER.debug("Params: " + json.dumps(lwa_params))

        response = requests.post(LWA_TOKEN_URI, headers=LWA_HEADERS, data=lwa_params, allow_redirects=True)
        LOGGER.debug("LWA response header: " + format(response.headers))
        LOGGER.debug("LWA response status: " + format(response.status_code))
        LOGGER.debug("LWA response body  : " + format(response.text))

        if response.status_code != 200:
            LOGGER.debug("Error calling LWA!")
            return None

        # store token in file
        token = get_utc_timestamp() + "***" + response.text
        with open(TOKEN_FILENAME, 'a') as outfile:
            outfile.write(token)

        access_token = json.loads(response.text)["access_token"]
    else:
        LOGGER.debug("Latest access token has not expired, so using it and won't call LWA...")
        access_token = need_new_token_response["access_token"]

    return access_token

def main():
    """Main function that sends a proactive state or change report to Alexa"""

    token = get_access_token()

    if token:
        message_id = get_uuid()
        time_of_sample = get_utc_timestamp()

        # ensure that this change or state report is appropriate for your user and skill
        alexa_params = {
            "context": {
                "properties": [{
                    "namespace": "Alexa.BrightnessController",
                    "name": "brightness",
                    "value": 99,
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 500
                }, {
                    "namespace": "Alexa.ColorController",
                    "name": "color",
                    "value": {
                        "hue": 350.5,
                        "saturation": 0.7138,
                        "brightness": 0.6524
                    },
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 500
                }, {
                    "namespace": "Alexa.ColorTemperatureController",
                    "name": "colorTemperatureInKelvin",
                    "value": 7500,
                    "timeOfSample": time_of_sample,
                    "uncertaintyInMilliseconds": 500
                }]
            },
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "ChangeReport",
                    "payloadVersion": "3",
                    "messageId": message_id
                },
                "endpoint": {
                    "scope": {
                        "type": "BearerToken",
                        "token": token
                    },
                    "endpointId": "appliance-002"
                },
                "payload": {
                    "change": {
                        "cause": {
                            "type": "ALEXA_INTERACTION"
                        }
                    },
                    "properties": [{
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": "ON",
                        "timeOfSample": time_of_sample,
                        "uncertaintyInMilliseconds": 500
                    }]
                }
            }
        }

        response = requests.post(ALEXA_URI, headers=ALEXA_HEADERS, data=json.dumps(alexa_params), allow_redirects=True)
        LOGGER.debug("Request data: " + json.dumps(alexa_params))
        LOGGER.debug("Alexa response header: " + format(response.headers))
        LOGGER.debug("Alexa response status: " + format(response.status_code))
        LOGGER.debug("Alexa response body  : " + format(response.text))

if __name__ == "__main__":
    main()
