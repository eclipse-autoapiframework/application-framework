# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Implements the functionality of model-related commands."""

import gc
import importlib.util
import inspect
import json
import os
import pkgutil
import re
import sys
from pathlib import Path
from typing import Any

from vaf.core.common.constants import VAF_CFG_FILE
from vaf.core.common.exceptions import VafProjectGenerationError
from vaf.core.common.utils import (
    ProjectType,
    get_subprojects_in_path,
    to_snake_case,
)
from vaf.core.objects.project_cmd import ProjectCmd
from vaf.core.state_manager.tracker import tracking_context
from vaf.vafgeneration import generate_cac_support
from vaf.vafifextojson.converter import ifex_batch_to_json
from vaf.vafpy.model_runtime import ModelRuntime
from vaf.vafvssimport import vss_import

# pylint: disable=duplicate-code


class ModelCmd:  # pylint: disable=too-few-public-methods
    """Class implementing the platform-related commands"""

    def __init__(self) -> None:
        """
        Initializes the class. If the VAF_CFG_FILE is found within
        the current working directory the file is used to read information
        mostly default values from that file.
        """
        if Path.is_file(Path(VAF_CFG_FILE)):
            with open(VAF_CFG_FILE, encoding="utf-8") as fh:
                self._vaf_config = json.load(fh)

    @staticmethod
    def __get_modules_to_import(input_dir: Path) -> list[str]:
        """Method to get modules that have the `import_module()` function
        Args:
            input_dir (Path): directory to search in
        Returns:
            List of modules to add to the __init__.py
        """
        modules: set[str] = set()
        sys.path.insert(0, input_dir.as_posix())

        # Iterate over all elements in folder
        for _, element_name, is_package in pkgutil.iter_modules([str(input_dir)]):
            if is_package:
                continue
            module = importlib.import_module(element_name)

            # check if import_model function is there -> found module to import
            if any(func_name == "import_model" for func_name, _ in inspect.getmembers(module, inspect.isfunction)):
                modules.add(element_name)

        sys.path.pop(0)
        return list(modules)

    def import_vss(self, input_file: str, model_dir: str) -> None:
        """
        :param input_file: JSON file of the input model.
        :param model_dir: Output directory to generate the resulting artifacts.
        """
        if model_dir is None or model_dir == "":
            # check if it's there is any vaf_config
            if hasattr(self, "_vaf_config") and self._vaf_config is not None:
                model_dir = Path(self._vaf_config["vaf-artifacts"]["vaf-init-model"]).as_posix()

        if model_dir is not None:
            vss_import.run_import(model_dir, input_file)
            # Generate the initial model Python helper
            generate_cac_support(
                Path(model_dir), "vss-derived-model.json", "vss", Path(model_dir), project_type=ProjectType.INTERFACE
            )
        else:
            print("Importing VSS fail! Define -m or --model-dir!")

    def import_ifex(
        self, input_files: list[str], model_dir: str, model_name: str = "ifex", enable_layering: bool = True
    ) -> None:
        """
        Import one or more IFEX models and convert/merge them into a VAF model.

        :param input_files: List of YAML file(s) of the input IFEX model(s). Can be a single file or multiple files to merge. # pylint: disable = line-too-long
        :param model_dir: Output directory to generate the resulting artifacts.
        :param model_name: Name prefix for the generated model files (default: "ifex").
        :param enable_layering: If True, recursively load and merge included IFEX files (default: True).
        """
        if model_dir is None or model_dir == "":
            # check if it's there is any vaf_config
            if hasattr(self, "_vaf_config") and self._vaf_config is not None:
                model_dir = Path(self._vaf_config["vaf-artifacts"]["vaf-init-model"]).as_posix()

        if model_dir is not None:
            output_json_name = f"{model_name}-derived-model.json"
            output_file = Path(model_dir) / output_json_name
            input_paths = [Path(f) for f in input_files]
            ifex_batch_to_json(input_paths, output_file, enable_layering=enable_layering)
            # Generate the initial model Python helper
            generate_cac_support(
                Path(model_dir),
                output_json_name,
                model_name,
                Path(model_dir),
                project_type=ProjectType.INTERFACE,
            )
        else:
            print("Importing IFEX fail! Define -m or --model-dir!")

    def import_model(  # pylint: disable = too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-branches, too-many-statements
        self,
        source_json_file: str,
        model_dir: str,
        import_mode: str,
        force_import: bool = False,
        skip_import: bool = False,
    ) -> None:  # pylint: disable=too-many-locals. too-many-branches, too-many-statements
        """
        Args:
            source_json_file: Path to the source json file.
            model_dir: Path to the directory of the VAF model.
            import_mode: Mode of import, either import by copy or reference.
            force_import: If true force import.
            skip_import: If true force skip import.

        Raises:
            FileNotFoundError: If needed artifact does not exist
            ValueError: If force import and force skip both are True
        """
        source_json_path: Path = Path(source_json_file)
        if not source_json_path.is_file():
            raise FileNotFoundError(f"Given source {source_json_file} is not a file!")
        if source_json_path.suffix != ".json":
            raise FileNotFoundError(f"Given source {source_json_file} has no suffix '.json'!")
        if len(source_json_path.suffixes) > 1:
            raise FileNotFoundError(f"Given source {source_json_file} has more than one suffix!")
        if force_import and skip_import:
            raise ValueError("The CLI parameters 'force-import' and 'skip-import' cannot be set at the same time!")
        source_dir: Path = source_json_path.parent
        name: str = source_json_path.stem
        target_base_path: Path = Path(model_dir)
        if not target_base_path.is_dir():
            raise FileNotFoundError(f"Directory {model_dir} does not exist!")
        target_import_path: Path = target_base_path / "imported_models"
        if not target_import_path.is_dir():
            target_import_path.mkdir(exist_ok=True)

        imported_models_json_path: Path = target_import_path / "_imported_models.json"
        imported_models: dict[str, Any] = {"ImportedModels": []}
        if imported_models_json_path.is_file():
            with open(imported_models_json_path, "r", encoding="utf-8") as file:
                imported_models = json.loads(file.read())

        # Check that source files exists
        source_base_path: Path = source_dir
        py_file_name = to_snake_case(name.replace("derived-model", ""))
        if not source_base_path.exists():
            raise FileNotFoundError(f"Directory {str(source_dir)} does not exist!")
        source_py_path: Path = source_base_path / (py_file_name + ".py")
        if not source_py_path.exists():
            raise FileNotFoundError(f"Source Py file {source_py_path} does not exist!")

        target_json_path: Path = target_import_path / (name + ".json")
        target_py_path: Path = target_import_path / (py_file_name + ".py")
        # Check if it is a reimport or new import
        found_in_registry: bool = False
        for imported_element in imported_models["ImportedModels"]:
            if imported_element["Name"] == name:
                if not force_import:
                    if skip_import:
                        print("Import canceled!")
                        return
                    user_response: str = input(
                        "Model with same name already imported. Do you want to overwrite? (yes/no) [no]: "
                    )  # pylint: disable=line-too-long
                    if user_response != "yes":
                        print("Import canceled!")
                        return
                imported_element["SourceDir"] = os.path.relpath(source_dir, target_import_path)
                imported_element["ImportMode"] = import_mode
                found_in_registry = True
                break
        if not found_in_registry:
            add_element: dict[str, str] = {
                "Name": name,
                "SourceDir": os.path.relpath(source_dir, target_import_path),
                "ImportMode": import_mode,
            }
            imported_models["ImportedModels"].append(add_element)

        with tracking_context(
            f"Import interface from {source_json_path} to {target_base_path.absolute().parent}"
        ) as tracker:
            new_model_content = json.dumps(imported_models, indent=2)
            tracker.create_modify_file(imported_models_json_path, new_model_content)

            # tracker.delete_file(target_json_path)
            # tracker.delete_file(target_py_path)
            if import_mode == "copy":
                print("Importing model by copy!")
                # Copy source to target
                tracker.create_modify_file(target_json_path, source_json_path.read_text(encoding="utf-8"))
                tracker.create_modify_file(target_py_path, source_py_path.read_text(encoding="utf-8"))
            else:
                print("Importing model by reference!")
                # Create symlink from source to target
                tracker.create_file_symlink(target_json_path, source_json_path)
                tracker.create_file_symlink(target_py_path, source_py_path)

        # create __init__.py for current directory
        template = str(Path(__file__).parent.parent / "templates/interface_model_subfolder")
        modules = self.__get_modules_to_import(target_import_path)

        # finalize tracker and then append to last operation
        tracker.run_copy(
            template,
            target_import_path,
            data={"modules": modules},
            overwrite=True,
            quiet=True,
        )
        tracker.finalize(append_position=False)

    def update_imported_models(self, model_dir: str) -> None:  # pylint: disable=too-many-locals
        """
        Args:
            model_dir: Path to the directory of the VAF model.

        Raises:
            FileNotFoundError: If needed artifact does not exist
        """
        target_base_path: Path = Path(model_dir)
        if not target_base_path.exists():
            raise FileNotFoundError(f"Directory {model_dir} does not exist!")
        target_import_path: Path = target_base_path / "imported_models"
        if not target_import_path.exists():
            print("No imported modules to update. Skipping!")
            return
        imported_models_json_path: Path = target_import_path / "_imported_models.json"
        imported_models: dict[str, Any] = {"ImportedModels": []}
        if imported_models_json_path.exists():
            with open(imported_models_json_path, "r", encoding="utf-8") as file:
                imported_models = json.loads(file.read())
        else:
            print("No imported modules to update. Skipping!")
            return
        for imported_element in imported_models["ImportedModels"]:
            if imported_element["ImportMode"] == "copy":
                print(f"Update imported module {imported_element['Name']}.")
                source_base_path: Path = target_import_path / Path(imported_element["SourceDir"])
                if not source_base_path.exists():
                    raise FileNotFoundError(f"Directory {source_base_path} does not exist!")
                source_json_path: Path = source_base_path / (imported_element["Name"] + ".json")
                if not source_json_path.exists():
                    raise FileNotFoundError(f"Source Json file {source_json_path} does not exist!")
                source_py_path: Path = source_base_path / (to_snake_case(imported_element["Name"]) + ".py")
                if not source_py_path.exists():
                    raise FileNotFoundError(f"Source Py file {source_py_path} does not exist!")
                # Copy source to target
                target_json_path: Path = target_import_path / (imported_element["Name"] + ".json")
                target_json_path.write_text(source_json_path.read_text())
                target_py_path: Path = target_import_path / (to_snake_case(imported_element["Name"]) + ".py")
                target_py_path.write_text(source_py_path.read_text())

    # pylint: enable=duplicate-code

    def update_app_modules(self, model_dir: Path, app_modules: list[Path]) -> None:
        """(Re-)generates the import_appmodule.py scripts for given app modules.
        Args:
            model_dir (Path): Path to the directory of the project model.
            app_modules (list[Path]): List of absolute paths of the application modules to update.

        Raises:
            VafProjectGenerationError: If an application module does not have a model.json file or it is malformed.
        """
        for project_path in app_modules:
            project_path = project_path / "model/"

            # find rel_pre_path
            pattern = r"\/src\/application_modules\/(.*)\/.*?\/model"
            match = re.search(pattern, project_path.as_posix())
            rel_pre_path = match.group(1) if match else "."

            # call import generation
            try:
                ProjectCmd.generate_import_appmodule(
                    rel_pre_path,
                    app_modules_dir=model_dir / "application_modules",
                    export_path=project_path / "model.json",
                )
            except (FileNotFoundError, ValueError) as e:
                raise VafProjectGenerationError(
                    f"Error generating the import_appmodule script for {project_path}/model.json:\n"
                    f"{str(e)}\nCheck your application module configuration."
                ) from e

            # update import instance
            ProjectCmd._generate_import_instances(  # pylint:disable=protected-access
                Path.cwd(),
                app_modules_dir=model_dir / "application_modules",
                rel_pre_path=rel_pre_path,
            )

    def generate(self, project_type: ProjectType, model_dir: str, mode: str, skip_validation: bool = False) -> None:
        """Calls the associated generates to generate the project.
        Args:
            project_type (ProjectType): VAF project type.
            model_dir (str): Path to the directory of the VAF model.
            mode (str): Generate for prj or all projects.
            skip_validation(bool): Skip the model validation.
        Raises:
            ValueError: If the CaC script of a (sub-) project can't be found / executed
            VafProjectGenerationError: If the app-module_import script generation fails
        """

        def _run_cac(model_file: Path) -> None:
            print(f"Executing CaC for {model_file}")
            # Clear __pycache__ to ensure everything is loaded properly
            os.system(f'find {model_file.parent} -name "__pycache__" -exec rm -rf {{}} +')
            # Reset runtime, remove previously loaded model, for the model-import to be triggered again
            ModelRuntime().reset()
            loaded_modules_before_cac = list(sys.modules)

            spec = importlib.util.spec_from_file_location(model_file.stem, model_file, submodule_search_locations=[])
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                if spec.loader is not None:
                    # temporarily add model_dir to sys.path to support local imports
                    sys.path.insert(0, model_file.parent.as_posix())
                    try:
                        sys.modules[model_file.stem] = module
                        spec.loader.exec_module(module)
                        module.export_model(skip_validation)
                    except Exception as e:
                        raise ValueError(f"CaC cannot be executed: {model_file}:\n{str(e)}") from e
                    finally:
                        sys.path.pop(0)

            # unload all modules loaded during CaC execution
            modules_to_unload = [mod for mod in sys.modules if mod not in loaded_modules_before_cac]
            for mod in modules_to_unload:
                del sys.modules[mod]
            gc.collect()

        if "all" == mode and project_type == ProjectType.INTEGRATION:
            # find all subprojects
            app_modules_dir = Path(model_dir) / "application_modules"
            subprojects = get_subprojects_in_path(ProjectType.APP_MODULE, app_modules_dir)

            for project_path in subprojects:
                model_path = project_path / "model" / "model.py"
                _run_cac(model_path)

            # call import generation
            self.update_app_modules(model_dir=Path(model_dir), app_modules=subprojects)

        # call local cac
        _run_cac(Path(model_dir) / "model.py")
