"""Test some LL programs to see if the output is correct"""
import json
import pytest
from . import prog_test, run_prog
# flake8: noqa
# pylint: disable=C0303
# Have to ignore the linters here because of the verbose string.
# Maybe could move expected output out to a file.

@pytest.mark.parametrize('prog', json.load(open("tests/programs.json")))
def test_programs(prog):
    """Iterate over and test programs"""
    prog_test(prog)


def test_verbose():
    """Test verbose mode"""
    with open('tests/programs.json') as file:
        data = json.load(file)
    helloworld = data[0]
    stdout = run_prog(helloworld['path'], '', verbose=True)
    assert stdout == r"""\   /\ 
\"Hel/ 
/dlrow\
"   \ /
#      
       
addr: 0 - stack: []
\
addr: 0 - stack: []
\
addr: 0 - stack: []
"
addr: 0 - stack: []
H
addr: 0 - stack: []
e
addr: 0 - stack: []
l
addr: 0 - stack: []
/
addr: 0 - stack: []
\
addr: 0 - stack: []
/
addr: 0 - stack: []
l
addr: 0 - stack: []
o
addr: 0 - stack: []
\
addr: 0 - stack: []
 
addr: 0 - stack: []
/
addr: 0 - stack: []
\
addr: 0 - stack: []
w
addr: 0 - stack: []
o
addr: 0 - stack: []
r
addr: 0 - stack: []
l
addr: 0 - stack: []
d
addr: 0 - stack: []
/
addr: 0 - stack: []
"
addr: 0 - stack: ['Hello world']
#
Hello world 
"""
