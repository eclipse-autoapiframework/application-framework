# ruff: noqa: F401
"""Initialize the module.

Could be used to define the public interface of the module.
"""

# TODO: Import modules and objects that belong to the public interface  # pylint: disable=W0511
from vaf.core.common.exceptions import VafProjectTemplateError

# VAFPY is accessable through VAFCLI
from vaf.vafpy import *  # noqa: F403
