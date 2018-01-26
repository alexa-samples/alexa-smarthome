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

from .api_handler_directive import ApiHandlerDirective
from .api_handler_endpoint import ApiHandlerEndpoint
from .api_handler_event import ApiHandlerEvent


class ApiHandler:
    def __init__(self):
        self.directive = ApiHandlerDirective()
        self.event = ApiHandlerEvent()
        self.endpoint = ApiHandlerEndpoint()
