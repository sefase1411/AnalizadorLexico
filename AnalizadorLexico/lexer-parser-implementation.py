import sys

import ply.lex as lex
import ply.yacc as yacc
from model import *  # Importa las clases de nodos AST

# Definición de tokens
tokens = [
    'ID', 'NUMBER',
    'RETURN', 'IF', 'ELSE', 'WHILE', 'FUNC', 'INT',
    'EQ', 'NE', 'GE', 'LE', 'GT', 'LT', 'ASSIGN'
]

# Caracteres literales (operadores y símbolos de puntuación de un solo caracter)
literals = ['+', '-', '*', '/', '(', ')', '{', '}', ';', ',']

# Palabras reservadas y su token correspondiente
reserved = {
    'return': 'RETURN',
    'if':     'IF',
    'else':   'ELSE',
    'while':  'WHILE',
    'func':   'FUNC',
    'int':    'INT'
}

# Reglas de expresiones regulares para tokens multi-caracter
t_EQ = r'=='
t_NE = r'!='
t_GE = r'>='
t_LE = r'<='
t_ASSIGN = r'='   # operador de asignación
t_GT = r'>'       # operador relacional 'mayor que'
t_LT = r'<'       # operador relacional 'menor que'

# Caracteres a ignorar (espacios y tabs)
t_ignore = ' \t'

# Token para números (enteros)
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)      # convierte el lexema a entero
    return t

# Token para identificadores y palabras reservadas
def t_ID(t):
    r'[A-Za-z_]\w*'
    t.type = reserved.get(t.value, 'ID')  # verifica si es palabra clave
    return t

# Manejo de nuevas líneas (para seguimiento de número de línea)
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores léxicos
def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}' en línea {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir el analizador léxico
lexer = lex.lex()

# Precedencia de operadores (de menor a mayor prioridad)
precedence = (
    ('right', 'ELSE'),            # 'else' se asocia al 'if' más cercano (evita ambigüedad)
    ('left', 'EQ', 'NE', 'GT', 'LT', 'GE', 'LE'),  # operadores relacionales
    ('left', '+', '-'),           # suma y resta
    ('left', '*', '/'),           # multiplicación y división
    ('right', 'UMINUS'),          # operador unario (negativo)
)

# Reglas gramaticales (analizador sintáctico)

def p_program(p):
    '''program : decl_list'''
    p[0] = Program(p[1])  # Nodo raíz del AST que contiene la lista de declaraciones

def p_decl_list_multiple(p):
    '''decl_list : decl_list decl'''
    p[1].append(p[2])
    p[0] = p[1]

def p_decl_list_single(p):
    '''decl_list : decl'''
    p[0] = [p[1]]

def p_decl(p):
    '''decl : func_decl'''
    p[0] = p[1]

def p_func_decl(p):
    '''func_decl : FUNC ID '(' params_opt ')' block'''
    # p[2] es el nombre de la función, p[4] es lista de parámetros, p[6] es el bloque de código
    params_node = ParamList(p[4]) if p[4] is not None else ParamList([]) 
    p[0] = FunctionDef(p[2], params_node, p[6])

def p_params_opt(p):
    '''params_opt : param_list 
                  | '''
    # Producción opcional para parámetros (vacía o lista de parámetros)
    if len(p) == 1:
        p[0] = []  # sin parámetros
    else:
        p[0] = p[1]

def p_param_list_comma(p):
    '''param_list : param_list ',' param'''
    p[1].append(p[3])
    p[0] = p[1]

def p_param_list_single(p):
    '''param_list : param'''
    p[0] = [p[1]]

def p_param(p):
    '''param : INT ID'''
    # Declaración de un parámetro con tipo y nombre
    p[0] = Param(p[1], p[2])

def p_block(p):
    '''block : '{' stmt_list '}' '''
    p[0] = Block(p[2])  # bloque con una lista de sentencias internas

def p_block_empty(p):
    '''block : '{' '}' '''
    p[0] = Block([])    # bloque vacío

def p_stmt_list_multiple(p):
    '''stmt_list : stmt_list stmt'''
    p[1].append(p[2])
    p[0] = p[1]

def p_stmt_list_single(p):
    '''stmt_list : stmt'''
    p[0] = [p[1]]

def p_stmt(p):
    '''stmt : var_decl
            | assign_stmt
            | if_stmt
            | while_stmt
            | return_stmt'''
    p[0] = p[1]

def p_var_decl_init(p):
    '''var_decl : INT ID ASSIGN expression ';' '''
    # Declaración de variable con inicialización (p[1] tipo, p[2] nombre, p[4] expresión valor)
    p[0] = VarDecl(p[1], p[2], p[4])

def p_var_decl_noinit(p):
    '''var_decl : INT ID ';' '''
    # Declaración de variable sin valor inicial
    p[0] = VarDecl(p[1], p[2], None)

def p_assign_stmt(p):
    '''assign_stmt : ID ASSIGN expression ';' '''
    # Asignación a variable existente (p[1] nombre, p[3] expresión valor)
    p[0] = Assign(p[1], p[3])

def p_if_no_else(p):
    '''if_stmt : IF '(' expression ')' block'''
    # Sentencia if sin else
    p[0] = If(p[3], p[5], None)

def p_if_with_else(p):
    '''if_stmt : IF '(' expression ')' block ELSE block'''
    # Sentencia if con else
    p[0] = If(p[3], p[5], p[7])

def p_while(p):
    '''while_stmt : WHILE '(' expression ')' block'''
    p[0] = While(p[3], p[5])

def p_return(p):
    '''return_stmt : RETURN expression ';' '''
    p[0] = Return(p[2])

# Reglas para expresiones (operaciones aritméticas y relacionales)

def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NE expression'''
    # Operación binaria: p[2] es el operador, p[1] operando izquierdo, p[3] operando derecho
    op_symbol = p[2]
    p[0] = BinOp(op_symbol, p[1], p[3])

def p_expression_uminus(p):
    '''expression : '-' expression %prec UMINUS'''
    # Operador unario '-' (negación)
    p[0] = UnaryOp('-', p[2])

def p_expression_group(p):
    '''expression : '(' expression ')' '''
    # Sub-expresión entre paréntesis
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    # Número literal
    p[0] = Number(p[1])

def p_expression_var(p):
    '''expression : ID'''
    # Referencia a variable (identificador)
    p[0] = VarRef(p[1])

def p_error(p):
    # Manejo de errores sintácticos
    if p:
        print(f"Error de sintaxis cerca de '{p.value}' (token {p.type}) en línea {getattr(p, 'lineno', '?')}")
    else:
        print("Error de sintaxis: fin de entrada inesperado")

# Construir el parser
parser = yacc.yacc()

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Código de prueba (se puede reemplazar con otro código GoxLang de entrada)
    sample_code = """
    func sumar(int a, int b) {
        int resultado = a + b;
        if (resultado > 10) {
            resultado = resultado - 1;
        } else {
            resultado = resultado + 1;
        }
        while (resultado < 5) {
            resultado = resultado + 2;
        }
        return resultado;
    }
    """
    # Analizar el código de entrada y obtener el AST
    ast_root = parser.parse(sample_code, lexer=lexer)
    # Generar y visualizar el AST en formato gráfico
    visualize_ast(ast_root, filename="ast_output")
