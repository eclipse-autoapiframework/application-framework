# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Contains helper functions for dealing with IFEX."""

from pathlib import Path
from typing import Optional

from ifex.models.ifex.ifex_ast import AST, Namespace
from ifex.models.ifex.ifex_parser import get_ast_from_yaml_file


def load_ifex_file(ifex_file: Path) -> AST:
    """Load an IFEX file and return its AST

    Args:
        ifex_file: Path to the IFEX YAML file

    Returns:
        AST: Abstract syntax tree (vehicle service catalog) from the IFEX file
    """
    return get_ast_from_yaml_file(str(ifex_file))


def load_ifex_with_includes(ifex_file: Path, base_path: Optional[Path] = None) -> AST:
    """Load an IFEX file and recursively load all included files, merging them into a single AST

    Args:
        ifex_file: Path to the main IFEX YAML file
        base_path: Base path for resolving relative includes (defaults to ifex_file's parent)

    Returns:
        AST: Merged abstract syntax tree containing all included namespaces
    """
    if base_path is None:
        base_path = ifex_file.parent

    # Load the main file
    main_ast = get_ast_from_yaml_file(str(ifex_file))

    # If no includes, return as-is
    if not main_ast.includes:
        return main_ast

    # Track all namespaces from includes first, then main file
    # This order ensures proper layering: includes provide base, main file overrides
    all_namespaces: list[Namespace] = []

    # Process each include FIRST (base definitions)
    for include in main_ast.includes:
        include_path = base_path / include.file
        if not include_path.exists():
            print(f"Warning: Include file not found: {include_path}")
            continue

        print(f"Loading included IFEX file: {include_path}")
        # Recursively load included files (they might have their own includes)
        included_ast = load_ifex_with_includes(include_path, base_path)

        # Merge namespaces from included file
        if included_ast.namespaces:
            all_namespaces.extend(included_ast.namespaces)

    # Add main file namespaces LAST (override definitions)
    if main_ast.namespaces:
        all_namespaces.extend(main_ast.namespaces)

    # Create merged AST with all namespaces
    merged_ast = AST(
        name=main_ast.name,
        description=main_ast.description,
        major_version=main_ast.major_version,
        minor_version=main_ast.minor_version,
        includes=None,  # Clear includes as they're now merged
        namespaces=all_namespaces if all_namespaces else None,
        filetype=main_ast.filetype,
        schema=main_ast.schema,
    )

    return merged_ast
