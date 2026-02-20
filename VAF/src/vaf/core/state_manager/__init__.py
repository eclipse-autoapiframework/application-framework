# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
State Manager Package

This package provides a stateless undo/redo system for file system operations
with a modular handler-based architecture.
"""

# Core system imports
from vaf.core.state_manager.state_manager import StatusQuoOrdinator
from vaf.core.state_manager.tracker import TrailSheriff

__all__ = [
    # Core system
    "TrailSheriff",
    "StatusQuoOrdinator",
]
