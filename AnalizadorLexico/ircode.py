from model import (
    Program, FunctionDef, ParamList, Param, Block, VarDecl,
    Assign, Return, BinOp, UnaryOp, VarRef, FunctionCall,
    Number, String, TrueLiteral, FalseLiteral, If, While,
    Print, Char
)

class IRFunction:
    def __init__(self, name, params=None):
        self.name = name
        self.instructions: list = []
        self.params = params or []  # Lista de nombres de parámetros (en orden)
        # Todos los locales (incluye parámetros), valor es tipo, ej. 'I'
        self.locals: dict[str, str] = {p: 'I' for p in self.params}

    def add_local(self, name: str, typ='I') -> None:
        # Solo agrega si no existe
        if name not in self.locals:
            self.locals[name] = typ

    def get_local(self, name: str) -> bool:
        # Simplemente verifica si existe
        return name in self.locals

    def add_instr(self, op: str, *args):
        self.instructions.append((op, *args))


class IRModule:
    def __init__(self):
        self.functions: list[IRFunction] = []
        self.global_vars: set[str] = set()

    def add_function(self, func: IRFunction):
        self.functions.append(func)

    def add_global(self, name: str):
        self.global_vars.add(name)

    def dump(self) -> str:
        out: list[str] = []
        out.append("MODULE:::")
        for func in self.functions:
            param_names = func.params
            param_types = ['I'] * len(param_names)  # ajusta si tienes tipos reales
            return_type = 'I'  # ajusta si tienes tipos reales

            # Los locales, excluyendo los parámetros
            locals_only = {k: v for k, v in func.locals.items() if k not in param_names}

            out.append(f"FUNCTION::: {func.name}, {param_names}, {param_types} {return_type}")
            out.append(f"locals: {locals_only}")
            for instr in func.instructions:
                out.append(str(instr))
        return "\n".join(out)


class IRCodeGenerator:
    def __init__(self):
        self.module = IRModule()
        self.global_inits: list[tuple[str, any]] = []

    def generic_visit(self, node, context):
        raise NotImplementedError(f"No se implementó visit_{node.__class__.__name__} en IRCodeGenerator")

    def generate(self, ast_root: list):
        # 1) Todas las funciones definidas por el usuario primero
        for node in ast_root:
            if isinstance(node, FunctionDef):
                self.visit_FunctionDef(node, None)

        # 2) main wrapper
        main_func = IRFunction("main", [])
        self.module.add_function(main_func)
        # 3) _actual_main para statements globales
        actual_main_func = IRFunction("_actual_main", [])
        self.module.add_function(actual_main_func)

        # 4) Registrar variables globales
        for node in ast_root:
            if isinstance(node, VarDecl):
                self.visit_VarDecl(node, None)

        # 5) Statements globales van a _actual_main
        for node in ast_root:
            if not isinstance(node, (FunctionDef, VarDecl)):
                node.accept(self, actual_main_func)

        # 6) Inicialización global
        init_instrs: list = []
        for name, expr in self.global_inits:
            if expr is not None:
                expr.accept(self, actual_main_func)
                init_instrs.extend(actual_main_func.instructions)
                init_instrs.append(('GLOBAL_SET', name))
                actual_main_func.instructions = []
        actual_main_func.instructions = init_instrs + actual_main_func.instructions

        # 7) main solo llama a _actual_main y hace RET
        main_func.add_instr("CALL", "_actual_main")
        main_func.add_instr("RET")

        return self.module

    # ─── Visitors ───────────────────────────────────────────

    def visit_Program(self, node: Program, context):
        pass

    def visit_FunctionDef(self, node: FunctionDef, context):
        param_names = [param.name for param in node.params.params]
        func = IRFunction(node.name, param_names)
        self.module.add_function(func)
        # Parámetros ya están en func.locals (por __init__)
        for stmt in node.body.statements:
            stmt.accept(self, func)

    def visit_VarDecl(self, node: VarDecl, context):
        name = node.name
        init = node.init_expr
        if context is None:
            self.module.add_global(name)
            self.global_inits.append((name, init))
        else:
            context.add_local(name, 'I')
            if init:
                init.accept(self, context)
                context.add_instr("LOCAL_SET", name)

    def visit_Assign(self, node: Assign, context):
        node.expr.accept(self, context)
        if context.get_local(node.name):
            context.add_instr("LOCAL_SET", node.name)
        else:
            context.add_instr("GLOBAL_SET", node.name)

    def visit_Print(self, node: Print, context):
        node.expr.accept(self, context)
        if not isinstance(node.expr, String) and not isinstance(node.expr, BinOp):
            context.add_instr("PRINTI")

    def visit_If(self, node: If, context):
        node.condition.accept(self, context)
        context.add_instr("IF")
        for stmt in node.then_block.statements:
            stmt.accept(self, context)
        if node.else_block:
            context.add_instr("ELSE")
            for stmt in node.else_block.statements:
                stmt.accept(self, context)
        context.add_instr("ENDIF")

    def visit_While(self, node: While, context):
        context.add_instr("LOOP")
        node.condition.accept(self, context)
        context.add_instr("CBREAK")
        for stmt in node.body.statements:
            stmt.accept(self, context)
        context.add_instr("ENDLOOP")

    def visit_Return(self, node: Return, context):
        if node.expr:
            node.expr.accept(self, context)
        context.add_instr("RET")

    def visit_FunctionCall(self, node: FunctionCall, context):
        for arg in node.arguments:
            arg.accept(self, context)
        context.add_instr("CALL", node.name)

    def visit_BinOp(self, node: BinOp, context):
        if node.op == '+' and isinstance(node.left, String):
            for ch in node.left.value:
                context.add_instr("PUSHI", ord(ch))
                context.add_instr("PRINTB")
            node.right.accept(self, context)
            context.add_instr("PRINTI")
            return
        if node.op == '+' and isinstance(node.right, String):
            node.left.accept(self, context)
            context.add_instr("PRINTI")
            for ch in node.right.value:
                context.add_instr("PUSHI", ord(ch))
                context.add_instr("PRINTB")
            return

        node.left.accept(self, context)
        node.right.accept(self, context)
        op_map = {
            '+':'ADDI','-':'SUBI','*':'MULI','/':'DIVI',
            '<':'LTI','<=':'LEI','>':'GTI','>=':'GEI',
            '==':'EQI','!=':'NEI'
        }
        if node.op in op_map:
            context.add_instr(op_map[node.op])

    def visit_UnaryOp(self, node: UnaryOp, context):
        node.expr.accept(self, context)
        if node.op == '-':
            context.add_instr("CONSTI", -1)
            context.add_instr("MULI")

    def visit_Number(self, node: Number, context):
        context.add_instr("CONSTI", node.value)

    def visit_Char(self, node: Char, context):
        context.add_instr("CONSTI", ord(node.value))

    def visit_TrueLiteral(self, node: TrueLiteral, context):
        context.add_instr("CONSTI", 1)

    def visit_FalseLiteral(self, node: FalseLiteral, context):
        context.add_instr("CONSTI", 0)

    def visit_String(self, node: String, context):
        for ch in node.value:
            context.add_instr("PUSHI", ord(ch))
            context.add_instr("PRINTB")

    def visit_VarRef(self, node: VarRef, context):
        if context.get_local(node.name):
            context.add_instr("LOCAL_GET", node.name)
        else:
            context.add_instr("GLOBAL_GET", node.name)

    def visit_Block(self, node: Block, context):
        for stmt in node.statements:
            stmt.accept(self, context)

    def visit_ParamList(self, node: ParamList, context):
        pass

    def visit_Param(self, node: Param, context):
        pass

    def visit_Literal(self, node, context):
        pass

    def visit_Break(self, node, context):
        context.add_instr("CONSTI", 1)
        context.add_instr("CBREAK")

    def visit_Continue(self, node, context):
        context.add_instr("CONTINUE")
