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

import sys

import mock

from deepaas.cmd import run
from deepaas.tests import base


class TestRun(base.TestCase):
    @mock.patch("deepaas.api.get_app")
    def test_run(self, mock_get_app):
        m = mock.MagicMock()
        mock_get_app.return_value = m
        with mock.patch.object(sys, 'argv', ["deepaas-run"]):
            run.main()
        mock_get_app.assert_called_once()
        m.run.assert_called_with(host="127.0.0.1",
                                 port=5000,
                                 debug=mock.ANY)

    @mock.patch("deepaas.api.get_app")
    def test_run_custom_ip_port(self, mock_get_app):
        m = mock.MagicMock()
        mock_get_app.return_value = m
        ip = "1.1.1.1"
        port = 1234
        self.flags(listen_ip=ip)
        self.flags(listen_port=port)
        with mock.patch.object(sys, 'argv', ["deepaas-run"]):
            run.main()
        mock_get_app.assert_called_once()
        m.run.assert_called_with(host=ip,
                                 port=port,
                                 debug=mock.ANY)
