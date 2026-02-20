# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""This module contains the implementation of platform-related commands."""

import json
from pathlib import Path

from vaf.core.common.constants import VAF_CFG_FILE


class PlatformCmd:  # pylint: disable=too-few-public-methods
    """Class implementing the platform related commands"""

    def __init__(self, verbose_mode: bool = False) -> None:
        """
        Initializes the class. If the VAF_CFG_FILE is found within
        the current working directory the file is used to read information
        mostly default values from that file.
        Args:
            verbose_mode (bool): Flag to enable verbose mode
        """
        if Path.is_file(Path(VAF_CFG_FILE)):
            with open(VAF_CFG_FILE, encoding="utf-8") as fh:
                self._vaf_config = json.load(fh)
        self.verbose_mode = verbose_mode
