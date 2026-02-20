# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Implements the functionality of project init related commands."""

import json
import subprocess
from pathlib import Path

from copier import run_copy

from vaf.core.common.constants import VAF_CFG_FILE, get_package_version
from vaf.core.common.exceptions import VafProjectGenerationError, VafProjectTemplateError
from vaf.core.common.utils import (
    ProjectType,
    get_project_type,
    get_projects_in_path,
    to_snake_case,
)


class ProjectInitCmd:
    """Class implementing related project init commands"""

    def __init__(self, verbose_mode: bool = False) -> None:
        """
        Ctor for CmdProject class
        Args:
            verbose_mode (bool): Flag to enable verbose mode.
        """
        self.verbose_mode = verbose_mode

    def _init_git_repository(self, output_dir: str) -> None:
        git_init_path = Path(output_dir).resolve()
        print(f"Initializing git repository in {git_init_path}")
        try:
            subprocess.run(["git", "init", "--initial-branch=main", git_init_path], check=True)
            subprocess.run(["git", "-C", git_init_path, "add", "."], check=True)
            print("Git repository initialized with 'main' branch.")
        except subprocess.CalledProcessError as e:
            print(f"Error initializing git repository: {e}")

    def _update_project_paths_in_ws(self, ws_path: Path) -> None:
        file_path = ws_path / ".vscode" / "settings.json"

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        source_dirs = set()
        for pr_path, pr_type in get_projects_in_path(ws_path):
            if pr_type == ProjectType.INTEGRATION:
                # add nested app-modules
                for nested_path, _ in get_projects_in_path(pr_path):
                    source_dirs.add(f"${{workspaceFolder}}/{nested_path.resolve().relative_to(ws_path).as_posix()}")
            source_dirs.add(f"${{workspaceFolder}}/{pr_path.relative_to(ws_path).as_posix()}")

        data["cmake.sourceDirectory"] = sorted(source_dirs)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def integration_project_init(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self, name: str, project_dir: str, template: str = "", git: bool = False
    ) -> None:
        """
        Args:
            name (str): The name of the project to create.
            project_dir (str): Path to the output directory.
            template (str): Project template to be used.
            git (bool): Flag to indicate if a git repository must be initialized.

        Raises:
            VafProjectTemplateError:  In cases of project template errors.
        """

        if template is None or template == "":
            template = str(Path(__file__).parent.parent / "templates/project/default")
        else:
            if not Path(template).is_dir():
                raise VafProjectTemplateError("Project template not found.")

            # Validate the minimal requirements on templates
            self._validate_vaf_config(template)

        print(f"Create Integration Project {name} in {Path(project_dir).absolute()} using template {template}")
        run_copy(
            template,
            project_dir,
            data={
                "project_name": name,
                "project_name_snk": to_snake_case(name),
                "vaf_version": get_package_version(),
            },
        )

        project_dir = str(Path(project_dir) / name)
        if git:
            self._init_git_repository(project_dir)

        # Check if project is generated inside of a workspace
        if get_project_type() == ProjectType.WORKSPACE and Path(project_dir).absolute().is_relative_to(Path.cwd()):
            self._update_project_paths_in_ws(Path.cwd())

    def interface_project_init(self, name: str, project_dir: str, git: bool = False) -> None:
        """
        Args:
            name (str): The name of the project to create.
            project_dir (str): Path to the output directory.
            git (bool): Flag to indicate if a git repository must be initialized.

        Raises:
            VafProjectTemplateError:  In cases of project template errors.
        """
        template = str(Path(__file__).parent.parent / "templates/interface_project")

        print(f"Create Interface Project {name} in {Path(project_dir).absolute()}")
        run_copy(
            template,
            project_dir,
            data={
                "project_name": name,
                "project_name_snk": to_snake_case(name),
                "export_path": "export",
                "export_name": name,
                "base_file_name": name,
                "output_path": "export",
                "vaf_version": get_package_version(),
            },
        )

        project_dir_with_name = str(Path(project_dir) / name)
        if git:
            self._init_git_repository(project_dir_with_name)

    def app_module_project_init(  # pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-positional-arguments
        self, namespace: str, name: str, project_dir: str, git: bool = False
    ) -> None:
        """
        Args:
            namespace: Namespace of the newly created app-module.
            name: Name of the newly created app-module.
            project_dir: Root path of the integration project.
            git (bool): Flag to indicate if a git repository must be initialized.

        Raises:
            VafProjectGenerationError: If there is a system-related error during init.
            ValueError: If the name of the app module to be created contains "-".
        """
        if "-" in name:
            raise ValueError(f'The name {name} of the application module must not contain "-".')

        # check if application module already exists
        full_app_module_dir: Path = Path(project_dir + to_snake_case(name))
        if full_app_module_dir.exists():
            raise VafProjectGenerationError("Application module already exists on specified location!")
        app_module_dir: Path = Path(project_dir)

        app_module_dir.mkdir(parents=True, exist_ok=True)
        template = str(Path(__file__).parent.parent / "templates/application_module")

        run_copy(
            template,
            app_module_dir,
            data={
                "module_namespace": namespace,
                "module_name": name,
                "module_name_snk": to_snake_case(name),
                "module_dir_name": name,
                "vaf_version": get_package_version(),
            },
        )

        project_dir = str(Path(project_dir) / name)
        if git:
            self._init_git_repository(project_dir)

        # Check if project is generated inside of a workspace
        if get_project_type() == ProjectType.WORKSPACE and Path(project_dir).absolute().is_relative_to(Path.cwd()):
            self._update_project_paths_in_ws(Path.cwd())

    def _validate_vaf_config(self, template: str) -> None:
        """
        Validates the VAF_CFG_FILE within the template directory if any.

        Args:
            template (str): Project template to be validated.
        """
        expected_vafconfig = Path(template) / VAF_CFG_FILE

        if not expected_vafconfig.is_file():
            raise VafProjectTemplateError(
                f"""
                Template does not have a {VAF_CFG_FILE}.
                Please refer to the documentation on how to create a valid {VAF_CFG_FILE}
                """
            )
