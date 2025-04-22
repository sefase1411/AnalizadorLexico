import unittest
from lexer import tokenize
from parser import Parser
from check import Checker

class TestSemanticAnalyzer(unittest.TestCase):
    
    def analyze(self, code):
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertFalse(parser.errors, "Errores de parsing detectados")

        checker = Checker()
        checker.check(ast)
        return checker.errores

    def test_variable_no_declarada(self):
        code = """
        func main() int {
            x = 10;
            return x;
        }
        """
        errors = self.analyze(code)
        self.assertTrue(any("no declarada" in e for e in errors))

    def test_asignacion_tipo_incorrecto(self):
        code = """
        func main() int {
            var x int;
            x = true;
            return 0;
        }
        """
        errors = self.analyze(code)
        self.assertTrue(any("tipos incompatibles" in e or "bool" in e for e in errors))

    def test_funcion_argumentos_incorrectos(self):
        code = """
        func suma(a int, b int) int {
            return a + b;
        }

        func main() int {
            var x int;
            x = suma(5);  // falta un argumento
            return x;
        }
        """
        errors = self.analyze(code)
        self.assertTrue(any("argumentos" in e for e in errors))

    def test_retorno_tipo_invalido(self):
        code = """
        func main() float {
            return true;
        }
        """
        errors = self.analyze(code)
        self.assertTrue(any("tipo de retorno" in e or "bool" in e for e in errors))

    def test_codigo_correcto(self):
        code = """
        func main() int {
            var x int;
            x = 5 + 3;
            return x;
        }
        """
        errors = self.analyze(code)
        self.assertEqual(len(errors), 0, f"Errores inesperados: {errors}")

if __name__ == '__main__':
    unittest.main()
