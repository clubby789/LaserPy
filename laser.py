"""A Python implementation of LaserLang"""
import argparse
import operator
import sys

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


def stack_string(self):
    """
    Casts a sequence of integers from the top of the stack to a string
    """
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
               "n": lambda self: [self.memory.push(ord(c))
                                  for c in self.memory.pop()[::-1]],
               "B": stack_string,
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

mirror_ops = {"\\": [WEST, NORTH, EAST, SOUTH],
              "/": [EAST, SOUTH, WEST, NORTH],
              ">": [EAST, WEST, EAST, EAST],
              "v": [NORTH, SOUTH, SOUTH, SOUTH],
              "<": [WEST, WEST, WEST, EAST],
              "^": [NORTH, NORTH, SOUTH, NORTH],
              "⌞": [EAST, NORTH, EAST, NORTH],
              "⌜": [EAST, SOUTH, EAST, SOUTH],
              "⌟": [WEST, NORTH, WEST, NORTH],
              "⌝": [WEST, SOUTH, WEST, SOUTH]}


class LaserStack:
    """
    Performs the stack operations required by Laser
    """
    contents = [[]]
    addr = 0

    def pop(self):
        """Pops the top element off the current stack"""
        if len(self.contents[self.addr]) == 0:
            print("Error: pop from empty stack")
            sys.exit(-1)
        return self.contents[self.addr].pop()

    def push(self, item):
        """Pushes an element to the current stack, casting to an int
        if numeric"""
        if isinstance(item, str) and item.isnumeric():
            item = int(item)
        self.contents[self.addr].append(item)

    def peek(self):
        """Returns the top element from the current stack"""
        if len(self.contents[self.addr]) == 0:
            return 0
        return self.contents[self.addr][-1]

    def s_up(self):
        """Moves up 1 stack"""
        self.addr += 1
        if self.addr == len(self.contents):
            # Top of the stack
            self.contents.append([])

    def s_down(self):
        """Moves down 1 stack"""
        self.addr -= 1

    def sw_up(self):
        """Moves the top element off the current stack to the next stack up"""
        temp = self.contents[self.addr].pop()
        if self.addr == len(self.contents) - 1:
            self.contents.append([])
        self.contents[self.addr + 1].append(temp)

    def sw_down(self):
        """Moves the top element of the current stack to the next stack down"""
        temp = self.contents[self.addr].pop()
        self.contents[self.addr - 1].append(temp)

    def r_up(self):
        """Moves the bottom element of the current stack to the top"""
        temp = self.contents[self.addr].pop(0)
        self.contents[self.addr].append(temp)

    def r_down(self):
        """Moves the top element of the current stack to the bottom"""
        temp = self.contents[self.addr].pop()
        self.contents[self.addr].insert(0, temp)

    def repl(self):
        """Replicate the current stack"""
        temp = list(self.contents[self.addr])
        self.contents.insert(self.addr, temp)

    def printself(self):
        """Prints the current stack"""
        while len(self) > 0:
            print(self.pop(), end=' ')
        print()

    def __repr__(self):
        return repr(self.contents[self.addr][::-1])

    def __len__(self):
        return len(self.contents[self.addr])


class LaserMachine:
    """A Laser 'VM' for intepreting a program"""
    # pylint: disable=too-many-instance-attributes
    # There's a lot to keep track of
    def __init__(self, prog, verbose=False, init=None):
        self.direction = EAST
        self.memory = LaserStack()
        self.parse_mode = INSTRUCTION
        self.current_string = ""
        self.verbose = verbose
        lines = prog.split('\n')
        self.prog = []
        self.width = max(map(len, lines))
        self.height = len(lines)
        for line in lines:
            self.prog.append(list(line.ljust(self.width)))
        self.program_counter = [0, self.height - 1]
        if isinstance(init, list):
            for var in init[::-1]:
                self.memory.push(var)
        if verbose:
            for line in self.prog:
                print(''.join(line))
            self.debug()

    def debug(self):
        """Print some debug info"""
        print(f"addr: {self.memory.addr} - "
              f"stack: {self.memory}"
              )

    def do_step(self):
        """Performs a single step of the machine"""
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
        x_mov, y_mov = self.direction[0], self.direction[1]
        self.program_counter[0] += x_mov
        self.program_counter[1] += y_mov
        if self.program_counter[0] == self.width:
            self.program_counter[0] = 0
        elif self.program_counter[0] == -1:
            self.program_counter[0] = self.width - 1

        if self.program_counter[1] == self.height:
            self.program_counter[1] = 0
        elif self.program_counter[1] == -1:
            self.program_counter[1] = self.height - 1
        if self.verbose:
            self.debug()
        return True

    def fetch_item(self):
        """Fetches the character at the current PC"""
        x_pos = self.program_counter[0]
        y_pos = self.height - self.program_counter[1] - 1
        return self.prog[y_pos][x_pos]

    def process_instruction(self, i):
        """
        Handle an instruction character
        """
        if i == '"':
            self.parse_mode = STRING
        elif i == '`':
            self.parse_mode = RAW

        # NULLARY OPERATIONS (NO ARGUMENTS) #
        elif i in nullary_ops:
            nullary_ops[i](self)

        # UNARY OPERATIONS #
        elif i in unary_ops:
            temp = self.memory.pop()
            self.memory.push(unary_ops[i](temp))

        # BINARY OPERATIONS #
        elif i in binary_ops:
            temp_a = self.memory.pop()
            temp_b = self.memory.pop()
            self.memory.push(binary_ops[i](temp_a, temp_b))

        # STACK OPERATIONS #
        elif i in stack_ops:
            stack_ops[i](self)

        # TERMINATE
        elif i == "#":
            self.memory.printself()
            sys.exit(0)
        else:
            print(f"Instruction {i} unknown!")
            sys.exit(-1)

    def process_string(self, i):
        """Process input while in string mode"""
        if i in ('"', '`'):
            self.memory.push(self.current_string)
            self.current_string = ""
            self.parse_mode = INSTRUCTION
        else:
            self.current_string += i

    def switch_direction(self, mirror):
        """Process a mirror and switch direction"""
        if mirror in CONDITIONALS:
            if self.memory.peek() != 0:
                return

        directions = [NORTH, WEST, SOUTH, EAST]
        self.direction = mirror_ops[mirror][directions.index(self.direction)]


parser = argparse.ArgumentParser(description='Run a LaserLang program.')
parser.add_argument("-v", "--verbose", action="store_true",
                    default=False, help="verbose output")
parser.add_argument("program", help="Laser program to run")
parser.add_argument("input", help="Items to initialize stack with",
                    nargs='*')
args = parser.parse_args()

with open(args.program, 'r') as f:
    program = f.read()

LM = LaserMachine(program, verbose=args.verbose, init=args.input)
while LM.do_step():
    pass
