# ruff: noqa: F401
"""Initialize the module.

Could be used to define the public interface of the module.
"""

# Import modules and objects that belong to the public interface  # pylint: disable=W0511
__all__ = ["ifex_batch_to_json"]
from .converter import ifex_batch_to_json
