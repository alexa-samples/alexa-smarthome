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

import datetime


class ApiUtils:

    @staticmethod
    def get_time_utc():
        """
        An ISO 8601 formatted string in UTC (e.g. YYYY-MM-DDThh:mm:ss.sD)
        :return: string date time
        """
        return datetime.datetime.utcnow().isoformat()
