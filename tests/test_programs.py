"""Test some LL programs to see if the output is correct"""
import subprocess
import json
import pytest  # noqa


def prog_test(program):
    """Test a single program"""
    if program['args'] is None:
        cmd = f"python3 laser.py {program['path']}"
    else:
        cmd = f"python3 laser.py {program['path']} {program['args']}"
    print(cmd)
    stdout = subprocess.run(cmd.split(),
                            stdout=subprocess.PIPE,
                            check=True).stdout.decode()
    assert stdout == program["expected"]


@pytest.mark.parametrize('prog', json.load(open("tests/tests.json")))
def test_programs(prog):
    """Iterate over and test programs"""
    prog_test(prog)
