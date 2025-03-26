import ply.lex as lex

# Definiciones de tokens y reglas del lexer

tokens = [
    'ID', 'NUMBER', 'STRING',
    'RETURN', 'IF', 'ELSE', 'WHILE', 'FUNC', 'INT', 'BOOL', 'VAR', 'PRINT', 'TRUE', 'FALSE',
    'EQ', 'NE', 'GE', 'LE', 'GT', 'LT', 'ASSIGN'
]

# Caracteres literales
literals = ['+', '-', '*', '/', '(', ')', '{', '}', ';', ',', '%']

# Palabras reservadas
reserved = {
    'return': 'RETURN',
    'if':     'IF',
    'else':   'ELSE',
    'while':  'WHILE',
    'func':   'FUNC',
    'int':    'INT',
    'bool':   'BOOL',
    'var':    'VAR',
    'print':  'PRINT',
    'true':   'TRUE',
    'false':  'FALSE'
}

# Reglas de expresiones regulares para tokens multi-caracter
t_EQ     = r'=='
t_NE     = r'!='
t_GE     = r'>='
t_LE     = r'<='
t_ASSIGN = r'='
t_GT     = r'>'
t_LT     = r'<'

# Caracteres a ignorar (espacios y tabs)
t_ignore = ' \t'


def t_COMMENT(t):
    r'//.*'
    pass  # Ignora comentarios de línea

def t_MULTILINE_COMMENT(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

# Token para números (enteros)
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Token para cadenas de texto
def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]  # Remover las comillas
    return t

# Token para identificadores y palabras reservadas
def t_ID(t):
    r'[A-Za-z_]\w*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Manejo de nuevas líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Verificar comentarios no cerrados
def check_unterminated_comment(source_code):
    open_comment = source_code.find("/*")
    close_comment = source_code.find("*/", open_comment + 2)
    if open_comment != -1 and close_comment == -1:
        line_number = source_code[:open_comment].count("\n") + 1
        raise SyntaxError(f"Línea {line_number}: Comentario no terminado")

# Manejo de errores léxicos
def t_error(t):
    print(f"[Lexer] Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir el analizador léxico
lexer = lex.lex()


def tokenize(source_code):
    """
    Tokeniza el código fuente y devuelve una lista de tokens.
    Cada token es una tupla (tipo, valor, línea).
    """
    check_unterminated_comment(source_code)
    lexer.input(source_code)
    tokens = []
    for tok in lexer:
        tokens.append((tok.type, tok.value, tok.lineno))
    tokens.append(('EOF', '', lexer.lineno))  # Agregar EOF para compatibilidad
    return tokens
