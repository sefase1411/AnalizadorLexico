import unittest
from lexer import tokenize
from parser import Parser
from ast_utility import to_json
from model import Program, VarDecl, Number

class TestLexer(unittest.TestCase):
    def test_token_var_decl(self):
        code = "var x int = 10;"
        tokens = tokenize(code)
        expected = [
            ('VAR', 'var', 1),
            ('ID', 'x', 1),
            ('INT', 'int', 1),
            ('ASSIGN', '=', 1),
            ('NUMBER', 10, 1),
            (';', ';', 1),
            ('EOF', '', 1)
        ]
        self.assertEqual(tokens, expected)

    def test_ignores_comments(self):
        code = """
        // comentario
        var x int = 2; /* otro comentario */
        """
        tokens = tokenize(code)
        types = [tok[0] for tok in tokens]
        self.assertIn('VAR', types)
        self.assertIn('ID', types)
        self.assertNotIn('COMMENT', types)
        self.assertNotIn('MULTILINE_COMMENT', types)

class TestParser(unittest.TestCase):
    def test_var_decl_ast(self):
        code = "var x int = 10;"
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertIsInstance(ast, Program)
        self.assertIsInstance(ast.decls[0], VarDecl)
        self.assertEqual(ast.decls[0].name, "x")
        self.assertEqual(ast.decls[0].type, "INT")
        self.assertIsInstance(ast.decls[0].init_expr, Number)
        self.assertEqual(ast.decls[0].init_expr.value, 10)

class TestASTUtility(unittest.TestCase):
    def test_to_json_structure(self):
        code = "var x int = 10;"
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        ast_json = to_json(ast)

        self.assertEqual(ast_json['type'], 'Program')
        self.assertIn('declarations', ast_json)
        decl = ast_json['declarations'][0]
        self.assertEqual(decl['type'], 'VarDecl')
        self.assertEqual(decl['name'], 'x')
        self.assertEqual(decl['type'], 'INT')
        self.assertEqual(decl['init']['value'], 10)

if __name__ == '__main__':
    unittest.main()
