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


class ApiResponseBody:

    def __init__(self, **kwargs):
        self.body = {}
        self.result = kwargs.get('result', "OK")
        self.message = kwargs.get('message', "")

    def __repr__(self):
        return self.create()

    def create(self):
        self.body['result'] = self.result
        if self.message:  # Check for an empty message
            self.body['message'] = self.message

        return json.dumps(self.body)

