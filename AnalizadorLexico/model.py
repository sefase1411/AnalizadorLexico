from graphviz import Digraph

# Clase base para nodos del AST
class ASTNode:
    def get_children(self):
        """Devuelve la lista de nodos hijo (sobrescribir en clases derivadas si aplica)."""
        return []
    def get_label(self):
        """Devuelve la etiqueta para visualizar el nodo (sobrescribir en clases derivadas si se requiere)."""
        return self.__class__.__name__

# Nodo Program: raíz del AST, contiene declaraciones globales (p.ej. funciones)
class Program(ASTNode):
    def __init__(self, decls):
        self.decls = decls  # lista de nodos (funciones u otras declaraciones)
    def get_children(self):
        return self.decls
    def get_label(self):
        return "Program"

# Nodo FunctionDef: definición de una función con nombre, parámetros y cuerpo
class FunctionDef(ASTNode):
    def __init__(self, name, params, body):
        self.name = name            # nombre de la función
        self.params = params        # nodo ParamList con la lista de parámetros
        self.body = body            # nodo Block con el cuerpo de la función
    def get_children(self):
        children = []
        if self.params is not None:
            children.append(self.params)
        if self.body is not None:
            children.append(self.body)
        return children
    def get_label(self):
        return f"FunctionDef({self.name})"

# Nodo ParamList: agrupa múltiples parámetros de función
class ParamList(ASTNode):
    def __init__(self, params):
        self.params = params or []  # lista de nodos Param
    def get_children(self):
        return self.params
    def get_label(self):
        return "ParamList"

# Nodo Param: representa un parámetro (tipo y nombre)
class Param(ASTNode):
    def __init__(self, type_name, name):
        self.type = type_name  # tipo (p.ej. "int")
        self.name = name       # nombre del parámetro
    def get_children(self):
        return []
    def get_label(self):
        return f"Param({self.name}:{self.type})"

# Nodo Block: representa un bloque de código { ... } con múltiples sentencias
class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements or []  # lista de sentencias (nodos AST)
    def get_children(self):
        return self.statements
    def get_label(self):
        return "Block"

# Nodo VarDecl: declaración de variable (tipo, nombre, expresión opcional de inicialización)
class VarDecl(ASTNode):
    def __init__(self, type_name, name, init_expr=None):
        self.type = type_name
        self.name = name
        self.init_expr = init_expr  # nodo de expresión inicial (o None si no hay)
    def get_children(self):
        return [self.init_expr] if self.init_expr is not None else []
    def get_label(self):
        return f"VarDecl({self.name}:{self.type})"

# Nodo Assign: asignación a una variable existente (nombre = expresión)
class Assign(ASTNode):
    def __init__(self, name, expr):
        self.name = name    # nombre de la variable a asignar
        self.expr = expr    # nodo de la expresión asignada
    def get_children(self):
        # Representamos la asignación con dos hijos: el nombre (como nodo VarRef) y la expresión
        return [VarRef(self.name), self.expr]
    def get_label(self):
        return "Assign"

# Nodo If: sentencia if (condición, bloque then, bloque else opcional)
class If(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition   # nodo expresión condicional
        self.then_block = then_block # nodo Block para la rama then
        self.else_block = else_block # nodo Block para la rama else (o None)
    def get_children(self):
        children = []
        if self.condition:
            children.append(self.condition)
        if self.then_block:
            children.append(self.then_block)
        if self.else_block:
            children.append(self.else_block)
        return children
    def get_label(self):
        return "If"

# Nodo While: bucle while (condición, cuerpo)
class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition  # nodo expresión condicional
        self.body = body            # nodo Block con el cuerpo del bucle
    def get_children(self):
        children = []
        if self.condition:
            children.append(self.condition)
        if self.body:
            children.append(self.body)
        return children
    def get_label(self):
        return "While"

# Nodo Return: sentencia return con una expresión opcional
class Return(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr  # nodo expresión a retornar (None si no hay valor)
    def get_children(self):
        return [self.expr] if self.expr is not None else []
    def get_label(self):
        return "Return"

# Nodo BinOp: operación binaria (aritmética o relacional) con operador, operando izquierdo y derecho
class BinOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op      # símbolo del operador (p.ej. '+', '>', '==', etc.)
        self.left = left  # nodo operando izquierdo
        self.right = right# nodo operando derecho
    def get_children(self):
        return [self.left, self.right]
    def get_label(self):
        return f"Op({self.op})"

# Nodo UnaryOp: operación unaria (por ejemplo, negación)
class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op    # símbolo del operador unario (p.ej. '-')
        self.expr = expr# nodo de la expresión operando
    def get_children(self):
        return [self.expr]
    def get_label(self):
        return f"UnaryOp({self.op})"

# Nodo VarRef: referencia/uso de una variable existente
class VarRef(ASTNode):
    def __init__(self, name):
        self.name = name  # nombre de la variable referenciada
    def get_children(self):
        return []
    def get_label(self):
        return str(self.name)

# Nodo Number: constante numérica entera
class Number(ASTNode):
    def __init__(self, value):
        self.value = value  # valor entero
    def get_children(self):
        return []
    def get_label(self):
        return str(self.value)

# --- Funciones para visualización del AST en formato gráfico ---

def generate_ast_graph(node):
    """Genera un grafo dirigido (Graphviz Digraph) a partir de un nodo AST dado."""
    dot = Digraph(name="AST", comment="Abstract Syntax Tree")
    counter = {"id": 0}
    def add_node(n):
        # Asigna un identificador único para cada nodo y lo añade al grafo
        nid = counter["id"]
        counter["id"] += 1
        label = n.get_label() if n is not None else "None"
        dot.node(str(nid), label)
        if n is not None:
            for child in n.get_children():
                cid = add_node(child)
                dot.edge(str(nid), str(cid))
        return nid
    add_node(node)
    return dot

def visualize_ast(node, filename="ast"):
    """Genera un archivo gráfico del AST y lo muestra si es posible."""
    dot = generate_ast_graph(node)
    dot.format = 'pdf'   # formato de salida (puede cambiarse a 'png' si se prefiere imagen)
    output_path = dot.render(filename, view=False)
    try:
        dot.view()  # intenta abrir el PDF generado con el visor predeterminado
    except:
        print(f"AST guardado en {output_path}")
    return output_path
