# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator library for generating the complete VAF project."""

import shutil
import subprocess
from pathlib import Path
from typing import List

from vaf import vafmodel
from vaf.core.common.constants import SUFFIX

# Utils
from vaf.core.common.utils import (
    concat_str_to_path,
)


def __file_has_conflict(file_path: Path) -> bool:
    """Function to check if file contains conflicts
    Args:
        file_path: Path to the file
    Return:
        boolean if file contains conflicts
    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return all(conflict_sign in file_content for conflict_sign in ["<<<<<<<", "=======", ">>>>>>>"])


def __get_ancestor_file_rel_path(real_file_rel_path: str | Path) -> str | Path:
    """Function to get rel path of the ancestor of a user file as str
    Args:
        real_file_rel_path: rel path of the real file
    Returns:
        respective rel path of the ancestor
    """
    return (
        concat_str_to_path(real_file_rel_path, SUFFIX["ancestor_file"])
        if isinstance(real_file_rel_path, Path)
        else real_file_rel_path + SUFFIX["ancestor_file"]
    )


def __get_newly_generated_file_path(real_file_rel_path: str | Path) -> str | Path:
    """Function to get rel path of the newly generated file (.new~)
    Args:
        real_file_rel_path: rel path of the real file
    Returns:
        respective rel path of the newly generated file
    """
    return (
        concat_str_to_path(real_file_rel_path, SUFFIX["new_file"])
        if isinstance(real_file_rel_path, Path)
        else real_file_rel_path + SUFFIX["new_file"]
    )


def __get_backup_file_path(real_file_rel_path: str | Path) -> str | Path:
    """Function to get rel path of the backup file (~)
    Args:
        real_file_rel_path: rel path of the real file
    Returns:
        respective rel path of the backup file
    """
    return (
        concat_str_to_path(real_file_rel_path, SUFFIX["old_file"])
        if isinstance(real_file_rel_path, Path)
        else real_file_rel_path + SUFFIX["old_file"]
    )


def __merge_files(
    newly_generated_file: Path,
    patched_file_path: Path,
    common_ancestor_file_path: Path,
    verbose_mode: bool = False,
) -> None:
    """Function to perform three-way files merge through subprocess
    Documentation for git merge-file: https://git-scm.com/docs/git-merge-file
    Args:
        newly_generated_file: path to the newly generated file (ends w/ .new~)
        patched_file_path: path to the patched file (older generated file + patch)
        common_ancestor_file_path: path to the common ancestor of current & patched (older generated file)
        verbose_mode (bool): Flag to enable verbose mode
    """
    # build cmd to perform git merge-file:
    # merge newly generated file to current file (patched_file)
    args = [
        "git",
        "merge-file",
        "-p",  # -p to send results to stdout
        newly_generated_file.as_posix(),
        common_ancestor_file_path.as_posix(),
        patched_file_path.as_posix(),
    ]
    # run the cmd
    merge = subprocess.run(args, capture_output=True, text=True, check=False)

    old_file_path = concat_str_to_path(patched_file_path, SUFFIX["old_file"])

    # check if merge results has conflicts
    msg_list = []
    if merge.returncode == 0:
        msg_list += (
            [
                "\nMERGE INFO",
                f"    Merge of {newly_generated_file} with {patched_file_path} successfully without conflicts!",
                f"    Merge result is saved in {patched_file_path}.",
            ]
            if verbose_mode
            else []
        )
    elif merge.returncode >= 1:
        msg_list += [
            "\nMERGE WARNING:",
            f"    Merge of {newly_generated_file} with {patched_file_path} has conflicts!",
            f"    Merge result is saved in {patched_file_path}. Please resolve the conflicts before moving on.",
        ]

    msg_list += (
        [
            f"    Original state of {patched_file_path} before merge is saved as backup in {old_file_path}\n",
        ]
        if msg_list
        else []
    )

    if verbose_mode:
        print(f"Return code is {merge.returncode} File: {patched_file_path}")

    if merge.returncode >= 0:
        print("\n".join(msg_list))
        # save merge results
        with open(patched_file_path, "w", encoding="utf-8") as out_file:
            out_file.write(merge.stdout)
    else:
        # Inform user if merge fails: Don't abort the whole workflow!
        print(f"Merge fails for file {patched_file_path}! Error code {merge.returncode} Reason: {merge.stderr}")


# --- Helper Function ---
def strip_suffix(name: str) -> str:
    """
    Remove any known suffix from a filename.
    Args:
        name: The filename to process.
    Returns:
        The filename with any recognized suffix removed.
    """
    # Sort suffixes by length (longest first) to avoid partial matches
    for suffix in sorted(SUFFIX.values(), key=len, reverse=True):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def is_source_file(file_path: Path) -> bool:
    """
    Helper function to identify the C++ source files.
    Args:
        file_path: Path object representing the file to check.
    Returns:
        True if the file is a recognized C++ source or header file (including variants),
        False otherwise.
    """
    base_extensions = [".cpp", ".h", ".hpp", ".cc"]
    base_name = strip_suffix(file_path.name)
    return not file_path.name.startswith("CMake") and any(base_name.endswith(ext) for ext in base_extensions)


def format_files(project_dir: str, list_files: List[Path], verbose_mode: bool = False) -> None:
    """Function to format source files and their variants (~, .new~, ~ancestor) if the base file is in list_files.
    Args:
        project_dir: Path to the project directory
        list_files: List of files to format
        verbose_mode (bool): Flag to enable verbose mode
    """
    print("Clang-formatting the generated source files.")

    # Normalize list_files to absolute paths
    base_paths = {f.resolve() for f in list_files}

    for file_path in Path(project_dir, "implementation").rglob("*"):
        if file_path.is_file() and is_source_file(file_path.resolve()):
            # Strip allowed suffixes to get base path
            base_name = strip_suffix(file_path.name)
            base_candidate = file_path.with_name(base_name).resolve()

            # Check if base path is in list_files
            if base_candidate in base_paths:
                if verbose_mode:
                    print(f"Formatting: {file_path}")
                try:
                    # Run clang-format
                    subprocess.run(
                        ["clang-format", "-i", str(file_path.resolve())],
                        check=True,
                        capture_output=True,
                        text=True,
                        cwd=str(project_dir),
                    )
                except subprocess.CalledProcessError as e:
                    print(f"clang-format failed for {file_path}:")
                    print("Exit code:", e.returncode)
                    print("Output:", e.stdout)
                    print("Error:", e.stderr)


def merge_after_regeneration(out_dir: Path, list_of_user_files_rel_path: List[str], verbose_mode: bool = False) -> None:
    """Function to perform three-way files merge after regeneration of app_module
    Args:
        out_dir: Path to the output directory
        list_of_user_files_rel_path: List of relative path from out_dir to user files (files that users can edit)
        verbose_mode (bool): Flag to enable verbose mode
    """
    for rel_path_to_file in list_of_user_files_rel_path:
        newly_generated_file_path = out_dir / __get_newly_generated_file_path(rel_path_to_file)
        ancestor_file_path = out_dir / __get_ancestor_file_rel_path(rel_path_to_file)
        # merge needed if there is a copy of .new~ file is created
        # merge can only be performed if ancestor exists
        if newly_generated_file_path.is_file():
            if ancestor_file_path.is_file():
                # backup current file
                current_file = out_dir / rel_path_to_file
                backup_file = __get_backup_file_path(current_file)
                # if current file has conflict, then check if backup is valid to be used
                if __file_has_conflict(current_file):
                    print(
                        "\n".join(
                            [
                                "WARNING:",
                                f"  The file {current_file} contains unresolved merge conflicts and will be ignored!",
                                f"  Using the backup file {backup_file} for the merge instead.",
                            ]
                        )
                    )
                    assert isinstance(backup_file, Path)  # Are you satisfied now, mypy?
                    if backup_file.is_file() and not __file_has_conflict(backup_file):
                        shutil.copyfile(backup_file, current_file)
                else:
                    # current file has no conflict, overwrite backup
                    shutil.copyfile(
                        out_dir / rel_path_to_file,
                        __get_backup_file_path(out_dir / rel_path_to_file),
                    )

                # perform three way merge
                __merge_files(
                    newly_generated_file=newly_generated_file_path,
                    patched_file_path=out_dir / rel_path_to_file,
                    common_ancestor_file_path=ancestor_file_path,
                    verbose_mode=verbose_mode,
                )
            else:
                # warning only if newly generated file exists,
                msg_list = [
                    "WARNING:",
                    f"  Cannot merge {newly_generated_file_path} to {out_dir / rel_path_to_file} automatically!",
                    "  Can't find old model.json~",
                    (
                        "  Please merge both files manually. The auto merge will be available "
                        + "the next time the model is updated."
                    ),
                ]
                print("\n".join(msg_list))

            # remove newly generated file only if merge took place
            # else no old model.json~ -> new file is identical with current, remove it
            newly_generated_file_path.unlink()

        # remove ancestor file regardless of the merge
        if ancestor_file_path.is_file():
            ancestor_file_path.unlink()


def get_ancestor_file_suffix(is_ancestor: bool) -> str:
    """Method to get file's suffix for ancestor
    Args:
        is_ancestor: boolean for ancestor
    Returns:
        file suffix if it's ancestor
    """
    return SUFFIX["ancestor_file"] if is_ancestor else ""


def get_ancestor_model(input_file: str) -> vafmodel.MainModel | None:
    """Function to get old model
    Args:
        input_file: Path to current model file
    Returns:
        Old vafmodel, if old model.json file exists
    """
    # check for "ancestor" model.json (model.json~)
    ancestor_json = concat_str_to_path(Path(input_file), SUFFIX["old_file"])
    return vafmodel.load_json(ancestor_json) if ancestor_json.is_file() else None
