"""Test some LL programs to see if the output is correct"""
import json
import pytest  # noqa
from . import prog_test


@pytest.mark.parametrize('prog', json.load(open("tests/operations.json")))
def test_operations(prog):
    """Iterate over and test programs"""
    prog_test(prog)
