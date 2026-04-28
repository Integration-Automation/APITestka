"""Tests for shell completion script generation."""
from __future__ import annotations

import pytest

from je_api_testka.cli.completion import SUBCOMMANDS, generate_completion_script


def test_bash_script_lists_subcommands():
    script = generate_completion_script("bash")
    for command in SUBCOMMANDS:
        assert command in script
    assert "complete" in script


def test_zsh_script_uses_compdef():
    script = generate_completion_script("zsh")
    assert "compdef" in script


def test_fish_script_one_completion_per_subcommand():
    script = generate_completion_script("fish")
    for command in SUBCOMMANDS:
        assert f"-a '{command}'" in script


def test_powershell_script_uses_register():
    script = generate_completion_script("powershell")
    assert "Register-ArgumentCompleter" in script


def test_unknown_shell_raises():
    with pytest.raises(ValueError):
        generate_completion_script("ksh")
