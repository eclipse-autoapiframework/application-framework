# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Abstraction layer for vafmodel.Task in Config as Code."""

from __future__ import annotations

from datetime import timedelta

from typing_extensions import Self

from vaf import vafmodel


# pylint: disable-next=too-few-public-methods
class Task(vafmodel.ApplicationModuleTasks):
    """Represents a VAF Task"""

    def __init__(
        self,
        name: str,
        period: timedelta,
        preferred_offset: int | None = None,
        run_after: list[Self] | None = None,
    ):
        vafmodel.ApplicationModuleTasks.__init__(
            self,
            Name=name,
            Period=f"{int(period.total_seconds() * 1000)}ms",
            PreferredOffset=preferred_offset,
            RunAfter=[task_.Name for task_ in run_after or []],
        )

    def add_run_after(self, task: Self) -> None:
        """Add a task to the run_after dependency

        Args:
            task (Task): Task to add
        """
        self.RunAfter.append(task.Name)
