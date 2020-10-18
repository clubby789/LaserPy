import subprocess


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
    print(list(stdout))
    assert stdout == program["expected"]
