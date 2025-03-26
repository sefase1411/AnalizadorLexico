import json
import pydot
from graphviz import Digraph
from model import ASTNode  # Asegurate de que todos tus nodos hereden de esta clase

# ===============================
# 🔁 Conversión de AST a JSON
# ===============================

def to_json(ast_node):
    """
    Convierte el AST a formato JSON.
    """
    if ast_node is None:
        return None

    def node_to_dict(node):
        if node is None:
            return None

        node_type = node.__class__.__name__
        result = {"type": node_type}

        # Mapeo explícito (si querés controlar nombres o estructura)
        if node_type == "Program":
            result["declarations"] = [node_to_dict(decl) for decl in node.decls]
        elif node_type == "FunctionDef":
            result["name"] = node.name
            result["params"] = node_to_dict(node.params)
            result["body"] = node_to_dict(node.body)
            result["return_type"] = getattr(node, "return_type", None)
        elif node_type == "ParamList":
            result["params"] = [node_to_dict(param) for param in node.params]
        elif node_type == "Param":
            result["type"] = node.type
            result["name"] = node.name
        elif node_type == "Print":
            result["expression"] = node_to_dict(node.expr)
        elif node_type == "StringLiteral":
            result["value"] = node.value
        elif node_type == "Block":
            result["statements"] = [node_to_dict(stmt) for stmt in node.statements]
        elif node_type == "VarDecl":
            result["type"] = node.type
            result["name"] = node.name
            result["init"] = node_to_dict(node.init_expr)
        elif node_type == "Assign":
            result["name"] = node.name
            result["value"] = node_to_dict(node.expr)
        elif node_type == "If":
            result["condition"] = node_to_dict(node.condition)
            result["thenBlock"] = node_to_dict(node.then_block)
            result["elseBlock"] = node_to_dict(node.else_block)
        elif node_type == "While":
            result["condition"] = node_to_dict(node.condition)
            result["body"] = node_to_dict(node.body)
        elif node_type == "Return":
            result["value"] = node_to_dict(node.expr)
        elif node_type == "BinOp":
            result["operator"] = node.op
            result["left"] = node_to_dict(node.left)
            result["right"] = node_to_dict(node.right)
        elif node_type == "UnaryOp":
            result["operator"] = node.op
            result["expression"] = node_to_dict(node.expr)
        elif node_type == "VarRef":
            result["name"] = node.name
        elif node_type == "Number":
            result["value"] = node.value
        else:
            # Fallback: recorrer los atributos del nodo automáticamente
            for attr, value in vars(node).items():
                if isinstance(value, ASTNode):
                    result[attr] = node_to_dict(value)
                elif isinstance(value, list):
                    result[attr] = [
                        node_to_dict(v) if isinstance(v, ASTNode) else v for v in value
                    ]
                else:
                    result[attr] = value

        return result

    return node_to_dict(ast_node)

def generate_json_output(ast_node, filename="ast_output.json"):
    ast_dict = to_json(ast_node)
    try:
        with open(filename, 'w') as f:
            json.dump(ast_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error al guardar el AST: {str(e)}")
        return False

def validate_json(filename="ast_output.json"):
    try:
        with open(filename, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Error de formato JSON: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error al abrir el archivo: {str(e)}")
        return False

# ===============================
# 🌳 Visualización con Graphviz
# ===============================

def visualize_ast(node, filename='ast_output'):
    """
    Crea una imagen PNG del AST usando graphviz.
    Requiere que cada nodo AST tenga un método `.children()`.
    """
    graph = Digraph()

    def visit(n):
        node_label = f"{n.__class__.__name__}"
        if hasattr(n, 'name'):
            node_label += f"\\n{n.name}"
        elif hasattr(n, 'value'):
            node_label += f"\\n{n.value}"

        graph.node(str(id(n)), label=node_label)

        if hasattr(n, 'children'):
            for child in n.children():
                if child:
                    graph.edge(str(id(n)), str(id(child)))
                    visit(child)

    visit(node)
    graph.render(filename, format='png', cleanup=True)

# ===============================
# 🌳 Visualización alternativa con pydot
# ===============================

def generate_ast_graph(node, graph=None, parent_name=None, node_id=0):
    if graph is None:
        graph = pydot.Dot(graph_type='graph')

    current_node_name = f"{node.__class__.__name__}_{node_id}"
    label = node.__class__.__name__
    if hasattr(node, 'name'):
        label += f"\\n{node.name}"
    if hasattr(node, 'value'):
        label += f"\\n{node.value}"

    graph.add_node(pydot.Node(current_node_name, label=label, shape="box", style="filled", fillcolor="lightyellow"))

    if parent_name:
        graph.add_edge(pydot.Edge(parent_name, current_node_name))

    for attr, value in vars(node).items():
        if isinstance(value, list):
            for idx, child in enumerate(value):
                if isinstance(child, ASTNode):
                    generate_ast_graph(child, graph, current_node_name, node_id + idx + 1)
        elif isinstance(value, ASTNode):
            generate_ast_graph(value, graph, current_node_name, node_id + 1)

    return graph

def save_ast_graph(ast_node, output_file="ast_graph.png"):
    graph = generate_ast_graph(ast_node)
    graph.write_png(output_file)
