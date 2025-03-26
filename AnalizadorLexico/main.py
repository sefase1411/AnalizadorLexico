import sys
from lexer import tokenize
from parser import Parser
from ast_utility import (
    visualize_ast, generate_json_output, validate_json, save_ast_graph, to_json
)

def analyze_file(filename):
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return None, [str(e)]

    try:
        tokens = tokenize(source_code)
    except Exception as e:
        print(f"Error durante la tokenización: {str(e)}")
        return None, [str(e)]

    print("=== Tokens ===")
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    ast = parser.parse()
    errors = parser.errors

    if errors:
        print("Errores de parsing:")
        for error in errors:
            print(f"  - {error}")
        return ast, errors

    # AST generado correctamente
    generate_json_output(ast)
    validate_json()
    return ast, []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.gox")
        sys.exit(1)

    filename = sys.argv[1]
    ast, errors = analyze_file(filename)

    if not ast or errors:
        print(f"Se encontraron {len(errors)} errores. Abortando.")
        sys.exit(1)

    try:
        '''visualize_ast(ast, filename="ast_output")'''
        save_ast_graph(ast, output_file="ast_graph.png")
    except Exception as e:
        print(f"Error al visualizar o exportar el AST: {e}")
