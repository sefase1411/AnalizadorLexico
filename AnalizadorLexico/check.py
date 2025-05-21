# check.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from rich import print
from rich.table import Table

from model import (
    Program, FunctionDef, ParamList, Param, Block, VarDecl,
    Assign, Return, BinOp, UnaryOp, VarRef, FunctionCall,
    Number, String, Char, If, While, Print,
    TrueLiteral, FalseLiteral
)

from symtab import Symtab
from typesys import check_binop, check_unaryop

# ────────────────────────────────────────────────
#  Estructura de error semántico enriquecido
# ────────────────────────────────────────────────
@dataclass
class SemanticError:
    kind: str                       # p.ej. "TypeError", "UndeclaredVar", …
    msg: str                        # mensaje legible
    line: Optional[int] = None
    col:  Optional[int] = None

    def __str__(self) -> str:
        loc = f"[L{self.line},C{self.col}] " if self.line is not None else ""
        return f"❌ {loc}{self.kind}: {self.msg}"

# ────────────────────────────────────────────────
#  Utilidades
# ────────────────────────────────────────────────
def normalize_type(t):
    return t.lower() if isinstance(t, str) else t

def unified_symbol_table(symtab: Symtab):
    """Imprime recursivamente solo las tablas con símbolos."""
    def recursive_print(env: Symtab):
        if not env.entries:            # oculta tablas vacías
            for child in env.children:
                recursive_print(child)
            return

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

# ────────────────────────────────────────────────
#  Analizador semántico
# ────────────────────────────────────────────────
class Checker:
    def __init__(self):
        self.symtab: Symtab | None = None
        self.errors: List[SemanticError] = []

    # ---------- API pública ----------
    def check(self, node):
        env = Symtab("global")
        self.symtab = env
        self.visit(node, env)

        print("\n📦 Tabla de Símbolos (unificada):\n")
        unified_symbol_table(self.symtab)

        return self.errors

    # ---------- helpers internos ----------
    def _err(self, node, kind: str, msg: str):
        line, col = ('?', '?')
        if hasattr(node, 'pos') and node.pos is not None:
            line, col = node.pos
        self.errors.append(SemanticError(kind, msg, line, col))

    # ---------- despacho genérico ----------
    def visit(self, node, env):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, env)

    def generic_visit(self, node, env):
        self._err(node, "NoVisitor",
                  f"No se implementó visit_{node.__class__.__name__}")

    # ---------- nodos de alto nivel ----------
    def visit_Program(self, node: Program, env):
        for decl in node.decls:
            self.visit(decl, env)

    def visit_FunctionDef(self, node: FunctionDef, env):
        node.dtype = "function"
        env.add(node.name, node)
        func_env = Symtab(node.name, env)

        if node.params:
            self.visit(node.params, func_env)
        if node.body:
            self.visit(node.body, func_env)

    def visit_ParamList(self, node: ParamList, env):
        for param in node.params:
            self.visit(param, env)

    def visit_Param(self, node: Param, env):
        node.dtype = normalize_type(node.type)
        env.add(node.name, node)

    def visit_Block(self, node: Block, env):
        block_env = Symtab("block", env)
        for stmt in node.statements:
            self.visit(stmt, block_env)

    # ---------- declaraciones y asignación ----------
    def visit_VarDecl(self, node: VarDecl, env):
        node.dtype = normalize_type(node.type)
        env.add(node.name, node)

        if node.init_expr:
            expr_type = normalize_type(self.visit(node.init_expr, env))
            if expr_type != node.dtype:
                self._err(node, "TypeError",
                          f"Asignación incompatible a '{node.name}': "
                          f"esperado {node.dtype}, obtenido {expr_type}")

    def visit_Assign(self, node: Assign, env):
        var = env.get(node.name)
        if not var:
            self._err(node, "UndeclaredVar",
                      f"Variable '{node.name}' no declarada")
            return

        expected = normalize_type(getattr(var, 'type',
                              getattr(var, 'dtype', 'undefined')))
        actual   = normalize_type(self.visit(node.expr, env))
        if actual != expected:
            self._err(node, "TypeError",
                      f"Tipo incompatible en asignación a '{node.name}': "
                      f"esperado {expected}, se obtuvo {actual}")

        return expected

    # ---------- E/S ----------
    def visit_Print(self, node: Print, env):
        self.visit(node.expr, env)

    # ---------- control de flujo ----------
    def visit_If(self, node: If, env):
        self.visit(node.condition, env)
        self.visit(node.then_block, env)
        if node.else_block:
            self.visit(node.else_block, env)

    def visit_While(self, node: While, env):
        self.visit(node.condition, env)
        self.visit(node.body, env)

    def visit_Return(self, node: Return, env):
        if node.expr:
            self.visit(node.expr, env)

    # ---------- expresiones ----------
    def visit_BinOp(self, node: BinOp, env):
        left  = normalize_type(self.visit(node.left,  env))
        right = normalize_type(self.visit(node.right, env))

        if left is None or right is None:
            self._err(node, "UntypedExpr",
                      f"No se puede aplicar '{node.op}' "
                      f"porque una de las expresiones no tiene tipo")
            return None

        result = check_binop(node.op, left, right)
        if result is None:
            self._err(node, "InvalidBinOp",
                      f"Operador '{node.op}' no válido para "
                      f"tipos {left} y {right}")
        else:
            node.type = result
        return result

    def visit_UnaryOp(self, node: UnaryOp, env):
        operand = normalize_type(self.visit(node.expr, env))
        result = check_unaryop(node.op, operand)
        if result is None:
            self._err(node, "InvalidUnaryOp",
                      f"Operador unario '{node.op}' no válido "
                      f"para tipo {operand}")
        else:
            node.type = result
        return result

    # ---------- literales ----------
    def visit_Number(self, node: Number, env):
        node.type = "int"
        return "int"

    def visit_String(self, node: String, env):
        node.type = "string"
        return "string"

    def visit_Char(self, node: Char, env):
        
        node.type = "char"
        return "char"

    def visit_TrueLiteral(self, node: TrueLiteral, env):
        node.type = "bool"
        return "bool"

    def visit_FalseLiteral(self, node: FalseLiteral, env):
        node.type = "bool"
        return "bool"

    # ---------- referencias ----------
    def visit_VarRef(self, node: VarRef, env):
        var = env.get(node.name)
        if not var:
            self._err(node, "UndeclaredVar",
                      f"Variable '{node.name}' no declarada")
            return "undefined"
        node.type = normalize_type(getattr(var, 'type',
                               getattr(var, 'dtype', 'undefined')))
        return node.type

    def visit_FunctionCall(self, node: FunctionCall, env):
        func = env.get(node.name)
        if not func:
            self._err(node, "UndeclaredFunc",
                      f"Función '{node.name}' no declarada")
            return "undefined"

        expected_params = func.params.params if func.params else []
        actual_args     = node.arguments or []

        if len(expected_params) != len(actual_args):
            self._err(node, "ArgMismatch",
                      f"La función '{node.name}' esperaba "
                      f"{len(expected_params)} argumentos, "
                      f"se pasaron {len(actual_args)}")

        for expected, actual in zip(expected_params, actual_args):
            actual_t = normalize_type(self.visit(actual, env))
            expected_t = normalize_type(expected.type)
            if actual_t != expected_t:
                self._err(node, "TypeError",
                          f"Tipo de argumento inválido para '{node.name}': "
                          f"se esperaba {expected_t}, se recibió {actual_t}")

        node.type = normalize_type(getattr(func, 'return_type', 'void'))
        return node.type
