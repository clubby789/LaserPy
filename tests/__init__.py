"""Provides a framework for testing LL programs"""
import subprocess


def prog_test(program):
    """Test a single program"""
    stdout = run_prog(program['path'], program['args'])
    print(list(stdout))
    assert stdout == program["expected"]


def run_prog(path, args, verbose=False):
    """Run a program and return the output"""
    cmd = "python3 laser.py "
    if verbose:
        cmd += "-v "
    cmd += f"{path} "
    if args:
        cmd += args
    stdout = subprocess.run(cmd.split(),
                            stdout=subprocess.PIPE,
                            check=True).stdout.decode()
    return stdout
