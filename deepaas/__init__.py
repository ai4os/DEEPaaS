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

from contextlib import suppress
# import importlib.metadata  # does not work with 3.6
from pathlib import Path

__version__ = "2.6.0"


def extract_version() -> str:
    """Returns either the version of the package installed."""
    with suppress(FileNotFoundError, StopIteration):
        root_dir = Path(__file__).parent.parent
        with open(root_dir / "pyproject.toml", encoding="utf-8") as pyproject_toml:
            version = (
                next(line for line in pyproject_toml if line.startswith("version"))
                .split("=")[1]
                .strip("'\"\n ")
            )
            return f"{version}-dev (at {root_dir})"
    # return importlib.metadata.version(__package__ or __name__.split(".", maxsplit=1)[0])
    return __version__
