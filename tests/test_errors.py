"""Test some LL programs to see if the output is correct"""
import json
import subprocess
import pytest
from . import prog_test


@pytest.mark.parametrize('prog', json.load(open("tests/errors.json")))
def test_errors(prog):
    """Iterate over and test programs that will cause errors"""
    with pytest.raises(subprocess.CalledProcessError):
        prog_test(prog)
