# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""VSS-related generator tests."""

# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="no-untyped-def"
import importlib
import inspect
import sys
from pathlib import Path

from vaf.vafgeneration import vaf_cac_support
from vaf.vafpy import ModuleInterface
from vaf.vafvssimport import vss_import


class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for VSS generation"""
        vss_input = Path(__file__).parent / "vss/seat_vss.json"
        vss_import.run_import(str(tmp_path), str(vss_input))
        vaf_cac_support.generate(tmp_path, "vss-derived-model.json", "vss", Path(tmp_path))

        # try to import the vss
        spec = importlib.util.spec_from_file_location("vss", tmp_path / "vss.py")
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        sys.modules["vss"] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]

        assert inspect.isclass(module.Vss)
        assert inspect.isclass(module.Vss.Vehicle)
        assert isinstance(module.Vss.vehicle_if, ModuleInterface)
        assert inspect.isclass(module.Vss.Vehicle.Cabin.Seat.Row1.Driverside)
        assert isinstance(module.Vss.Vehicle.Cabin.Seat.Row1.driver_side_if, ModuleInterface)
        assert inspect.isclass(module.Vss.Vehicle.Cabin.Seat.Row1.Driverside.Backrest)
        assert inspect.isclass(module.Vss.Vehicle.Cabin.Seat.Row2.Driverside.Backrest)
        assert isinstance(
            module.Vss.Vehicle.Cabin.Seat.Row1.Driverside.Backrest.lumbar_if,
            ModuleInterface,
        )
        assert isinstance(
            module.Vss.Vehicle.Cabin.Seat.Row2.Driverside.Backrest.lumbar_if,
            ModuleInterface,
        )
