# -*- coding: utf-8 -*-

# Copyright 2021 Spanish National Research Council (CSIC)
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

import dask.distributed
from oslo_config import cfg
from oslo_log import log

LOG = log.getLogger(__name__)

CONF = cfg.CONF


def get_default_executor():
    return LocalDaskExecutor()


class Executor:
    def __repr__(self) -> str:
        return "<Executor: {}>".format(type(self).__name__)

    def submit(self, fn, *args, extra_context=None, **kwargs):
        """Submit a function to the executor for execution.

        :param fn: function that is being submitted for execution
        :param *args: arguments to be passed to `fn`
        :param extra_context: an optional dictionary with extra information
            about the submitted task
        :param **kwargs: keyword arguments to be passed to `fn`

        :returns: a future-like object
        """
        raise NotImplementedError()

    def shutdown(self):
        """Shut down the executor."""
        raise NotImplementedError()


class LocalDaskExecutor(Executor):
    def __init__(self):
        config = {
            "temporary-directory": "/tmp/",
        }
        paths = CONF.dask_config
        if paths:
            tmp_conf = dask.config.collect(paths=paths)
        else:
            tmp_conf = dask.config.collect()
        config.update(tmp_conf)
        dask.config.set(config)

        self.client = dask.distributed.Client(
            asynchronous=True,
        )
        super().__init__()

    def submit(self, fn, *args, **kwargs):
        """FIXME(aloga): document this."""

        fut = self.client.submit(fn, *args, **kwargs)
        return fut

    def shutdown():
        self.client.shutdown()
