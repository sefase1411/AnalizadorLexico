import sys
import json
from lexer import tokenize
from parser import Parser
from check import Checker
from ast_utility import generate_json_output, save_ast_graph
from symtab_utility import save_symbol_table_json, print_symbol_table
import json
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
        print("Errores de parsing:")
        for err in parser.errors:
            print(f"  - {err}")
        return

    # 3. Análisis semántico
    checker = Checker()
    errores = checker.check(ast)

    # 4. Generación del AST (siempre)
    generate_json_output(ast)
    save_ast_graph(ast)

    # 5. Guardar y mostrar tabla de símbolos
    save_symbol_table_json(checker.symtab, "symbol_table.json")
    print("\n📦 Tabla de Símbolos:\n")
    print_symbol_table(checker.symtab)

    # 6. Mostrar errores semánticos si hay
    if errores:
        print("\nErrores semánticos detectados:")
        for e in errores:
            print(e)
        return

    print("\n✅ Análisis exitoso. Programa válido sintáctica y semánticamente.")

    # 7. Ejecutar el programa (si está disponible)
    try:
        from run_program import run_program
        result = run_program(ast)
        if result is not None:
            print(f"Resultado de ejecución: {result}")
    except ImportError:
        print("🔍 No se encontró el archivo run_program.py para ejecutar el programa.")

    # 8. Mostrar estructura completa del AST (para depuración)
    print("\n🧠 AST completo en JSON:\n")
    print(json.dumps(ast, default=lambda o: o.__dict__, indent=2))
    print(json.dumps(ast_to_dict(ast), indent=2))


if __name__ == "__main__":
    main()
