# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Implements the functionality of workspace-related commands."""

import os
import re
from pathlib import Path

from copier import run_copy

from vaf.core.common.constants import get_package_version


class WorkspaceCmd:  # pylint: disable=too-few-public-methods
    """Class implementing related workspace commands"""

    def __init__(self) -> None:
        """
        Ctor for WorkspaceCmd class
        """

    def _get_devcontainer_mounts(self, paths: tuple[str, ...], project_dir: str) -> list[str]:
        """Converts a tuple of paths into mount point statements for a DevContainer.
        Relative paths are converted to be relative to the corresponding project.

        Args:
            paths (tuple[str]): Relative or absolute paths to mount in the DevContainer.
            project_dir (str): Path to the project directory.

        Returns:
            A list of strings that match the syntax of devcontainer's mount points.
        """
        mounts = []
        for path_str in paths:
            if not Path(path_str).is_absolute():
                path_str = f"${{localWorkspaceFolder}}/../{os.path.relpath(path_str, project_dir)}"
            mounts.append(
                f"source={path_str},target=/opt/vaf/mounts/{Path(path_str).name},type=bind,consistency=cached"
            )
        return mounts

    def init(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self, name: str, workspace_dir: str, mount_paths: tuple[str, ...] = ()
    ) -> None:
        """Initializes a new VAF workspace with required directories and configuration files.

        Args:
            name (str): The name of the project to create.
            workspace_dir (str): Path to the output directory.
            mount_paths (tuple[str]): List of paths to include in the DevContainer mounts.

        Raises:
            VafProjectTemplateError:  In cases of project template errors.
        """

        pwd = Path(__file__).resolve().parent.parent
        template = str(pwd / "templates" / "workspace")

        vaf_version = get_package_version()
        devcontainer_version = vaf_version if re.fullmatch(r"\d+\.\d+\.\d+", vaf_version) else "latest"

        print(f"Creating Workspace {name} in {Path(workspace_dir).absolute()}")
        run_copy(
            template,
            workspace_dir,
            data={
                "workspace_name": name,
                "mount_paths": self._get_devcontainer_mounts(mount_paths, workspace_dir),
                "devcontainer_version": devcontainer_version,
                "vaf_version": vaf_version,
            },
        )
