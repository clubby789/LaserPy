import argparse
import operator

NORTH = [0, 1]
SOUTH = [0, -1]
EAST = [1, 0]
WEST = [-1, 0]

INSTRUCTION = 0
STRING = 1
RAW = 2

CONDITIONALS = "⌞⌜⌟⌝"
MIRRORS = "\\/>v<^" + CONDITIONALS
NULLARY = "crRpPoOnB "
UNARY = "()!~b"
BINARY = "+-×÷*gl=&|%"

def _B(self):
    chars = []
    while isinstance(self.memory.peek(), int):
        chars.append(chr(self.memory.pop()))
    self.memory.push(''.join(chars))

nullary_ops = {"c": lambda self: self.memory.push(len(self.memory)),
               "r": lambda self: self.memory.push(self.memory.peek()),
               "R": lambda self: self.memory.repl(),
               "p": lambda self: self.memory.pop(),
               "P": lambda self: self.memory.pop(),
               "o": lambda self: print(self.memory.pop()),
               "O": lambda self: self.memory.printself(),
               "n": lambda self: [self.memory.push(ord(c)) for c in self.memory.pop()[::-1]],
               "B": _B,
               " ": lambda _: None}

unary_ops = {"(": lambda x: x - 1,
             ")": lambda x: x + 1,
             "~": operator.inv,
             "!": operator.not_,
             "b": chr}

binary_ops = {"+": operator.add,
              "-": operator.sub,
              "×": operator.mul,
              "÷": operator.truediv,
              "*": operator.pow,
              "g": lambda a, b: int(b > a),
              "l": lambda a, b: int(b < a),
              "=": lambda a, b: int(a == b),
              "&": operator.and_,
              "|": operator.or_,
              "%": lambda a, b: b % a}

stack_ops = {"U": lambda self: self.memory.sUp(),
             "D": lambda self: self.memory.sDown(),
             "u": lambda self: self.memory.rUp(),
             "d": lambda self: self.memory.rDn(),
             "s": lambda self: self.memory.swUp(),
             "w": lambda self: self.memory.swDown()}

class LaserStack:
    contents = [[]]
    addr = 0

    def pop(self):
        if len(self.contents[self.addr]) == 0:
            print("Error: pop from empty stack")
            exit(-1)
        return self.contents[self.addr].pop()

    def push(self, item):
        if isinstance(item, str) and item.isnumeric():
            item = int(item)
        self.contents[self.addr].append(item)

    def peek(self):
        if len(self.contents[self.addr]) == 0:
            return 0
        return self.contents[self.addr][-1]

    def sUp(self):
        self.addr += 1
        if self.addr == len(self.contents):
            # Top of the stack
            self.contents.append([])

    def sDown(self):
        self.addr -= 1

    def swUp(self):
        a = self.contents[self.addr].pop()
        if self.addr == len(self.contents) - 1:
            self.contents.append([])
        self.contents[self.addr + 1].append(a)

    def swDown(self):
        a = self.contents[self.addr].pop()
        self.contents[self.addr - 1].append(a)

    def rUp(self):
        a = self.contents[self.addr].pop(0)
        self.contents[self.addr].append(a)

    def rDn(self):
        a = self.contents[self.addr].pop()
        self.contents[self.addr].insert(0, a)

    def repl(self):
        a = list(self.contents[self.addr])
        self.contents.insert(self.addr, a)

    def printself(self):
        while len(self):
            print(self.pop(), end=' ')
        print()

    def __repr__(self):
        return repr(self.contents[self.addr][::-1])

    def __len__(self):
        return len(self.contents[self.addr])

class LaserMachine:
    direction = [1, 0]
    memory = LaserStack()
    parse_mode = INSTRUCTION
    current_string = ""

    def __init__(self, prog, verbose=False, init=[]):
        self.verbose = verbose
        lines = prog.split('\n')
        self.prog = []
        self.width = max(map(len, lines))
        self.height = len(lines)
        for line in lines:
            self.prog.append(list(line.ljust(self.width)))
        self.pc = [0, self.height - 1]
        for var in init[::-1]:
            self.memory.push(var)
        if verbose:
            for line in self.prog:
                print(''.join(line))
            self.debug()

    def debug(self):
        """
        print(f"PC: {self.pc} -"
              f"DIRECTION: {self.direction} -"
              f"STACK: {self.memory} -"
              f"MODE: {self.parse_mode}"
              )
        """
        print(f"addr: {self.memory.addr} - "
              f"stack: {self.memory}"
              )
    def do_step(self):
        i = self.fetch_item()
        if self.verbose:
            print(i)
        if self.parse_mode == RAW:
            self.process_string(i)
        elif i in MIRRORS:
            self.switch_direction(i)
        elif self.parse_mode == INSTRUCTION:
            self.process_instruction(i)
        elif self.parse_mode == STRING:
            self.process_string(i)
        xMov, yMov = self.direction[0], self.direction[1]
        self.pc[0] += xMov
        self.pc[1] += yMov
        if self.pc[0] == self.width:
            self.pc[0] = 0
        elif self.pc[0] == -1:
            self.pc[0] = self.width - 1

        if self.pc[1] == self.height:
            self.pc[1] = 0
        elif self.pc[1] == -1:
            self.pc[1] = self.height - 1
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

        # NULLARY OPERATIONS (NO ARGUMENTS) #
        elif i in nullary_ops:
            nullary_ops[i](self)

        # UNARY OPERATIONS #
        elif i in unary_ops:
            a = self.memory.pop()
            self.memory.push(unary_ops[i](a))

        # BINARY OPERATIONS #
        elif i in binary_ops:
            a = self.memory.pop()
            b = self.memory.pop()
            self.memory.push(binary_ops[i](a, b))

        # STACK OPERATIONS #
        elif i in stack_ops:
            stack_ops[i](self)

        # TERMINATE
        elif i == "#":
            self.memory.printself()
            exit()
        else:
            print(f"Instruction {i} unknown!")
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
            if self.direction == NORTH: self.direction = WEST
            elif self.direction == WEST: self.direction = NORTH
            elif self.direction == SOUTH: self.direction = EAST
            elif self.direction == EAST: self.direction = SOUTH
        elif mirror == "/":
            if   self.direction == NORTH: self.direction = EAST
            elif self.direction == WEST: self.direction = SOUTH
            elif self.direction == SOUTH: self.direction = WEST
            elif self.direction == EAST: self.direction = NORTH
        elif mirror == ">":
            if   self.direction == NORTH: self.direction = EAST
            elif self.direction == SOUTH: self.direction = EAST
        elif mirror == "v":
            if self.direction == WEST: self.direction = SOUTH
            elif self.direction == EAST: self.direction = SOUTH
        elif mirror == "<":
            if   self.direction == NORTH: self.direction = WEST
            elif self.direction == SOUTH: self.direction = WEST
        elif mirror == "^":
            if self.direction == WEST: self.direction = NORTH
            elif self.direction == EAST: self.direction = NORTH
        elif mirror in CONDITIONALS:
            if self.memory.peek() == 0:
                if mirror == "⌞":
                    if   self.direction == NORTH: self.direction = EAST
                    elif self.direction == WEST: self.direction = NORTH
                    elif self.direction == SOUTH: self.direction = EAST
                    elif self.direction == EAST: self.direction = NORTH
                elif mirror == "⌜":
                    if   self.direction == NORTH: self.direction = EAST
                    elif self.direction == WEST: self.direction = SOUTH
                    elif self.direction == SOUTH: self.direction = EAST
                    elif self.direction == EAST: self.direction = SOUTH
                elif mirror == "⌟":
                    if   self.direction == NORTH: self.direction = WEST
                    elif self.direction == WEST: self.direction = NORTH
                    elif self.direction == SOUTH: self.direction = WEST
                    elif self.direction == EAST: self.direction = NORTH
                elif mirror == "⌝":
                    if   self.direction == NORTH: self.direction = WEST
                    elif self.direction == WEST: self.direction = SOUTH
                    elif self.direction == SOUTH: self.direction = WEST
                    elif self.direction == EAST: self.direction = SOUTH


parser = argparse.ArgumentParser(description='Run a LaserLang program.')
parser.add_argument("-v", "--verbose", action="store_true",
                    default=False, help="verbose output")
parser.add_argument("program", help="Laser program to run")
parser.add_argument("input", help="Items to initialize stack with",
                    nargs='*')
args = parser.parse_args()

with open(args.program, 'r') as f:
    prog = f.read()

LM = LaserMachine(prog, verbose=args.verbose, init=args.input)
while LM.do_step():
    pass
