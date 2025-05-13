import sys
import json
from lexer import tokenize
from parser import Parser
from check import Checker
from ast_utility import generate_json_output, save_ast_graph
from symtab_utility import save_symbol_table_json, print_symbol_table
from model import ast_to_dict

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.gox")
        return

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {filepath}")
        return

    # 1. Análisis léxico
    tokens = tokenize(source)
    print("=== Tokens generados ===")
    for t in tokens:
        print(t)

    # 2. Análisis sintáctico
    parser = Parser(tokens)
    ast = parser.parse()

    if parser.errors:
        print("\nErrores de parsing:")
        for err in parser.errors:
            print(f"  - {err}")
        return

    # 3. Análisis semántico
    checker = Checker()
    errores = checker.check(ast)

    # 4. Generación del AST
    generate_json_output(ast)
    save_ast_graph(ast)

    # 5. Mostrar y guardar tabla de símbolos (sin tablas vacías)
    print("\n📦 Tabla de Símbolos:\n")
    def print_nonempty(env):
        if env.entries:
            print_symbol_table(env)
        for child in env.children:
            print_nonempty(child)

    print_nonempty(checker.symtab)
    save_symbol_table_json(checker.symtab)

    # 6. Mostrar errores semánticos detallados
    if checker.errors:
        print("\nErrores semánticos detectados:")
        for err in checker.errors:
            print(err)  # Ahora usa __str__ de SemanticError
        return

    print("\n✅ Análisis exitoso. Programa válido sintáctica y semánticamente.")

    # (Opcional) AST completo para depuración
    '''
    print("\nAST completo en JSON:\n")
    print(json.dumps(ast_to_dict(ast), indent=2))
    '''

if __name__ == "__main__":
    main()
