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

"""DEEPaaS configuration.

Options are read from (in order of precedence):

1. The command line (e.g. ``--listen-port 8080``, ``--nowarm``).
2. Environment variables (e.g. ``DEEPAAS_LISTEN_PORT=8080``).
3. Configuration files, in INI format, with the options in the ``[DEFAULT]``
   section (e.g. ``listen_port = 8080``).
4. The default value of the option.

This module is compatible with the command line options, environment
variables and configuration files used by previous DEEPaaS versions, that were
based on ``oslo.config``.
"""

import argparse
import configparser
import dataclasses
import glob
import os
import textwrap
import typing
import warnings

import deepaas
from deepaas import log

warnings.simplefilter("default", DeprecationWarning)

LOG = log.getLogger(__name__)

PROJECT = "deepaas"
ENV_PREFIX = "DEEPAAS_"
# NOTE(aloga): environment variables used by oslo.config, deprecated
LEGACY_ENV_PREFIX = "OS_DEFAULT__"

_TRUE_VALUES = ("1", "true", "yes", "on", "t", "y")
_FALSE_VALUES = ("0", "false", "no", "off", "f", "n")


class ConfigError(Exception):
    """Invalid configuration."""


def _to_bool(value: str) -> bool:
    if isinstance(value, bool):
        return value
    v = str(value).strip().lower()
    if v in _TRUE_VALUES:
        return True
    if v in _FALSE_VALUES:
        return False
    raise ValueError(f"'{value}' is not a valid boolean value")


@dataclasses.dataclass
class Opt:
    """A configuration option.

    :param name: name of the option, as used in the command line (without the
        leading dashes). Dashes are converted to underscores to get the name
        used in the configuration files and to access its value.
    :param type: type of the option (``str``, ``int`` or ``bool``).
    :param default: default value.
    :param help: help message.
    :param short: short command line option (a single letter), if any.
    :param choices: valid values, if restricted.
    :param min: minimum value, for integers.
    :param max: maximum value, for integers.
    :param secret: whether the value must be hidden in the logs.
    :param deprecated_reason: if set, the option is deprecated.
    :param env: additional (legacy) environment variables to read the option
        from.
    """

    name: str
    type: type = str
    default: typing.Any = None
    help: str = ""
    short: typing.Optional[str] = None
    choices: typing.Optional[typing.Sequence] = None
    min: typing.Optional[int] = None
    max: typing.Optional[int] = None
    secret: bool = False
    deprecated_reason: typing.Optional[str] = None
    env: typing.Sequence[str] = ()

    @property
    def dest(self) -> str:
        return self.name.replace("-", "_")

    @property
    def env_vars(self) -> typing.List[str]:
        return [ENV_PREFIX + self.dest.upper(), *self.env]

    def convert(self, value: typing.Any) -> typing.Any:
        """Convert a value (e.g. a string) to the type of the option.

        :raises ValueError: if the value is not valid.
        """
        if self.type is bool:
            value = _to_bool(value)
        elif self.type is int:
            value = int(value)
            if self.min is not None and value < self.min:
                raise ValueError(f"{value} is lower than {self.min}")
            if self.max is not None and value > self.max:
                raise ValueError(f"{value} is greater than {self.max}")
        else:
            value = str(value)

        if self.choices is not None and value not in self.choices:
            raise ValueError(
                f"'{value}' is not one of {', '.join(map(str, self.choices))}"
            )
        return value


def PortOpt(name, **kwargs):  # noqa: N802
    """An integer option holding a TCP port number."""
    return Opt(name, type=int, min=0, max=65535, **kwargs)


class Config(object):
    """Hold the configured values, accessible as attributes."""

    def __init__(self):
        self._opts = {}

    def register_opts(self, opts: typing.Iterable[Opt]) -> None:
        """Register options, setting them to their default value."""
        for opt in opts:
            if opt.dest in self._opts:
                continue
            self._opts[opt.dest] = opt
            setattr(self, opt.dest, opt.default)

    @property
    def opts(self) -> typing.List[Opt]:
        return list(self._opts.values())

    def reset(self) -> None:
        """Set all the options to their default values."""
        for opt in self._opts.values():
            setattr(self, opt.dest, opt.default)


def _get_default_config_dirs(project=PROJECT):
    dirs = [
        os.path.join("~", "." + project),
        "~",
        os.path.join("/etc", project),
        "/etc",
    ]
    return [os.path.expanduser(d) for d in dirs]


def find_config_files(project=PROJECT, prog=None):
    """Find the default configuration files.

    As in previous versions, we look for ``<project>.conf`` and ``<prog>.conf``
    in ``~/.<project>/``, ``~/``, ``/etc/<project>/`` and ``/etc/``, using the
    first one found for each.
    Moreover, all the ``*.conf`` files in the ``<project>.conf.d`` directories
    in the same locations are also read.
    """
    names = [f"{project}.conf"]
    if prog and prog != project:
        names.append(f"{prog}.conf")

    dirs = _get_default_config_dirs(project)
    files = []
    for name in names:
        for d in dirs:
            path = os.path.join(d, name)
            if os.path.isfile(path):
                files.append(path)
                break

    for d in dirs:
        conf_d = os.path.join(d, f"{project}.conf.d")
        if os.path.isdir(conf_d):
            files.extend(sorted(glob.glob(os.path.join(conf_d, "*.conf"))))
    return files


def _read_config_files(files):
    """Read the [DEFAULT] section of the given INI files.

    Later files override the values of former ones.
    """
    values = {}
    for path in files:
        parser = configparser.ConfigParser(interpolation=None)
        try:
            with open(path) as f:
                parser.read_file(f)
        except (OSError, configparser.Error) as e:
            raise ConfigError(f"Cannot read configuration file {path}: {e}")
        for key, value in parser.defaults().items():
            values[key.replace("-", "_")] = (value, path)
    return values


def add_arguments(parser: argparse.ArgumentParser, opts: typing.Iterable[Opt]):
    """Add the configuration options to an argparse parser.

    Boolean options get two flags: ``--<name>`` to enable them and
    ``--no<name>`` to disable them (as with oslo.config).
    """
    parser.add_argument(
        "--config-file",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "Path to a configuration file to use. Multiple files can be "
            "specified, with values in later files taking precedence. "
            "Defaults to the first deepaas.conf found in ~/.deepaas/, ~/, "
            "/etc/deepaas/ or /etc/."
        ),
    )
    parser.add_argument(
        "--config-dir",
        action="append",
        default=None,
        metavar="DIR",
        help=(
            "Path to a directory with configuration files (*.conf), that "
            "are read in alphabetical order after the --config-file files."
        ),
    )
    parser.add_argument(
        "--version", action="version", version=deepaas.extract_version()
    )

    for opt in opts:
        help_ = " ".join(opt.help.split())
        if opt.deprecated_reason:
            help_ = f"DEPRECATED: {help_} {opt.deprecated_reason}"

        if opt.type is bool:
            group = parser.add_mutually_exclusive_group()
            flags = [f"--{opt.name}"]
            if opt.short:
                flags.append(f"-{opt.short}")
            group.add_argument(
                *flags,
                dest=opt.dest,
                action="store_const",
                const=True,
                default=None,
                help=f"{help_} (default: {opt.default})",
            )
            group.add_argument(
                f"--no{opt.name}",
                dest=opt.dest,
                action="store_const",
                const=False,
                default=None,
                help=f"The inverse of --{opt.name}.",
            )
        else:
            flags = [f"--{opt.name}"]
            if opt.short:
                flags.append(f"-{opt.short}")

            def _type(value, opt=opt):
                try:
                    return opt.convert(value)
                except ValueError as e:
                    raise argparse.ArgumentTypeError(str(e))

            default_help = "" if opt.secret else f" (default: {opt.default!r})"
            parser.add_argument(
                *flags,
                dest=opt.dest,
                type=_type,
                default=None,
                metavar=opt.dest.upper(),
                help=f"{help_}{default_help}",
            )


def build_parser(opts=None, prog=None, **kwargs) -> argparse.ArgumentParser:
    """Build a command line parser for the given (or all registered) options."""
    if opts is None:
        opts = CONF.opts
    parser = argparse.ArgumentParser(prog=prog, **kwargs)
    add_arguments(parser, opts)
    return parser


def load(namespace, opts=None, default_config_files=None, prog=None):
    """Set the configuration from parsed command line arguments.

    :param namespace: the result of parsing the command line with a parser
        built with :py:func:`build_parser` or :py:func:`add_arguments`.
    :param opts: options to load (by default, all registered options).
    :param default_config_files: configuration files to read if none is
        given in the command line. If ``None``, the default locations are
        searched.
    :raises ConfigError: if the configuration is not valid.
    """
    if opts is None:
        opts = CONF.opts

    config_files = getattr(namespace, "config_file", None)
    if config_files:
        missing = [f for f in config_files if not os.path.isfile(f)]
        if missing:
            raise ConfigError(f"Failed to find some config files: {', '.join(missing)}")
    elif default_config_files is not None:
        config_files = list(default_config_files)
    else:
        config_files = find_config_files(prog=prog)

    for d in getattr(namespace, "config_dir", None) or []:
        if not os.path.isdir(d):
            raise ConfigError(f"Config directory {d} not found")
        config_files.extend(sorted(glob.glob(os.path.join(d, "*.conf"))))

    file_values = _read_config_files(config_files)

    for opt in opts:
        value = getattr(namespace, opt.dest, None)
        source = "command line"
        if value is None:
            value, source = _get_from_environment(opt)
        if value is None and opt.dest in file_values:
            value, source = file_values[opt.dest]
        if value is None:
            value, source = opt.default, None
        elif source != "command line":
            try:
                value = opt.convert(value)
            except ValueError as e:
                raise ConfigError(f"Invalid value for '{opt.dest}' in {source}: {e}")

        if source is not None and opt.deprecated_reason:
            warnings.warn(
                f"Option '{opt.dest}' is deprecated: {opt.deprecated_reason}",
                DeprecationWarning,
                stacklevel=2,
            )
        setattr(CONF, opt.dest, value)

    return CONF


def _get_from_environment(opt):
    for var in opt.env_vars:
        if var in os.environ:
            return os.environ[var], f"environment variable {var}"

    var = LEGACY_ENV_PREFIX + opt.dest.upper()
    if var in os.environ:
        warnings.warn(
            f"The environment variable {var} is deprecated, use "
            f"{opt.env_vars[0]} instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return os.environ[var], f"environment variable {var}"
    return None, None


def generate_sample(opts=None) -> str:
    """Generate a sample configuration file for the given options."""
    if opts is None:
        opts = CONF.opts

    lines = ["[DEFAULT]", ""]
    for opt in opts:
        help_ = " ".join(opt.help.split())
        lines.extend("# " + line for line in textwrap.wrap(help_, 77))
        meta = [f"{opt.type.__name__} value"]
        if opt.choices:
            meta.append(f"allowed values: {', '.join(map(str, opt.choices))}")
        if opt.min is not None:
            meta.append(f"minimum value: {opt.min}")
        if opt.max is not None:
            meta.append(f"maximum value: {opt.max}")
        lines.append(f"# ({'; '.join(meta)})")
        lines.append(f"# Environment variable: {opt.env_vars[0]}")
        if opt.deprecated_reason:
            lines.append(f"# DEPRECATED: {opt.deprecated_reason}")
        default = opt.default
        if isinstance(default, bool):
            default = str(default).lower()
        lines.append(f"#{opt.dest} = {default if default is not None else '<None>'}")
        lines.append("")
    return "\n".join(lines)


opts = [
    Opt(
        "debug-endpoint",
        type=bool,
        default=False,
        help="""
Enable debug endpoint. If set we will provide all the information that you
print to the standard output and error (i.e. stdout and stderr) through the
"/debug" endpoint. Default is to not provide this information. This will not
provide logging information about the API itself.
""",
    ),
    Opt(
        "doc-endpoint",
        type=bool,
        default=True,
        help="""
Enable documentation endpoints. If set we will provide the documentation
through the "/docs" (Swagger UI) and "/redoc" (ReDoc) endpoints. Default is to
provide this information.
""",
    ),
    Opt(
        "workers",
        type=int,
        short="p",
        default=1,
        min=1,
        help="""
Maximum number of predictions that are executed at the same time. Further
requests wait until a prediction finishes. Most models are not thread safe, or
cannot hold several predictions in memory (e.g. in a GPU), so leave it to 1
unless you know that your model supports concurrent predictions. (defaults to
1)
""",
    ),
    Opt(
        "client-max-size",
        type=int,
        default=0,
        min=0,
        deprecated_reason="This option is ignored since DEEPaaS 3.0.0.",
        help="""
Client's maximum size in a request, in bytes. If a POST request exceeds this
value, it raises an HTTPRequestEntityTooLarge exception. If set to 0, no
file size limit will be enforced.
""",
    ),
    Opt(
        "warm",
        type=bool,
        default=True,
        help="""
Pre-warm the modules (eg. load models, do preliminary checks, etc). You might
want to disable this option if DEEPaaS is loading more than one module because
you risk getting out of memory errors.
""",
    ),
    Opt(
        "model-name",
        default="",
        env=("DEEPAAS_V2_MODEL",),
        help="""
Specify the model to be used. If not specified, DEEPaaS will fail if there are
more than only one models available.
""",
    ),
    Opt(
        "debug",
        type=bool,
        short="d",
        default=False,
        help="""
Enable debug mode in logging. This will provide more information about what
is happening in the API. Default is to not provide this information.
""",
    ),
    Opt(
        "log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="""
Specify the log level for the API. Default is INFO. Possible values are DEBUG,
INFO, WARNING, ERROR, CRITICAL.
""",
    ),
    Opt(
        "log-file",
        default="",
        help="""
Specify the log file to use. If not specified, logs will be sent to stdout.
""",
    ),
    Opt(
        "auth-bearer-token",
        default="",
        secret=True,
        help="""
Bearer token for API authentication. If set, the model endpoints (including
predictions) and the debug endpoint will require an
'Authorization: Bearer <token>' header. If not set, authentication is
disabled. Avoid passing it in the command line, as it will be visible in the
process list: use a configuration file or the DEEPAAS_AUTH_BEARER_TOKEN
environment variable instead.
""",
    ),
]

CONF = Config()
CONF.register_opts(opts)


def parse_args(argv, default_config_files=None, prog=None):
    """Parse the command line and load the configuration.

    :param argv: the command line, including the program name.
    """
    prog = prog or (os.path.basename(argv[0]) if argv else None)
    parser = build_parser(prog=prog)
    namespace = parser.parse_args(argv[1:])
    try:
        load(namespace, default_config_files=default_config_files, prog=prog)
    except ConfigError as e:
        parser.error(str(e))
    return namespace


def setup(argv, default_config_files=None):
    parse_args(argv, default_config_files=default_config_files)

    log_level = (CONF.debug and "DEBUG") or CONF.log_level

    log.setup(log_level, CONF.log_file)
