# -*- coding: utf-8 -*-

# Copyright 2018 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from deepaas.cmd import run
from deepaas.tests import base


class TestRun(base.TestCase):
    @mock.patch("deepaas.api.get_app")
    def test_run(self, mock_get_app):
        m = mock.MagicMock()
        mock_get_app.return_value = m
        run.main()
        mock_get_app.assert_called_once()
        m.run.assert_called_with(host="0.0.0.0", debug=mock.ANY)
