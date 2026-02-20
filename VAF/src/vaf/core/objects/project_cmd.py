# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Implements the functionality of project-related commands."""

import importlib
import inspect
import json
import pkgutil
import re
import shutil
import sys
import warnings
from pathlib import Path
from shutil import rmtree
from types import ModuleType
from typing import Any, Dict, Optional, cast

from copier import run_copy

from vaf import vafmodel, vafpy
from vaf.core.common import constants
from vaf.core.common.constants import VAF_CFG_FILE
from vaf.core.common.exceptions import (
    VafProjectGenerationError,
    VafProjectTemplateError,
)
from vaf.core.common.utils import (
    ProjectType,
    concat_str_to_path,
    get_kwargs_from_local_variables,
    get_parent_ws,
    get_project_type,
    get_projects_in_path,
    to_camel_case,
    to_snake_case,
)
from vaf.core.state_manager.protocols import RunCopyCallableProtocol
from vaf.core.state_manager.tracker import TrailSheriff, tracking_context
from vaf.vafgeneration.vaf_application_module import validate_model_app_modules
from vaf.vafgeneration.vaf_generate_application_module import (
    generate_application_module,
)
from vaf.vafgeneration.vaf_generate_project import generate_integration_project

# pylint: disable=duplicate-code


class ProjectCmd:
    """Class implementing related project commands"""

    def __init__(self, verbose_mode: bool = False) -> None:
        """
        Ctor for CmdProject class
        Args:
            verbose_mode (bool): Flag to enable verbose mode.
        """
        self.verbose_mode = verbose_mode

    @staticmethod
    def _save_model_backup(model_path: Path) -> None:
        model_backup_path = concat_str_to_path(model_path, constants.SUFFIX["old_file"])

        print(f"Backup {model_path} file to {model_backup_path}")
        shutil.copyfile(model_path, model_backup_path)

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

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def generate_integration(
        self,
        input_file: str,
        project_dir: str,
        mode: str,
        type_variant: str,
        disable_auto_merge: bool = False,
    ) -> None:
        """Calls the associated generates to generate the project.
        Args:
            input_file (str): Path to the VAF model.
            project_dir (str): Path to the project root directory.
            mode (str): Generate for PRJ or ALL.
            type_variant (str): Type variant of the generated data types.
            disable_auto_merge (bool): Flag to disable auto merging logic after generation.
        Raises:
            ValueError: If the path to the project root directory is invalid.
            VafProjectGenerationError: If there is an error during project generation.
        """

        # validate all application modules
        model = vafmodel.load_json(input_file)
        validate_model_app_modules(model)

        # ALL: also regenerate app-module projects
        if mode == "all":
            print("Generate source for all application modules inside this Integration project.")

            if project_dir is None:
                raise ValueError("Path to project directory cannot be None!")

            base_path: Path = Path(project_dir).absolute()
            for pr_path, pr_type in get_projects_in_path(base_path / "src" / "application_modules"):
                if pr_type == ProjectType.APP_MODULE:
                    print(f"Generate source for application module in {pr_path}")

                    app_module_input_path: str = (pr_path / "model" / "model.json").as_posix()
                    generate_application_module(
                        model_file=app_module_input_path,
                        project_dir=pr_path.as_posix(),
                        verbose_mode=self.verbose_mode,
                        execute_merge=not disable_auto_merge,
                        type_variant=type_variant,
                    )
                    self._save_model_backup(Path(app_module_input_path))

        print("Generate source for integration project.")
        generate_integration_project(
            model_file=input_file,
            verbose_mode=self.verbose_mode,
            execute_merge=not disable_auto_merge,
            **(get_kwargs_from_local_variables(locals(), generate_integration_project)),  # type:ignore[arg-type]
        )
        self._save_model_backup(Path(input_file))

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    # pylint: disable=unused-argument # used via kwargs
    def generate_app_module(
        self,
        input_file: str,
        project_dir: str,
        type_variant: str,
        disable_auto_merge: bool = False,
    ) -> None:
        """Calls the associated generates to generate the project.
        Args:
            input_file (str): Path to the VAF model
            project_dir (str): Path to the project root directory
            type_variant (str): Type variant of the generated data types
            disable_auto_merge (bool): Flag to disable auto merging logic after generation
        """
        print("Generate source for Application Module.")
        generate_application_module(
            model_file=input_file,
            verbose_mode=self.verbose_mode,
            execute_merge=not disable_auto_merge,
            **(get_kwargs_from_local_variables(locals(), generate_application_module)),  # type:ignore[arg-type]
        )
        self._save_model_backup(Path(input_file))

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
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

    @staticmethod
    def __create_next_init_py_file(sub_folder: str | Path, output_dir: Path) -> None:
        """Method to create next init.py file
        Args:
            sub_folder: subfolder name
            output_dir: output directory
        """
        next_init_py_file_path = output_dir / sub_folder / "__init__.py"
        if not next_init_py_file_path.exists():
            with open(next_init_py_file_path, "w", encoding="utf-8") as file:
                file.write("")

    @staticmethod
    def __import_by_file_name(path_to_file: Path | str, file_name: str) -> ModuleType:
        """Method to import python module by it's path & fill name
        Args:
            path_to_file: path to the file
            file_name: name of the python file without ".py"
        Returns:
            ModuleType: module object contained by the file
        """
        spec = importlib.util.spec_from_file_location(file_name, f"{path_to_file}/{file_name}.py")
        module = None
        if spec:
            module = importlib.util.module_from_spec(spec)
            if module and spec.loader:
                sys.modules[file_name] = module
                spec.loader.exec_module(module)

        if not module:
            raise RuntimeError(f"Failed to import module in {path_to_file}/{file_name}.py")

        return module

    @classmethod
    def __get_packages_and_modules(
        cls, full_module_parent_dir: Path | str, output_dir: str | Path
    ) -> tuple[list[str], list[str], list[str]]:
        """Method to get packages and modules
        Args:
            full_module_parent_dir: module parent dir
            output_dir: output directory
        Returns:
            Tuple that contains lists of packages, imports, classes
        """
        packages: set[str] = set()
        imports: set[str] = set()
        classes: set[str] = set()

        if isinstance(output_dir, str):
            output_dir = Path(output_dir)

        if isinstance(full_module_parent_dir, str):
            full_module_parent_dir = Path(full_module_parent_dir)

        # if output dir is not relative to cwd (somehow wrong path, mostly pytest scenarios)
        # then correct it
        if not Path(output_dir).is_relative_to(Path.cwd()):
            output_dir = Path.cwd() / output_dir

        # Iterate over all elements in folder
        for _, element_name, is_package in pkgutil.iter_modules([(Path.cwd() / output_dir).as_posix()]):
            if is_package:
                packages.add(element_name)
                classes.add(element_name)
            elif (full_module_parent_dir / f"{element_name}.py").is_file():
                module = cls.__import_by_file_name(full_module_parent_dir, element_name)

                if module is not None:
                    if element_name.endswith("import_instances"):
                        instance_class_names = []
                        for instance_class in inspect.getmembers(module, inspect.isclass):
                            classes.add(instance_class[0])
                            instance_class_names.append(instance_class[0])
                        instance_classes_import_str = ", ".join(instance_class_names)
                        imports.add(f"from .{element_name} import {instance_classes_import_str}")

                    # check if import_application_module function is there -> import class
                    if any(
                        func_name == "import_application_module"
                        for func_name, _ in inspect.getmembers(module, inspect.isfunction)
                    ):
                        # add imported AppModules
                        for app_module_name, _ in inspect.getmembers(
                            module, lambda x: isinstance(x, vafpy.ApplicationModule)
                        ):
                            imports.add(f"from .{element_name} import {app_module_name}")
                            classes.add(app_module_name)

        return (list(packages), list(imports), list(classes))

    @staticmethod
    def __read_app_module_data_from_json(
        path_to_json: Path | str,
    ) -> tuple[str, Dict[str, Any]]:
        result: Dict[str, Any] = {}
        # Load name, namespace, consumed_interfacemodules, provided_interfacemodules and tasks from model.json
        with open(path_to_json, "r", encoding="utf-8") as file:
            model = json.load(file)
            if len(model["ApplicationModules"]) != 1:
                raise ValueError(f"Model file {path_to_json} contains more than one application module.")
            app_module = model["ApplicationModules"][0]
            name = app_module["Name"]
            result["namespace"] = app_module["Namespace"]
            result["tasks"] = [task["Name"] for task in app_module.get("Tasks", [])]
            result["consumed_interfaces"] = [mi["InstanceName"] for mi in app_module.get("ConsumedInterfaces", [])]
            result["provided_interfaces"] = [mi["InstanceName"] for mi in app_module.get("ProvidedInterfaces", [])]
            result["persistency_files"] = app_module.get("PersistencyFiles", [])

        return name, result

    @classmethod
    def __read_imports_from_init(cls, path_to_init: Path | str) -> Optional[str]:
        """Method to replace imports in model.py with explicit imports
        Args:
            path_to_init: Path to application_modules/__init__.py
        Returns:
            list of imports
        """
        if isinstance(path_to_init, str):
            path_to_init = Path(path_to_init)

        imported = re.findall(
            r"(?<=__all__ =).+(?=\])",
            path_to_init.read_text(encoding="utf-8"),
            flags=re.S,
        )
        return (
            ", ".join(
                imported[0]
                .replace("[", "")
                .replace("\n", "")
                .replace('"', "")
                .replace("]", "")
                .replace(" ", "")
                .split(",")
            )
            if len(imported) == 1
            else None
        )

    @classmethod
    def __update_model_imports(
        cls, path_to_model: Path | str, imports_str: str, tracker: Optional[TrailSheriff] = None
    ) -> None:
        """Method to replace imports in model.py with explicit imports
        Args:
            path_to_model: Path to model.py
            imports_str: import strings
        """
        if isinstance(path_to_model, str):
            path_to_model = Path(path_to_model)

        if path_to_model.is_file() and path_to_model.as_posix().endswith(".py"):
            model_text = path_to_model.read_text(encoding="utf-8")
            pattern = r"from\s+\.application_modules\s+import\s*(\([^\)]*\)|[^\n]*)"

            replacement_str = f"from .application_modules import {imports_str}"

            new_text = re.sub(pattern, replacement_str, model_text)
            if tracker is not None:
                tracker.create_modify_file(path_to_model, new_text)
            else:
                path_to_model.write_text(new_text, encoding="utf-8")

    @classmethod
    def _generate_import_instances(
        cls,
        project_dir: Path | str,
        app_modules_dir: Path,
        rel_pre_path: str,
        *,
        tracker: Optional[TrailSheriff] = None,
    ) -> None:
        """Method to generate the import_instances.py script for an application module
        Args:
            project_dir: Root path of the integration project.
            app_modules_dir (Path): Path to the application modules model directory
            rel_pre_path: Relative pre-path to the app-module directory in which the app-module is to be created,
                according to the following schema:
                <project_root_dir>/src/application_modules/<relativ_pre_path>/<app_module_dir>
            tracker: Undo/redo tracker to track file modifications.
        Raises:
            FileNotFoundError: If the model.json file cannot be found
            ValueError: If the model.json file contains more than one application module
        """
        if isinstance(project_dir, str):
            project_dir = Path(project_dir)

        app_modules_data: Dict[str, Dict[str, Any]] = {}
        # get app modules data
        app_module_src_dir = project_dir / "src/application_modules"
        for app_module_dir in app_module_src_dir.iterdir():
            model_file = app_module_dir / "model/model.json"
            if app_module_dir.is_dir() and model_file.is_file():
                name, data = cls.__read_app_module_data_from_json(model_file)
                app_modules_data[name] = data

        if app_modules_data:
            template = str(Path(__file__).parent.parent / "templates/application_module_integration_instance_import")

            run_copy_function: RunCopyCallableProtocol = cls._get_run_copy_callable(tracker)

            run_copy_function(
                template,
                app_modules_dir,
                data={
                    "app_modules_data": app_modules_data,
                    "to_camel_case": to_camel_case,
                    "generated_attributes": [
                        "Tasks",
                        "ConsumedInterfaces",
                        "ProvidedInterfaces",
                        "PersistencyFiles",
                    ],
                },
                overwrite=True,
                quiet=True,
            )

        # generate/update init.py
        cls.__generate_init_py(app_modules_dir, rel_pre_path, run_copy_function)

        # get imports strings
        imports_string = cls.__read_imports_from_init(app_modules_dir / "__init__.py")
        if imports_string is not None and not imports_string.isspace():
            # update explicit imports in integration project CaC model
            # get name of the CaC file in integration model
            path_to_cac_model = project_dir / "model/vaf" / (to_snake_case(project_dir.name) + ".py")
            # update the imports there
            cls.__update_model_imports(path_to_cac_model, imports_string, tracker)

        if tracker is not None:
            tracker.finalize(append_position=False)

    @staticmethod
    def _get_run_copy_callable(tracker: Optional[TrailSheriff] = None) -> RunCopyCallableProtocol:
        """
        Method to get the run_copy callable

        Args:
            tracker: Undo/redo tracker to track file modifications.

        Returns:
            Callable that can be used to run copy with or without tracker
        """
        if tracker is None:
            return cast(RunCopyCallableProtocol, run_copy)
        return cast(RunCopyCallableProtocol, tracker.run_copy)

    @classmethod
    def generate_import_appmodule(
        cls, rel_pre_path: str, app_modules_dir: Path, export_path: Path, *, tracker: Optional[TrailSheriff] = None
    ) -> None:
        """Method to generate the import_appmodule.py script for an application module
        Args:
            rel_pre_path (str): Relative prefix path of the app-module to the app-module directory
            app_modules_dir (Path): Path to the application modules model directory
            export_path (Path): Path to the exported model.json of the application module
            tracker: Undo/redo tracker to track file modifications.
        Raises:
            FileNotFoundError: If the model.json file cannot be found
            ValueError: If the model.json file contains more than one application module
        """
        if not export_path.is_file():
            raise FileNotFoundError(f"Model file {export_path} not found.")

        # Load name, namespace, consumed_interfacemodules, provided_interfacemodules and tasks from model.json
        name, app_module_data = cls.__read_app_module_data_from_json(export_path)

        go_down: str = ""
        if rel_pre_path not in (".", "./"):
            go_down = "../" * len(rel_pre_path.split("/"))

        template = str(Path(__file__).parent.parent / "templates/application_module_integration_model_import")

        if rel_pre_path in (".", "./"):
            app_module_dir = to_snake_case(name)
        else:
            app_module_dir = rel_pre_path + "/" + to_snake_case(name)

        cls._get_run_copy_callable(tracker)(
            template,
            app_modules_dir / rel_pre_path,
            data={
                "model_path": f"{go_down}../../../src/application_modules/{app_module_dir}/model",
                "full_app_module_dir": app_module_dir,
                "module_namespace": app_module_data["namespace"],
                "module_name": name,
                "module_name_snk": to_snake_case(name),
            },
            overwrite=True,
            quiet=True,
        )

    def create_appmodule(
        self,
        namespace: str,
        name: str,
        project_dir: str,
        rel_pre_path: str,
        model_dir: str,
    ) -> None:  # pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-positional-arguments
        """
        Args:
            namespace: Namespace of the newly created app-module.
            name: Name of the newly created app-module.
            project_dir: Root path of the integration project.
            rel_pre_path: Relative pre-path to the app-module directory in which the app-module is to be created,
            according to the following schema:
            <project_root_dir>/src/application_modules/<relative_pre_path>/<app_module_dir>
            model_dir: Path to the directory of the VAF model.

        Raises:
            VafProjectGenerationError: If there is a system-related error during create app-module.
            VafProjectTemplateError: If the app-module_import script generation fails
            ValueError: If the name of the app module to be created contains "-".
        """
        if "-" in name:
            raise ValueError(f'The name {name} of the application module must not contain "-".')
        if Path(rel_pre_path).is_absolute():
            raise VafProjectGenerationError("The path rel-pre-path must be relative!")
        if Path(model_dir).is_absolute():
            raise VafProjectGenerationError("The path model-dir must be relative!")

        output_dir: Path = Path(project_dir) / "src/application_modules" / rel_pre_path
        # check if application module already exists
        full_app_module_dir: Path = output_dir / to_snake_case(name)
        if full_app_module_dir.exists():
            raise VafProjectGenerationError("Other application module already exists on specified location!")

        output_dir.mkdir(parents=True, exist_ok=True)
        template = str(Path(__file__).resolve().parent.parent / "templates/application_module")

        run_copy(
            template,
            output_dir,
            data={
                "module_namespace": namespace,
                "module_name": name,
                "module_name_snk": to_snake_case(name),
                "module_dir_name": to_snake_case(name),
            },
        )

        app_modules_dir = Path(project_dir) / Path(model_dir) / "application_modules"

        try:
            self.generate_import_appmodule(rel_pre_path, app_modules_dir, full_app_module_dir / "model/model.json")
        except (FileNotFoundError, ValueError) as e:
            raise VafProjectTemplateError(
                f"Error generating the import_appmodule script for {namespace}::{name}:\n"
                f"{str(e)}\nCheck your application module template."
            ) from e

        sys.path.append(str(Path(project_dir) / Path(model_dir)))

        self._generate_import_instances(project_dir, app_modules_dir, rel_pre_path)

        # Check if app-module is added to an integration project inside of a workspace
        containing_ws = get_parent_ws(Path(project_dir))
        if containing_ws:
            self._update_project_paths_in_ws(containing_ws)

    @classmethod
    def __generate_init_py(
        cls,
        app_modules_dir: Path,
        rel_pre_path: str,
        run_copy_callable: Optional[RunCopyCallableProtocol] = None,
    ) -> None:
        """method to generate init.py
        Args:
            app_modules_dir: Absolute path to the application_modules dir in model/vaf
            rel_pre_path: Relative pre-path to the app-module directory in which the app-module is to be created,
                according to the following schema:
                <project_root_dir>/src/application_modules/<relative_pre_path>/<app_module_dir>
        """
        output_dir = app_modules_dir
        full_module_parent_dir = app_modules_dir

        sub_folders: list[str] = []
        if rel_pre_path not in (".", "./"):
            sub_folders = rel_pre_path.split("/")
        if len(sub_folders) > 0:
            cls.__create_next_init_py_file(sub_folders[0], output_dir)
        template = str(Path(__file__).parent.parent / "templates/application_module_integration_model_subfolder")

        packages, imports, classes = cls.__get_packages_and_modules(full_module_parent_dir, output_dir)

        run_copy_function = run_copy_callable if run_copy_callable is not None else cls._get_run_copy_callable()

        run_copy_function(
            template,
            output_dir,
            data={
                "packages": packages,
                "imports": imports,
                "classes": classes,
            },
            overwrite=True,
            quiet=True,
        )
        number_subfolders = len(sub_folders)
        for index, folder in enumerate(sub_folders):
            output_dir = output_dir / folder
            full_module_parent_dir = full_module_parent_dir / folder
            if index < (number_subfolders - 1):
                cls.__create_next_init_py_file(sub_folders[0], output_dir)

            packages, imports, classes = cls.__get_packages_and_modules(full_module_parent_dir, output_dir)
            run_copy_function(
                template,
                output_dir,
                data={
                    "packages": packages,
                    "imports": imports,
                    "classes": classes,
                },
                overwrite=True,
                quiet=True,
            )

    def import_appmodule(
        self,
        import_module_dir: str,
        project_dir: str,
        rel_pre_path: str,
        model_dir: str,
    ) -> None:  # pylint: disable=too-many-arguments, too-many-locals, too-many-statements, too-many-positional-arguments, too-many-branches
        """
        Args:
            import_module_dir: Path to the app-module which is to be imported
            project_dir: Root path of the integration project.
            rel_pre_path: Relative pre-path to the app-module directory in which the app-module is to be imported,
            according to the following schema:
            <project_root_dir>/src/application_modules/<relative_pre_path>/<app_module_dir>
            model_dir: Path to the directory of the VAF model.

        Raises:
            VafProjectGenerationError: If there is a system-related error during cleanup.
            VafProjectTemplateError: If the appmodule_import script generation fails
        """
        if Path(rel_pre_path).is_absolute():
            raise VafProjectGenerationError("The path rel-pre-path must be relative!")
        if Path(model_dir).is_absolute():
            raise VafProjectGenerationError("The path model-dir must be relative!")

        main_model = vafmodel.load_json(f"{import_module_dir}/model/model.json")
        if len(main_model.ApplicationModules) != 1:
            raise VafProjectGenerationError(
                "Imported application module has wrong number of application modules in exported model!"
            )

        name: str = main_model.ApplicationModules[0].Name
        namespace: str = main_model.ApplicationModules[0].Namespace

        output_dir: Path = Path(project_dir) / "src/application_modules" / rel_pre_path

        with tracking_context(
            f"Import app_module from {import_module_dir} to {Path(project_dir).parent.name}"
        ) as tracker:
            # check if application module is already part of integration project and if not link it in
            full_app_module_dir: Path = output_dir / to_snake_case(name)
            if not full_app_module_dir.resolve() == Path(import_module_dir).resolve():
                if full_app_module_dir.exists():
                    raise VafProjectGenerationError("Other application module already exists on specified location!")

                # track output dir creation
                if not output_dir.is_dir():
                    tracker.create_dir(output_dir)
                if Path(import_module_dir).is_absolute():
                    tracker.create_dir_symlink(full_app_module_dir, Path(import_module_dir).resolve())
                else:
                    tracker.create_dir_symlink(
                        full_app_module_dir, symlink_target=import_module_dir, relative_to=full_app_module_dir.parent
                    )

            # Generate the import_appmodule.py script
            app_modules_dir = Path(project_dir) / Path(model_dir) / "application_modules"
            try:
                self.generate_import_appmodule(
                    rel_pre_path, app_modules_dir, Path(import_module_dir) / "model/model.json", tracker=tracker
                )
            except (FileNotFoundError, ValueError) as e:
                raise VafProjectTemplateError(
                    f"Error generating the import_appmodule script for {namespace}::{name}:\n"
                    f"{str(e)}\nCheck your application module's model.json."
                ) from e

            sys.path.append(str(Path(project_dir) / Path(model_dir)))

        # tracker must finalize all operations and
        # then we add the import instances to the last operation
        self._generate_import_instances(project_dir, app_modules_dir, rel_pre_path, tracker=tracker)

    def remove_appmodule(self, project_dir: Path, model_dir: Path, app_modules: list[str]) -> None:
        """
        Args:
            project_dir (Path): Root path of the integration project.
            model_dir (Path): Path to the directory of the VAF model.
            app_modules (list[str]): List of absolute paths of the application modules to remove.

        Raises:
            ValueError: If the model-dir is absolute.
            RuntimeError: If import_<name>.py doesn't exist but needs to be removed
        """

        if model_dir.is_absolute():
            raise ValueError("The path model-dir must be relative!")

        project_dir = project_dir.resolve()  # Ensure project_dir is absolute

        # remove the application module project from rel pre path
        for app_module in app_modules:
            app_module_path = Path(app_module)
            # Check if path is in project_dir and an app module project
            if (
                not app_module_path.is_relative_to(project_dir)
                or get_project_type(app_module_path) != ProjectType.APP_MODULE
            ):
                warnings.warn(f"{app_module_path} is not an app-module project or part of the integration project.")
                continue

            print(f"Removing App Module Project {app_module_path} from integration project.")
            # use unlink to remove symlink
            if app_module_path.is_symlink():
                app_module_path.unlink()
            else:
                rmtree(app_module_path)

            app_modules_dir = project_dir / model_dir / "application_modules"
            rel_pre_path = app_module_path.relative_to(project_dir / "src/application_modules").parent
            import_model_file = app_modules_dir / rel_pre_path / f"import_{app_module_path.name}.py"
            if import_model_file.is_file():
                print(f"Removing app-module CaC Model from integration project: {import_model_file}")
                import_model_file.unlink()
            else:
                raise RuntimeError(f"VAF Error: Path {import_model_file} doesn't exist")

            self.__generate_init_py(app_modules_dir, rel_pre_path.as_posix())


# pylint: enable=duplicate-code
