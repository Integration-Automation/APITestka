"""
Shell completion script generator.

Emits ready-to-source completion scripts for bash, zsh, fish, and PowerShell.
Each script enumerates the top-level subcommands of ``apitestka``.
"""
from __future__ import annotations

SUBCOMMANDS = ("run", "create", "mock", "import", "repl", "scaffold", "summary")
SUPPORTED_SHELLS = ("bash", "zsh", "fish", "powershell")


def generate_completion_script(shell: str) -> str:
    """Return a completion script for ``shell`` (bash/zsh/fish/powershell)."""
    if shell not in SUPPORTED_SHELLS:
        raise ValueError(f"unsupported shell {shell}; expected one of {SUPPORTED_SHELLS}")
    if shell == "bash":
        joined = " ".join(SUBCOMMANDS)
        return (
            "_apitestka_complete() {\n"
            "  local cur prev\n"
            "  COMPREPLY=()\n"
            "  cur=\"${COMP_WORDS[COMP_CWORD]}\"\n"
            f"  COMPREPLY=( $(compgen -W \"{joined}\" -- ${{cur}}) )\n"
            "}\n"
            "complete -F _apitestka_complete apitestka\n"
        )
    if shell == "zsh":
        joined = " ".join(SUBCOMMANDS)
        return (
            "_apitestka() { _arguments '*::cmd:->cmds' && case $state in cmds) "
            f"_values 'cmd' {joined};; esac }}\n"
            "compdef _apitestka apitestka\n"
        )
    if shell == "fish":
        lines = []
        for command in SUBCOMMANDS:
            lines.append(f"complete -c apitestka -n '__fish_use_subcommand' -a '{command}'")
        return "\n".join(lines) + "\n"
    return (
        "Register-ArgumentCompleter -CommandName apitestka -ScriptBlock {\n"
        "  param($wordToComplete, $commandAst, $cursorPosition)\n"
        f"  @({', '.join(repr(c) for c in SUBCOMMANDS)}) | Where-Object {{ $_ -like \"$wordToComplete*\" }}\n"
        "}\n"
    )
