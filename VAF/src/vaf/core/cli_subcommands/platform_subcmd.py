# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf platform subcommands"""

import click


# vaf platform derive group #
@click.group()
def platform_derive() -> None:
    """Derive platform-specific artifacts into the project."""


# vaf platform export group #
@click.group()
def platform_export() -> None:
    """Export the VAF configuration to a platform-specific file format."""
