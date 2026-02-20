# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""VSS import."""

import json
from pathlib import Path

from vaf.vafvssimport.vss.vss_model import VSS


def run_import(out_dir: str, input_file: str) -> bool:
    """Runs JSON import for the VSS catalog

    Args:
        out_dir (str): The output directory for the vss.json model.
        input_file (str): JSON file to import.

    Raises:
        OSError: Raised when files cannot be written
        OSError: Raised when JSON file cannot be found

    Returns:
        bool: Indicates whether the import succeeded
    """

    path_to_json = out_dir + "/vss-derived-model.json"
    with open(path_to_json, "w+", encoding="utf-8") as json_file:
        if not json_file.writable():
            raise OSError("Can not write to file " + str(path_to_json))

        # Import type definitions from IDLs
        if Path(input_file).is_file():
            with open(input_file, "r", encoding="utf-8") as f:
                vss_json = json.load(f)
                vss_model = VSS(vss_json)

            json_model = vss_model.export().model_dump_json(
                indent=2, by_alias=True, exclude_unset=True, exclude_defaults=True
            )
            json_file.write(json_model)

        else:
            raise OSError("VSS JSON file " + str(input_file) + " not found")

    print(f"VSS Catalogue imported to '{Path(path_to_json).absolute()}'.")

    return True
