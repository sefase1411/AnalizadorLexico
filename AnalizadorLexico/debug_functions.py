# debug_functions.py
import sys
from lexer import tokenize
from parser import Parser
from check import Checker
from ircode import IRCodeGenerator
from stack_machine import StackMachine

code = """
func add(x int, y int) int {
    return x + y;
}

var result int = add(5, 3);
print result;
"""

print("=== DEBUG FUNCIONES ===")
tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()
checker = Checker()
errores = checker.check(ast)

ir_generator = IRCodeGenerator()
module_ir = ir_generator.generate(ast.decls)
ir_content = module_ir.dump()

print("IR GENERADO:")
print(ir_content)
print("\nEJECUTANDO...")
vm = StackMachine()
vm.load_ir_from_string(ir_content)
vm.run("main")