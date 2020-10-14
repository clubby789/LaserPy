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
UNARY = "()crR!~pPoObnB"
BINARY = "+-×÷*gl=&|%"

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

class LaserStack:
    self.contents = [[]]
    self.addr = 0

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

        # UNARY OPERATIONS #

        elif i == "(":  # DEC
            val = self.memory.pop()
            val -= 1
            self.memory.push(val)
        elif i == ")":  # INC
            val = self.memory.pop()
            val += 1
            self.memory.push(val)
        elif i == "c":  # CRD
            val = len(self.memory)
            self.memory.push(val)
        elif i == "r":  # RPL
            val = self.memory.peek()
            self.memory.push(val)
        elif i == "R":  # SRPL
            self.memory.repl()
        elif i == "!":  # NBF
            pass
        elif i == "~":  # NBW
            val = self.memory.pop()
            val = ~val
            self.memory.push(val)
        elif i == "p" or i == "P":  # POP
            val = self.memory.pop()
        elif i == "o":  # POPO
            val = self.memory.pop()
            print(val)
        elif i == "O":  # POPS
            while len(self.memory) > 0:
                print(self.memory.pop(), end=' ')
            print('')
        elif i == "b":  # CS
            val = self.memory.pop()
            val = chr(val)
            self.memory.push(val)
        elif i == "n":  # CN
            val = self.memory.pop()
            for c in val[::-1]:
                self.memory.push(ord(c))
        elif i == "B":  # CSS
            nums = []
            while type(self.memory.peek()) == int:
                nums.append(self.memory.pop())
            val = ''.join([chr(x) for x in nums])
            self.memory.push(val)

        # BINARY OPERATIONS #

        elif i in binary_ops:
            a = self.memory.pop()
            b = self.memory.pop()
            self.memory.push(binary_ops[i](a, b))
        # STACK OPERATIONS #

        elif i == "U":  # SUP
            self.memory.sUp()
        elif i == "D":  # SDN
            self.memory.sDown()
        elif i == "u":  # RUP
            self.memory.rUp()
        elif i == "d":  # RDN
            self.memory.rDn()
        elif i == "s":  # SWUP
            self.memory.swUp()
        elif i == "w":  # SWDN
            self.memory.swDown()

        elif i == " ":  # NOP
            pass
        elif i == "#":
            while len(self.memory) > 0:
                print(self.memory.pop(), end=' ')
            print('')
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
