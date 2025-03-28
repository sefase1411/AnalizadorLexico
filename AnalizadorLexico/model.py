from graphviz import Digraph


class ASTNode:
    def get_children(self):
        """Devuelve la lista de nodos hijo (sobrescribir en clases derivadas si aplica)."""
        return []
    def get_label(self):
        """Devuelve la etiqueta para visualizar el nodo (sobrescribir en clases derivadas si se requiere)."""
        return self.__class__.__name__


class Program(ASTNode):
    def __init__(self, decls):
        self.decls = decls
    def get_children(self):
        return self.decls
    def get_label(self):
        return "Program"

class FunctionDef(ASTNode):  # <- hereda de ASTNode ahora
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type
    def get_children(self):
        return [child for child in [self.params, self.body] if child]
    def get_label(self):
        return f"FunctionDef({self.name})"

# Nodo ParamList: agrupa múltiples parámetros de función
class ParamList(ASTNode):
    def __init__(self, params):
        self.params = params or []
    def get_children(self):
        return self.params
    def get_label(self):
        return "ParamList"

# Nodo Param: representa un parámetro (tipo y nombre)
class Param(ASTNode):
    def __init__(self, type_name, name):
        self.type = type_name
        self.name = name
    def get_label(self):
        return f"Param({self.name}:{self.type})"

# Nodo Block: representa un bloque de código { ... } con múltiples sentencias
class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements or []
    def get_children(self):
        return self.statements
    def get_label(self):
        return "Block"

class TrueLiteral(ASTNode):
    def get_label(self):
        return "true"

class FalseLiteral(ASTNode):
    def get_label(self):
        return "false"

class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments
    def get_children(self):
        return self.arguments
    def get_label(self):
        return f"Call({self.name})"

class VarDecl(ASTNode):
    def __init__(self, type_name, name, init_expr=None):
        self.type = type_name
        self.name = name
        self.init_expr = init_expr
    def get_children(self):
        return [self.init_expr] if self.init_expr else []
    def get_label(self):
        return f"VarDecl({self.name}:{self.type})"

# Nodo Assign: asignación a una variable existente (nombre = expresión)
class Assign(ASTNode):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    def get_children(self):
        # Representamos la asignación con dos hijos: el nombre (como nodo VarRef) y la expresión
        return [VarRef(self.name), self.expr]
    def get_label(self):
        return "Assign"

class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def get_children(self):
        return [self.expr]
    def get_label(self):
        return "Print"

class String(ASTNode):
    def __init__(self, value):
        self.value = value
    def get_label(self):
        return f"String({self.value})"

class If(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
    def get_children(self):
        children = [self.condition, self.then_block]
        if self.else_block:
            children.append(self.else_block)
        return children
    def get_label(self):
        return "If"

# Nodo While: bucle while (condición, cuerpo)
class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def get_children(self):
        return [self.condition, self.body]
    def get_label(self):
        return "While"

# Nodo Return: sentencia return con una expresión opcional
class Return(ASTNode):
    def __init__(self, expr=None):
        self.expr = expr
    def get_children(self):
        return [self.expr] if self.expr else []
    def get_label(self):
        return "Return"

# Nodo BinOp: operación binaria (aritmética o relacional) con operador, operando izquierdo y derecho
class BinOp(ASTNode):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def get_children(self):
        return [self.left, self.right]
    def get_label(self):
        return f"Op({self.op})"

# Nodo UnaryOp: operación unaria (por ejemplo, negación)
class UnaryOp(ASTNode):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def get_children(self):
        return [self.expr]
    def get_label(self):
        return f"UnaryOp({self.op})"

# Nodo VarRef: referencia/uso de una variable existente
class VarRef(ASTNode):
    def __init__(self, name):
        self.name = name
    def get_label(self):
        return f"VarRef({self.name})"

# Nodo Number: constante numérica entera
class Number(ASTNode):
    def __init__(self, value):
        self.value = value
    def get_label(self):
        return f"{self.value}"


def generate_ast_graph(node):
    """Genera un grafo dirigido (Graphviz Digraph) a partir de un nodo AST dado."""
    dot = Digraph(name="AST", comment="Abstract Syntax Tree")
    counter = {"id": 0}
    def add_node(n):
        # Asigna un identificador único para cada nodo y lo añade al grafo
        nid = counter["id"]
        counter["id"] += 1
        label = n.get_label() if n else "None"
        dot.node(str(nid), label)
        if n:
            for child in n.get_children():
                cid = add_node(child)
                dot.edge(str(nid), str(cid))
        return nid
    add_node(node)
    return dot

def visualize_ast(node, filename="ast_output"):
    """
    Genera una imagen PNG del AST y la guarda con el nombre indicado.
    """
    dot = generate_ast_graph(node)
    dot.format = 'png'  # <- PNG en vez de PDF
    output_path = dot.render(filename, cleanup=True)
    print(f" AST generado como imagen: {output_path}")
    return output_path

