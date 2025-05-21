from model import (
    Number, String, TrueLiteral, FalseLiteral,
    VarRef, FunctionCall, Char,
    Program, FunctionDef, ParamList, Param,
    Block, VarDecl, Assign, Print,
    If, While, Return, BinOp, UnaryOp, Break, Continue
)
from ast_utility import *
from lexer import *



class SyntaxErrorDetail(Exception):
    def __init__(self, error_type, line, column, message):
        self.error_type = error_type
        self.line = line
        self.column = column
        self.message = message

    def __str__(self):
        loc = f"línea {self.line}, columna {self.column}" if self.column else f"línea {self.line}"
        return f"{self.error_type} en {loc}: {self.message}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    def parse(self):
        declarations = []
        while self.current < len(self.tokens) and not self.check('EOF'):
            try:
                stmt = self.statement()
                declarations.append(stmt)
            except SyntaxErrorDetail as e:
                self.errors.append(str(e))
                self.synchronize()
        return Program(declarations)

    def peek(self):
        return self.tokens[self.current] if self.current < len(self.tokens) else ('EOF', '', 0)

    def consume(self):
        token = self.peek()
        self.current += 1
        return token

    def check(self, token_type):
        return self.peek()[0] == token_type

    def check_literal(self, literal):
        return self.peek()[1] == literal

    def match(self, token_type):
        if self.check(token_type):
            return self.consume()
        token = self.peek()
        line = token[2]
        col = token[3] if len(token) > 3 else None
        raise SyntaxErrorDetail("UnexpectedToken", line, col, f"Se esperaba token '{token_type}', se encontró '{token[0]}'")

    def match_literal(self, literal):
        if self.check_literal(literal):
            return self.consume()
        token = self.peek()
        line = token[2]
        col = token[3] if len(token) > 3 else None
        raise SyntaxErrorDetail("UnexpectedLiteral", line, col, f"Se esperaba '{literal}', se encontró '{token[1]}'")

    def synchronize(self):
        self.consume()
        while self.current < len(self.tokens):
            if self.check_literal(';') or self.check_literal('{') or self.check_literal('}') or \
               self.check('FUNC') or self.check('INT') or self.check('IF') or \
               self.check('WHILE') or self.check('RETURN'):
                return
            self.consume()

    def statement(self):
        if self.check('FUNC'):
            return self.funcdecl()
        elif self.check('VAR'):
            return self.var_decl()
        elif self.check('INT') or self.check('BOOL'):
            return self.typed_var_decl()
        elif self.check('PRINT'):
            return self.print_stmt()
        elif self.check('ID') and self.current + 1 < len(self.tokens) and self.tokens[self.current + 1][1] == '(':
            return self.function_call_stmt()
        elif self.check('ID'):
            return self.assignment()
        elif self.check('IF'):
            return self.if_stmt()
        elif self.check('WHILE'):
            return self.while_stmt()
        elif self.check('RETURN'):
            return self.return_stmt()
        token = self.peek()
        raise SyntaxErrorDetail("InvalidStatement", token[2], None, f"Declaración inesperada '{token[1]}'")

    def var_decl(self):
        self.match('VAR')
        id_token = self.match('ID')
        type_token = self.match('INT') if self.check('INT') else self.match('BOOL')
        init_expr = None
        if self.check('ASSIGN'):
            self.consume()
            init_expr = self.expression()
        self.match_literal(';')
        return VarDecl(type_token[1], id_token[1], init_expr)

    def typed_var_decl(self):
        type_token = self.match('INT') if self.check('INT') else self.match('BOOL')
        id_token = self.match('ID')
        init_expr = None
        if self.check('ASSIGN'):
            self.consume()
            init_expr = self.expression()
        self.match_literal(';')
        return VarDecl(type_token[1], id_token[1], init_expr)

    def funcdecl(self):
        self.match('FUNC')
        func_name = self.match('ID')[1]
        self.match_literal('(')
        params = self.parameters() if not self.check_literal(')') else []
        self.match_literal(')')
        if self.check('INT') or self.check('BOOL'):
            return_type = self.consume()[1]
        else:
            return_type = 'void'
        body = self.block()
        return FunctionDef(func_name, ParamList(params), body, return_type)

    def parameters(self):
        params = [self.parameter()]
        while self.check_literal(','):
            self.consume()
            params.append(self.parameter())
        return params

    def parameter(self):
        id_token = self.match('ID')
        type_token = self.match('INT') if self.check('INT') else self.match('BOOL')
        return Param(type_token[1], id_token[1])

    def block(self):
        self.match_literal('{')
        statements = []
        while not self.check_literal('}') and not self.check('EOF'):
            statements.append(self.statement())
        self.match_literal('}')
        return Block(statements)

    def assignment(self):
        var_name = self.match('ID')[1]
        self.match('ASSIGN')
        value = self.expression()
        self.match_literal(';')
        return Assign(var_name, value)

    def print_stmt(self):
        self.match('PRINT')
        value = self.expression()
        self.match_literal(';')
        if value is None:
            raise SyntaxErrorDetail("MissingExpression", self.peek()[2], None, "Expresión faltante en print")
        return Print(value)

    def if_stmt(self):
        self.match('IF')
        self.match_literal('(')
        condition = self.expression()
        self.match_literal(')')
        then_branch = self.block()
        else_branch = self.block() if self.check('ELSE') and self.consume() else None
        return If(condition, then_branch, else_branch)

    def while_stmt(self):
        self.match('WHILE')
        self.match_literal('(')
        condition = self.expression()
        self.match_literal(')')
        return While(condition, self.block())

    def return_stmt(self):
        self.match('RETURN')
        value = self.expression() if not self.check_literal(';') else None
        self.match_literal(';')
        if value is None:
            raise SyntaxErrorDetail("MissingReturnValue", self.peek()[2], None, "Expresión faltante en return")
        return Return(value)

    def expression(self):
        expr = self.orterm()
        if expr is None:
            raise SyntaxErrorDetail("InvalidExpression", self.peek()[2], None, "Expresión inválida")
        return expr

    def orterm(self):
        expr = self.andterm()
        while self.check_literal('||'):
            operator = self.consume()[1]
            expr = BinOp(operator, expr, self.andterm())
        return expr

    def andterm(self):
        expr = self.relterm()
        while self.check_literal('&&'):
            operator = self.consume()[1]
            expr = BinOp(operator, expr, self.relterm())
        return expr

    def relterm(self):
        expr = self.addterm()
        op_map = {'EQ': '==', 'NE': '!=', 'LT': '<', 'GT': '>', 'LE': '<=', 'GE': '>='}
        while any(self.check(op) for op in op_map.keys()):
            operator = op_map[self.consume()[0]]
            expr = BinOp(operator, expr, self.addterm())
        return expr

    def addterm(self):
        expr = self.factor()
        while self.check_literal('+') or self.check_literal('-'):
            operator = self.consume()[1]
            expr = BinOp(operator, expr, self.factor())
        return expr

    def factor(self):
        expr = self.primary()
        while self.check_literal('*') or self.check_literal('/') or self.check_literal('%'):
            operator = self.consume()[1]
            expr = BinOp(operator, expr, self.primary())
        return expr

    def primary(self):
        if self.check('NUMBER'):
            return Number(int(self.consume()[1]))
        elif self.check('TRUE'):
            self.consume()
            return TrueLiteral()
        elif self.check('FALSE'):
            self.consume()
            return FalseLiteral()
        elif self.check('ID'):
            if self.current + 1 < len(self.tokens) and self.tokens[self.current + 1][1] == '(':
                return self.function_call_expr()
            return VarRef(self.consume()[1])
        elif self.check_literal('('):
            self.consume()
            expr = self.expression()
            self.match_literal(')')
            return expr
        
        
        elif self.check('STRING'):
            return String(self.consume()[1])
        elif self.check('CHAR'):             
            raw = self.consume()[1]          
            val = raw[1:-1]                  
            return Char(val)

        elif self.check_literal('-'):
            self.consume()
            return UnaryOp('-', self.primary())

        
        
        token = self.peek()
        raise SyntaxErrorDetail("UnexpectedPrimary", token[2], None, f"Expresión no válida: {token[1]}")

    def function_call_expr(self):
        func_name = self.match('ID')[1]
        self.match_literal('(')
        args = []
        if not self.check_literal(')'):
            args.append(self.expression())
            while self.check_literal(','):
                self.consume()
                args.append(self.expression())
        self.match_literal(')')
        return FunctionCall(func_name, args)

    def function_call_stmt(self):
        func_name = self.match('ID')[1]
        self.match_literal('(')
        args = []
        if not self.check_literal(')'):
            args.append(self.expression())
            while self.check_literal(','):
                self.consume()
                args.append(self.expression())
        self.match_literal(')')
        self.match_literal(';')
        return FunctionCall(func_name, args)

    def analyze_file(filename):
        try:
            with open(filename, 'r') as file:
                source_code = file.read()
        except Exception as e:
            print(f"Error al leer el archivo: {str(e)}")
            return None, [str(e)]

        tokens = tokenize(source_code)
        print("=== Tokens ===")
        for token in tokens:
            print(token)

        parser_instance = Parser(tokens)
        ast = parser_instance.parse()

        parser_errors = parser_instance.errors
        if parser_errors:
            print("Errores de parsing:")
            for error in parser_errors:
                print(f"  - {error}")

        if ast and not parser_errors:
            generate_json_output(ast)
            validate_json()
        return ast, parser_errors
