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

from .api_response_body import ApiResponseBody


class ApiResponse:

    def __init__(self, **kwargs):
        self.isBase64Encoded = kwargs.get('isBase64Encoded', False)
        self.statusCode = kwargs.get('statusCode', 200)
        self.headers = {}
        self.body = ApiResponseBody()
        self.response = {}

    def __repr__(self):
        return self.create()

    def create(self):
        self.headers['Content-Type'] = 'application/json'

        self.response['isBase64Encoded'] = str(self.isBase64Encoded)
        self.response['statusCode'] = str(self.statusCode)
        self.response['headers'] = self.headers
        self.response['body'] = str(self.body)

        return self.response
