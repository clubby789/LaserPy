import argparse

NORTH = [0, 1]
SOUTH = [0, -1]
EAST = [1, 0]
WEST = [-1, 0]


INSTRUCTION = 0
STRING      = 1
RAW         = 2

CONDITIONALS = "⌞⌜⌟⌝"
MIRRORS = "\\/>v<^" + CONDITIONALS
UNARY = "()crR!~pPoObnB"
BINARY = "+-×÷*gl=&|%"

class LaserStack:
    contents = []

    def pop(self):
        if len(self.contents) == 0:
            print("Error: pop from empty stack")
            exit(-1)
        return self.contents.pop()

    def push(self, item):
        self.contents.append(item)

    def peek(self):
        if len(self.contents) == 0:
            return 0
        return self.contents[-1]

    def __repr__(self):
        return repr(self.contents[::-1])

    def __len__(self):
        return len(self.contents)

class LaserMachine:
    direction = [1, 0]
    memory = LaserStack()
    parse_mode = INSTRUCTION
    current_string = ""
    def __init__(self, prog, verbose=False):
        self.verbose = verbose
        lines = prog.split('\n')
        self.prog = []
        self.width = len(max(lines, key=len))
        self.height = len(lines)
        for line in lines:
            self.prog.append(list(line.ljust(self.width)))
        self.pc = [0, self.height - 1]
        if verbose:
            for line in self.prog:
                print(''.join(line))
            self.debug()

    def debug(self):
            print(f"PC: {self.pc} - DIRECTION: {self.direction} - STACK: {self.memory} - MODE: {self.parse_mode}")


    def do_step(self):
        i = self.fetch_item()
        if self.verbose:
            print(i)
        if self.parse_mode == RAW:
            self.process_string(i)
        elif i in MIRRORS:
            self.switch_direction(i)
        elif self.parse_mode == INSTRUCTION:
            self.process_instruction( i)
        elif self.parse_mode == STRING:
            self.process_string(i)
        xMov, yMov = self.direction[0], self.direction[1]
        self.pc[0] += xMov
        self.pc[1] += yMov
        if self.verbose:
            self.debug()
        return True

    def fetch_item(self):
        x, y = self.pc[0], self.height - self.pc[1] - 1
        return self.prog[y][x]

    def process_instruction(self, i):
        if i == '"':
            self.parse_mode = STRING
        elif i == '`':
            self.parse_mode = RAW

        # UNARY OPERATIONS #

        elif i == "(": # DEC
            val = self.memory.pop()
            val -= 1
            self.memory.push(val)
        elif i == ")": # INC
            val = self.memory.pop()
            val += 1
            self.memory.push(val)
        elif i == "c": # CRD
            val = len(self.memory)
            self.memory.push(val)
        elif i == "r" or i == "R": # RPL
            # Should function the same for replicating a stack
            # or a value
            val = self.memory.peek()
            self.memory.push(val)
        elif i == "!": # NBF
            pass
        elif i == "~": # NBW
            val = self.memory.pop()
            val = ~val
            self.memory.push(val)
        elif i == "p" or i == "P": # POP
            val = self.memory.pop()
        elif i == "o": # POPO
            val = self.memory.pop()
            print(val)
        elif i == "O": # POPS
            while len(self.memory) > 0:
                print(self.memory.pop(), end=' ')
            print('')
        elif i == "b": # CS
            val = self.memory.pop()
            val = chr(val)
            self.memory.push(val)
        elif i == "n": # CN
            val = self.memory.pop()
            for c in val[::-1]:
                self.memory.push(ord(c))
        elif i == "B": # CSS
            nums = []
            while type(self.memory.peek()) == int:
                nums.append(self.memory.pop())
            val = ''.join([chr(x) for x in nums])
            self.memory.push(val)

        # BINARY OPERATIONS #

        elif i == "+": # ADD
            val = self.memory.pop() + self.memory.pop()
            self.memory.push(val)
        elif i == "-": # SUB
            val = self.memory.pop() - self.memory.pop()
            self.memory.push(val)
        elif i == "×": # MUL
            val = self.memory.pop() * self.memory.pop()
            self.memory.push(val)
        elif i == "÷": # DIV
            a = self.memory.pop()
            b = self.memory.pop()
            val = b / a
            self.memory.push(val)
        elif i == "*": # EXP
            a = self.memory.pop()
            b = self.memory.pop()
            val = b ** a
            self.memory.push(val)
        elif i == "g": # GRT
            a = self.memory.pop()
            b = self.memory.pop()
            val = int(b > a)
            self.memory.push(val)
        elif i == "l": # LSS
            a = self.memory.pop()
            b = self.memory.pop()
            val = int(b < a)
            self.memory.push(val)
        elif i == "u": # EQL
            a = self.memory.pop()
            b = self.memory.pop()
            val = int(b == a)
            self.memory.push(val)
        elif i == "&": # AND
            val = int(self.memory.pop & self.memory.pop())
            self.memory.push(val)
        elif i == "&": # OR
            val = int(self.memory.pop | self.memory.pop())
            self.memory.push(val)
        elif i == "&": # MOD
            a = self.memory.pop()
            b = self.memory.pop()
            val = b % a
            self.memory.push(val)


        elif i == "#":
            while len(self.memory) > 0:
                print(self.memory.pop(), end=' ')
            print('')
            exit()

    def process_string(self, i):
        if i == '"' or i == '`':
            self.memory.push(self.current_string)
            self.current_string = ""
            self.parse_mode = INSTRUCTION
        else:
            self.current_string += i

    def switch_direction(self, mirror):
        if mirror == "\\":
            if   self.direction == NORTH: self.direction = WEST
            elif self.direction == WEST : self.direction = NORTH
            elif self.direction == SOUTH: self.direction = EAST
            elif self.direction == EAST : self.direction = SOUTH
        elif mirror == "/":
            if   self.direction == NORTH: self.direction = EAST
            elif self.direction == WEST : self.direction = SOUTH
            elif self.direction == SOUTH: self.direction = WEST
            elif self.direction == EAST: self.direction  = NORTH
        elif mirror == ">":
            if   self.direction == NORTH: self.direction = EAST
            elif self.direction == SOUTH: self.direction = EAST
        elif mirror == "v":
            if self.direction == WEST : self.direction = SOUTH
            elif self.direction == EAST : self.direction = SOUTH
        elif mirror == "<":
            if   self.direction == NORTH: self.direction = WEST
            elif self.direction == SOUTH: self.direction = WEST
        elif mirror == "^":
            if self.direction == WEST : self.direction = NORTH
            elif self.direction == EAST: self.direction  = NORTH
        elif mirror in CONDITIONALS:
            if self.memory.peek() == 0:
                if mirror == "⌞":
                    if   self.direction == NORTH: self.direction = EAST
                    elif self.direction == WEST : self.direction = NORTH
                    elif self.direction == SOUTH: self.direction = EAST
                    elif self.direction == EAST : self.direction = NORTH
                elif mirror == "⌜":
                    if   self.direction == NORTH: self.direction = EAST
                    elif self.direction == WEST : self.direction = SOUTH
                    elif self.direction == SOUTH: self.direction = EAST
                    elif self.direction == EAST : self.direction = SOUTH
                elif mirror == "⌟":
                    if   self.direction == NORTH: self.direction = WEST
                    elif self.direction == WEST : self.direction = NORTH
                    elif self.direction == SOUTH: self.direction = WEST
                    elif self.direction == EAST : self.direction = NORTH
                elif mirror == "⌝":
                    if   self.direction == NORTH: self.direction = WEST
                    elif self.direction == WEST : self.direction = SOUTH
                    elif self.direction == SOUTH: self.direction = WEST
                    elif self.direction == EAST : self.direction = SOUTH


parser = argparse.ArgumentParser(description='Run a LaserLang program.')
parser.add_argument("-v", "--verbose", action="store_true",
                    default=False, help="verbose output")
parser.add_argument("program", help="Laser program to run")
args = parser.parse_args()

with open(args.program, 'r') as f:
    prog = f.read()

LM = LaserMachine(prog, verbose=args.verbose)
while LM.do_step():
    pass
