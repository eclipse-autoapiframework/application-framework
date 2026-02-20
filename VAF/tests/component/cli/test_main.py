# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test CLI."""

# from unittest import mock

from click.testing import CliRunner

from vaf.entry_points.default.entry_point import cli


class TestMain:
    """
    TestMain class
    """

    def test_cli(self) -> None:
        """test without subcommand.

        .. test:: unit test cli()
            :id: TCASE-CLI_001
            :links: CLI-001

            unit test for cli()
        """
        runner = CliRunner()
        result = runner.invoke(cli, [])
        # starting click 8.2.0, empty arguments return 2 instead of 0
        assert result.exit_code == 2, result.output

    def test_help(self) -> None:
        """test help parameter.

        .. test:: unit test --help
            :id: TCASE-CLI_002
            :links: CLI-001

            unit test for --help
        """
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0, result.output

    def test_version(self) -> None:
        """test version subcommand.

        .. test:: unit test version()
            :id: TCASE-CLI_003
            :links: CLI-001

            unit test for version()
        """
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0, result.output
        #
        # Test version with short option
        result = runner.invoke(cli, ["-v"])
        assert result.exit_code == 0, result.output

    # @mock.patch("vaf.example.greet")
    # def test_execute(self, mocked_example_greet: mock.MagicMock) -> None:
    #     """test execute subcommand.

    #     Args:
    #         mocked_example_greet (mock.MagicMock):mocked greet function

    #         .. test:: Example unit test execute()
    #             :id: TCASE-CLI_004
    #             :links: CLI-002

    #             Example unit test for execute()
    #     """
    #     mocked_example_greet.return_value = "testing"

    #     runner = CliRunner()
    #     result = runner.invoke(cli, ["execute"])

    #     assert result.exit_code == 0
    #     mocked_example_greet.assert_called_with("default-name")
