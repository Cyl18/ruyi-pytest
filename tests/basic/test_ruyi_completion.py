import pexpect
import io
import shlex

from typing import Dict

from tests.helpers import bind_gettext, ruyi_init_default_telemetry, spawn_ruyi


def test_ruyi_output_completion_script(ruyi_exe: str, isolated_env: Dict[str, str]):
    _ = bind_gettext(isolated_env, {
        "zh_CN.UTF-8": {
            "ruyi: error: argument --output-completion-script: expected one argumen":
                "ruyi：错误：参数 --output-completion-script: 预期单个参数",
        },
    })

    # See: https://github.com/ruyisdk/ruyi/issues/452

    child = spawn_ruyi(
        ruyi_exe,
        ["--output-completion-script"],
        env=isolated_env,
    )
    try:
        child.expect_exact(_("ruyi: error: argument --output-completion-script: expected one argumen"))
        child.expect(pexpect.EOF)
    finally:
        child.close()

    assert child.exitstatus == 2

    child = spawn_ruyi(
        ruyi_exe,
        ["--output-completion-script=bash"],
        env=isolated_env,
    )
    try:
        child.expect_exact("#compdef ruyi")
        child.expect_exact("_python_argcomplete_ruyi")
        child.expect(pexpect.EOF)
    finally:
        child.close()

    assert child.exitstatus == 0

    child = spawn_ruyi(
        ruyi_exe,
        ["--output-completion-script=zsh"],
        env=isolated_env,
    )
    try:
        child.expect_exact("#compdef ruyi")
        child.expect_exact("_python_argcomplete_ruyi")
        child.expect(pexpect.EOF)
    finally:
        child.close()

    assert child.exitstatus == 0

    child = spawn_ruyi(
        ruyi_exe,
        ["--output-completion-script=fish"],
        env=isolated_env,
    )
    try:
        child.expect_exact("ValueError: Unsupported shell: fish")
        child.expect(pexpect.EOF)
    finally:
        child.close()

    assert child.exitstatus == 1


def test_ruyi_completion_issue452(ruyi_exe: str, isolated_env: Dict[str, str]):
    shell_env = isolated_env.copy()
    shell_env["PS1"] = "$ "

    output = io.StringIO()
    child = spawn_ruyi(
        "bash",
        ["--noprofile", "--norc", "-i"],
        env=shell_env,
    )
    child.logfile_read = output

    try:
        child.expect_exact("$ ")
        child.sendline(f'eval "$({shlex.quote(ruyi_exe)} --output-completion-script=bash)"')
        child.expect_exact("$ ")
        child.send("ruyi --ver")
        child.send("\t")
        child.expect_exact("ruyi --version")
        child.sendline("")
        child.expect_exact("Ruyi")
        child.expect_exact("$ ")
        child.sendline("exit")
        child.expect(pexpect.EOF)
    finally:
        child.close()

    assert child.exitstatus == 0

    completion_output = output.getvalue()
    assert "bash:" not in completion_output
    assert "Counting objects" not in completion_output
    assert "cloning from" not in completion_output
    assert "package repository does not exist" not in completion_output
