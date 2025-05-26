# test_direct.py - Test directo
import sys
from lexer import tokenize
from parser import Parser
from check import Checker
from ircode import IRCodeGenerator
from stack_machine import StackMachine

# Código de prueba
code = """
var x int = 42;
print x;
"""

print("1. Tokenizando...")
tokens = tokenize(code)
print(f"   Tokens: {len(tokens)}")

print("2. Parseando...")
parser = Parser(tokens)
ast = parser.parse()
print(f"   AST: {len(ast.decls)} declaraciones")

print("3. Análisis semántico...")
checker = Checker()
errores = checker.check(ast)
print(f"   Errores: {len(errores)}")

print("4. Generando IR...")
ir_generator = IRCodeGenerator()
module_ir = ir_generator.generate(ast.decls)
ir_content = module_ir.dump()

print("5. IR generado:")
print(ir_content)

print("6. Ejecutando...")
vm = StackMachine()
vm.load_ir_from_string(ir_content)
vm.run("main")