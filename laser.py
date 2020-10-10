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
        return repr(self.contents)

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
            if self.contents.peek() == 0:
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
