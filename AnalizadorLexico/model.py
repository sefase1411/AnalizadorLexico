# model.py
from graphviz import Digraph

# ───────────────────────────────────────────
#  Clase base con uid y posición de fuente
# ───────────────────────────────────────────
class ASTNode:
    _uid_counter = 0

    def __init__(self, *, pos=None):
        self.uid = ASTNode._uid_counter
        ASTNode._uid_counter += 1
        self.pos = pos

    def get_children(self):
        return []

    def get_label(self):
        return self.__class__.__name__

    def accept(self, visitor, context):
        method_name = 'visit_' + self.__class__.__name__
        method = getattr(visitor, method_name, visitor.generic_visit)
        return method(self, context)

    def to_dict(self):
        result = {
            "type": self.__class__.__name__,
            "kind": self.__class__.__name__,
            "uid": self.uid
        }
        if self.pos:
            line, col = self.pos
            result["pos"] = {"line": line, "col": col}

        for attr, value in self.__dict__.items():
            if attr in {"uid", "pos"}:
                continue
            if isinstance(value, ASTNode):
                result[attr] = value.to_dict()
            elif isinstance(value, list):
                result[attr] = [
                    v.to_dict() if isinstance(v, ASTNode) else v
                    for v in value
                ]
            else:
                result[attr] = value
                if attr == "type":
                    result["dtype"] = value
        return result

class Program(ASTNode):
    def __init__(self, decls, *, pos=None):
        super().__init__(pos=pos)
        self.decls = decls
    def get_children(self):
        return self.decls
    def get_label(self):
        return "Program"

class FunctionDef(ASTNode):
    def __init__(self, name, params, body, return_type=None, *, pos=None):
        super().__init__(pos=pos)
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type
    def get_children(self):
        return [c for c in (self.params, self.body) if c]
    def get_label(self):
        return f"FunctionDef({self.name})"

class ParamList(ASTNode):
    def __init__(self, params, *, pos=None):
        super().__init__(pos=pos)
        self.params = params or []
    def get_children(self):
        return self.params
    def get_label(self):
        return "ParamList"

class Param(ASTNode):
    def __init__(self, type_name, name, *, pos=None):
        super().__init__(pos=pos)
        self.type = type_name
        self.name = name
    def get_label(self):
        return f"Param({self.name}:{self.type})"

class Block(ASTNode):
    def __init__(self, statements, *, pos=None):
        super().__init__(pos=pos)
        self.statements = statements or []
    def get_children(self):
        return self.statements
    def get_label(self):
        return "Block"

class Literal(ASTNode):
    def __init__(self, dtype, value, *, pos=None):
        super().__init__(pos=pos)
        self.dtype = dtype
        self.value = value
    def get_label(self):
        return f"{self.value}"

class TrueLiteral(Literal):
    def __init__(self, *, pos=None):
        super().__init__("bool", True, pos=pos)
    def get_label(self):
        return "true"

class FalseLiteral(Literal):
    def __init__(self, *, pos=None):
        super().__init__("bool", False, pos=pos)
    def get_label(self):
        return "false"

class String(ASTNode):
    def __init__(self, value, *, pos=None):
        super().__init__(pos=pos)
        self.value = value
    def get_label(self):
        return f"String({self.value})"

class Number(ASTNode):
    def __init__(self, value, *, pos=None):
        super().__init__(pos=pos)
        self.value = value
    def get_label(self):
        return f"{self.value}"
    

class Char(ASTNode):
    def __init__(self, value, *, pos=None):
        super().__init__(pos=pos)
        self.value = value       
    def get_children(self):
        return []
    def get_label(self):
        return f"Char('{self.value}')"


class FunctionCall(ASTNode):
    def __init__(self, name, arguments, *, pos=None):
        super().__init__(pos=pos)
        self.name = name
        self.arguments = arguments or []
    def get_children(self):
        return self.arguments
    def get_label(self):
        return f"Call({self.name})"

class VarDecl(ASTNode):
    def __init__(self, type_name, name, init_expr=None, *, pos=None):
        super().__init__(pos=pos)
        self.type = type_name
        self.name = name
        self.init_expr = init_expr
    def get_children(self):
        return [self.init_expr] if self.init_expr else []
    def get_label(self):
        return f"VarDecl({self.name}:{self.type})"

class Assign(ASTNode):
    def __init__(self, name, expr, *, pos=None):
        super().__init__(pos=pos)
        self.name = name
        self.expr = expr
    def get_children(self):
        return [VarRef(self.name), self.expr] if self.expr else [VarRef(self.name)]
    def get_label(self):
        return "Assign"

class Print(ASTNode):
    def __init__(self, expr, *, pos=None):
        super().__init__(pos=pos)
        self.expr = expr
    def get_children(self):
        return [self.expr] if self.expr else []
    def get_label(self):
        return "Print"

class If(ASTNode):
    def __init__(self, condition, then_block, else_block=None, *, pos=None):
        super().__init__(pos=pos)
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

class While(ASTNode):
    def __init__(self, condition, body, *, pos=None):
        super().__init__(pos=pos)
        self.condition = condition
        self.body = body
    def get_children(self):
        return [self.condition, self.body]
    def get_label(self):
        return "While"

class Return(ASTNode):
    def __init__(self, expr=None, *, pos=None):
        super().__init__(pos=pos)
        self.expr = expr
    def get_children(self):
        return [self.expr] if self.expr else []
    def get_label(self):
        return "Return"

class BinOp(ASTNode):
    def __init__(self, op, left, right, *, pos=None):
        super().__init__(pos=pos)
        self.op = op
        self.left = left
        self.right = right
    def get_children(self):
        return [self.left, self.right]
    def get_label(self):
        return f"Op({self.op})"

class UnaryOp(ASTNode):
    def __init__(self, op, expr, *, pos=None):
        super().__init__(pos=pos)
        self.op = op
        self.expr = expr
    def get_children(self):
        return [self.expr]
    def get_label(self):
        return f"UnaryOp({self.op})"

class VarRef(ASTNode):
    def __init__(self, name, *, pos=None):
        super().__init__(pos=pos)
        self.name = name
    def get_label(self):
        return f"VarRef({self.name})"

class Break(ASTNode):
    def __init__(self, *, pos=None):
        super().__init__(pos=pos)
    def get_label(self):
        return "Break"

class Continue(ASTNode):
    def __init__(self, *, pos=None):
        super().__init__(pos=pos)
    def get_label(self):
        return "Continue"

# ───────────────────────────────────────────
#  Utilidades de visualización (sin cambios)
# ───────────────────────────────────────────
def generate_ast_graph(node):
    dot = Digraph(name="AST", comment="Abstract Syntax Tree")
    counter = {"id": 0}

    def add_node(n):
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
    dot = generate_ast_graph(node)
    dot.format = 'png'
    output_path = dot.render(filename, cleanup=True)
    print(f" AST generado como imagen: {output_path}")
    return output_path

def ast_to_dict(node):
    if node is None:
        return None
    if isinstance(node, list):
        return [ast_to_dict(n) for n in node]
    return node.to_dict()
