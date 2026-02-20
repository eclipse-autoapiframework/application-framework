# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Data Handlers Package

This package contains handlers for file, directory, and symlink operations.
These handlers are responsible for applying and validating file system deltas
in the stateless undo/redo system.
"""

from .dir_handlers import DirCreateHandler, DirDeleteHandler
from .file_handlers import FileCreateHandler, FileDeleteHandler, FileModifyHandler, FileMoveHandler
from .symlink_handlers import (
    SymlinkDirCreateHandler,
    SymlinkDirDeleteHandler,
    SymlinkFileCreateHandler,
    SymlinkFileDeleteHandler,
)

__all__ = [
    # File handlers
    "FileCreateHandler",
    "FileDeleteHandler",
    "FileModifyHandler",
    "FileMoveHandler",
    # Directory handlers
    "DirCreateHandler",
    "DirDeleteHandler",
    # Symlink handlers
    "SymlinkFileCreateHandler",
    "SymlinkFileDeleteHandler",
    "SymlinkDirCreateHandler",
    "SymlinkDirDeleteHandler",
]
