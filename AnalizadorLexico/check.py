from rich import print
from rich.table import Table
from model import (
    Program, FunctionDef, ParamList, Param, Block, VarDecl,
    Assign, Return, BinOp, UnaryOp, VarRef, FunctionCall,
    Number, String, If, While, Print, TrueLiteral, FalseLiteral
)
from symtab import Symtab
from typesys import check_binop, check_unaryop

def normalize_type(t):
    return t.lower() if isinstance(t, str) else t

def unified_symbol_table(symtab):
    def recursive_print(env):
        table = Table(title=f"Symbol Table: '{env.name}'")
        table.add_column("Símbolo", style="cyan")
        table.add_column("Tipo de nodo", style="green")
        table.add_column("Tipo declarado", style="magenta")

        for name, node in env.entries.items():
            table.add_row(
                name,
                node.__class__.__name__,
                getattr(node, "dtype", "-")
            )

        print(table)
        for child in env.children:
            recursive_print(child)

    recursive_print(symtab)

class Checker:
    def __init__(self):
        self.symtab = None
        self.errores = []

    def check(self, node):
        env = Symtab("global")
        self.symtab = env
        self.visit(node, env)
        print("\n📦 Tabla de Símbolos (unificada):\n")
        unified_symbol_table(self.symtab)
        return self.errores

    def visit(self, node, env):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env):
        self.errores.append(f"⚠️ No se implementó visit_{node.__class__.__name__}")

    def visit_Program(self, node, env):
        for decl in node.decls:
            self.visit(decl, env)

    def visit_FunctionDef(self, node, env):
        node.dtype = "function"
        env.add(node.name, node)
        func_env = Symtab(node.name, env)
        if node.params:
            self.visit(node.params, func_env)
        if node.body:
            self.visit(node.body, func_env)

    def visit_ParamList(self, node, env):
        for param in node.params:
            self.visit(param, env)

    def visit_Param(self, node, env):
        node.dtype = normalize_type(node.type)
        env.add(node.name, node)

    def visit_Block(self, node, env):
        block_env = Symtab("block", env)
        for stmt in node.statements:
            self.visit(stmt, block_env)

    def visit_VarDecl(self, node, env):
        node.dtype = normalize_type(node.type)
        env.add(node.name, node)
        if node.init_expr:
            expr_type = self.visit(node.init_expr, env)
            expected = normalize_type(node.type)
            actual = normalize_type(expr_type)
            if actual != expected:
                self.errores.append(f"❌ Tipo incompatible en '{node.name}': esperado {expected}, se obtuvo {actual}")

    def visit_Assign(self, node, env):
        var = env.get(node.name)
        if not var:
            self.errores.append(f"❌ Variable '{node.name}' no declarada")
            return
        expected = normalize_type(getattr(var, 'type', getattr(var, 'dtype', 'undefined')))
        actual = normalize_type(self.visit(node.expr, env))
        if actual != expected:
            self.errores.append(f"❌ Tipo incompatible en asignación a '{node.name}': esperado {expected}, se obtuvo {actual}")
        return check_binop("=", expected, actual)

    def visit_Print(self, node, env):
        self.visit(node.expr, env)

    def visit_If(self, node, env):
        self.visit(node.condition, env)
        self.visit(node.then_block, env)
        if node.else_block:
            self.visit(node.else_block, env)

    def visit_While(self, node, env):
        self.visit(node.condition, env)
        self.visit(node.body, env)

    def visit_Return(self, node, env):
        if node.expr:
            self.visit(node.expr, env)

    def visit_BinOp(self, node, env):
        left = normalize_type(self.visit(node.left, env))
        right = normalize_type(self.visit(node.right, env))

        if left is None or right is None:
            self.errores.append(f"❌ No se puede aplicar '{node.op}' porque una de las expresiones no tiene tipo")
            return None

        result = check_binop(node.op, left, right)
        if result is None:
            self.errores.append(f"❌ Operador binario inválido '{node.op}' para tipos '{left}' y '{right}'")
        return result

    def visit_UnaryOp(self, node, env):
        operand = normalize_type(self.visit(node.expr, env))
        result = check_unaryop(node.op, operand)
        if result is None:
            self.errores.append(f"❌ Operador unario inválido '{node.op}' para tipo '{operand}'")
        return result

    def visit_Number(self, node, env):
        return "int"

    def visit_String(self, node, env):
        return "string"

    def visit_TrueLiteral(self, node, env):
        return "bool"

    def visit_FalseLiteral(self, node, env):
        return "bool"

    def visit_VarRef(self, node, env):
        var = env.get(node.name)
        if not var:
            self.errores.append(f"❌ Variable '{node.name}' no declarada")
            return "undefined"
        return normalize_type(getattr(var, 'type', getattr(var, 'dtype', 'undefined')))

    def visit_FunctionCall(self, node, env):
        func = env.get(node.name)
        if not func:
            self.errores.append(f"❌ Función '{node.name}' no declarada")
            return "undefined"
        expected = func.params.params if func.params else []
        actual = node.arguments or []
        if len(expected) != len(actual):
            self.errores.append(f"❌ La función '{node.name}' esperaba {len(expected)} argumentos, se pasaron {len(actual)}")
        for e, a in zip(expected, actual):
            t = normalize_type(self.visit(a, env))
            et = normalize_type(e.type)
            if et != t:
                self.errores.append(f"❌ Tipo de argumento inválido para '{node.name}': se esperaba {et}, se recibió {t}")
        return normalize_type(getattr(func, 'return_type', 'void'))
