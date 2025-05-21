import sys
from lexer import tokenize
from parser import Parser
from check import Checker
from ast_utility import generate_json_output, save_ast_graph
from symtab_utility import save_symbol_table_json, print_symbol_table
from ircode import IRCodeGenerator  

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.gox")
        return

    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    # 1. Léxico
    tokens = tokenize(source)

    # 2. Sintaxis
    parser = Parser(tokens)
    ast = parser.parse()
    if parser.errors:
        print("\nErrores de parsing:")
        for err in parser.errors:
            print(err)
        return

    # 3. Semántica
    checker = Checker()
    errores = checker.check(ast)
    if errores:
        print("\nErrores semánticos detectados:")
        for err in errores:
            print(err)
        return

    print("\n✅ Análisis exitoso. Generando código intermedio (IR)...")

    # 4. Generación de IR
    ir_generator = IRCodeGenerator()
    module_ir = ir_generator.generate(ast.decls)

    # 5. Mostrar y guardar IR
    print(module_ir.dump())
    with open("output.ir", "w", encoding="utf-8") as f:
        f.write(module_ir.dump())

    # 6. Salida adicional: AST y tabla de símbolos
    generate_json_output(ast)
    save_ast_graph(ast)
    save_symbol_table_json(checker.symtab)

if __name__ == "__main__":
    main()
