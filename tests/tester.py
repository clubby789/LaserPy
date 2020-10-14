import subprocess
import json

with open('tests.json') as f:
    tests = json.load(f)

for program, sample_output in tests.items():
    cmd = 'python3 ../laser.py ' + program
    stdout = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode()
    if stdout != sample_output:
        print(f'{cmd} failed:\nSample output: {sample_output!r}\nProgram output: {stdout!r}')
        exit(-1)
    else:
        print(f'{cmd} passed')
