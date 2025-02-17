import re

# Definir los tokens
TOKENS = [
    # Palabras reservadas
    ('CONST', r'\bconst\b'),
    ('VAR', r'\bvar\b'),
    ('PRINT', r'\bprint\b'),
    ('RETURN', r'\breturn\b'),
    ('BREAK', r'\bbreak\b'),
    ('CONTINUE', r'\bcontinue\b'),
    ('IF', r'\bif\b'),
    ('ELSE', r'\belse\b'),
    ('WHILE', r'\bwhile\b'),
    ('FUNC', r'\bfunc\b'),
    ('IMPORT', r'\bimport\b'),
    ('TRUE', r'\btrue\b'),
    ('FALSE', r'\bfalse\b'),

    # Identificadores
    ('ID', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),

    # Literales
    ('INTEGER', r'\b\d+\b'),
    ('FLOAT', r'\b\d+\.\d+\b'),
    ('CHAR', r"'(\\.|[^'\\])'"),
    ('STRING', r'"[^"\n]*"'),

    # Operadores
    ('PLUS', r'\+'),
    ('MINUS', r'-'),
    ('TIMES', r'\*'),
    ('DIVIDE', r'/'),
    ('MOD', r'%'),
    ('LT', r'<'),
    ('LE', r'<='),
    ('GT', r'>'),
    ('GE', r'>='),
    ('EQ', r'=='),
    ('NE', r'!='),
    ('LAND', r'&&'),
    ('LOR', r'\|\|'),
    ('GROW', r'\^'),

    # Símbolos misceláneos
    ('ASSIGN', r'='),
    ('SEMI', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('COMMA', r','),
    ('DEREF', r'`'),

    # Comentarios
    ('COMMENT', r'//.*'),  # Comentarios de una línea
    ('MULTILINE_COMMENT', r'/\*[\s\S]*?\*/'),  # Comentarios cerrados correctamente

    # Espacios en blanco
    ('WHITESPACE', r'\s+'),
]

# Función para verificar comentarios no terminados
def check_unterminated_comment(code):
    """Lanza un error si hay un comentario de bloque sin cerrar."""
    open_comment = code.find("/*")
    close_comment = code.find("*/", open_comment + 2)

    if open_comment != -1 and close_comment == -1:
        line_number = code[:open_comment].count("\n") + 1
        raise SyntaxError(f"Línea {line_number}: Comentario no terminado")

# Función para tokenizar
def tokenize(code):
    check_unterminated_comment(code)  # Verificar si hay comentarios sin cerrar antes de tokenizar

    tokens = []
    lineno = 1
    position = 0
    token_regex = [(name, re.compile(pattern, re.DOTALL)) for name, pattern in TOKENS]

    while position < len(code):
        match = None
        for token_name, regex in token_regex:
            match = regex.match(code, position)
            if match:
                value = match.group(0)

                # Ignorar comentarios y espacios en blanco
                if token_name not in ['COMMENT', 'MULTILINE_COMMENT', 'WHITESPACE']:
                    tokens.append((token_name, value, lineno))

                # Actualizar la posición y contar nuevas líneas
                lineno += value.count('\n')
                position = match.end()
                break
        
        # Si no se encontró un token válido, lanzar error
        if not match:
            raise SyntaxError(f"Línea {lineno}: Caracter ilegal '{code[position]}'")
    
    return tokens

# Leer el archivo .gox
def read_gox_file(filename):
    """Lee el contenido de un archivo .gox y lo retorna como una cadena."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filename}")
        exit(1)

# uso en el archivo factorizre.gox
if __name__ == "__main__":
    try:
        # Leer el archivo .gox
        code = read_gox_file("factorize.gox")
        
        # Tokenizar el código
        tokens = tokenize(code)
        
        # Imprimir los tokens obtenidos
        for token in tokens:
            print(token)
    except SyntaxError as e:
        print(e)
