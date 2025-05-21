# vm.py

class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.globals = {}
        self.functions = {}
        self.ip = 0
        self.instructions = []
        self.labels = {}

    def load_ir(self, filename):
        with open(filename) as f:
            lines = [line.strip() for line in f if line.strip()]

        current_func = None
        for line in lines:
            if line.startswith("FUNCTION"):
                current_func = line.split()[1]
                self.functions[current_func] = []
            elif current_func:
                self.functions[current_func].append(line)

    def run(self, func_name="main"):
        self.instructions = self.functions.get(func_name, [])
        self.ip = 0
        while self.ip < len(self.instructions):
            parts = self.instructions[self.ip].split()
            op = parts[0]
            args = parts[1:]
            self.execute(op, args)
            self.ip += 1

    def execute(self, op, args):
        if op == "PUSHI":
            self.stack.append(int(args[0]))
        elif op == "CONSTI":
            self.stack.append(int(args[0]))
        elif op == "PRINTI":
            print(self.stack.pop())
        elif op == "PRINTB":
            print(chr(self.stack.pop()), end='')
        elif op == "ADDI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a + b)
        elif op == "SUBI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a - b)
        elif op == "MULI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a * b)
        elif op == "DIVI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(a // b)
        elif op == "EQI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a == b))
        elif op == "NEI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a != b))
        elif op == "LTI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a < b))
        elif op == "LEI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a <= b))
        elif op == "GTI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a > b))
        elif op == "GEI":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(int(a >= b))
        elif op == "GLOBAL_SET":
            self.globals[args[0]] = self.stack.pop()
        elif op == "GLOBAL_GET":
            self.stack.append(self.globals.get(args[0], 0))
        elif op == "CALL":
            # Save state
            return_ip = self.ip
            self.run(args[0])
            self.ip = return_ip
        elif op == "RET":
            self.ip = len(self.instructions)  # finish current run
        elif op == "IF":
            if self.stack.pop() == 0:
                # Skip to ELSE or ENDIF
                nest = 1
                while nest > 0:
                    self.ip += 1
                    if self.instructions[self.ip] == "IF":
                        nest += 1
                    elif self.instructions[self.ip] == "ENDIF":
                        nest -= 1
                    elif self.instructions[self.ip] == "ELSE" and nest == 1:
                        break
        elif op == "ELSE":
            # Skip to ENDIF
            while self.instructions[self.ip] != "ENDIF":
                self.ip += 1
        elif op == "ENDIF":
            pass
        elif op == "LOOP":
            self.loop_start = self.ip
        elif op == "CBREAK":
            if self.stack.pop() == 0:
                # Exit loop, skip to ENDLOOP
                nest = 1
                while nest > 0:
                    self.ip += 1
                    if self.instructions[self.ip] == "LOOP":
                        nest += 1
                    elif self.instructions[self.ip] == "ENDLOOP":
                        nest -= 1
        elif op == "ENDLOOP":
            self.ip = self.loop_start - 1
        elif op == "CONTINUE":
            self.ip = self.loop_start - 1

if __name__ == "__main__":
    vm = VirtualMachine()
    vm.load_ir("output.ir")
    vm.run("main")
