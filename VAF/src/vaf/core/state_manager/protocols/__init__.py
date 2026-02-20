# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Abstracts Package

This package contains abstract definitions and protocols for the state manager system.
It provides structural typing and decouples components to avoid circular dependencies.
"""

from .protocols import DeltaTypeProtocol, FileDeltaInterface, RunCopyCallableProtocol

__all__ = [
    "FileDeltaInterface",
    "DeltaTypeProtocol",
    "RunCopyCallableProtocol",
]
