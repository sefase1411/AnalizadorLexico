import pytest
from lexer import tokenize

def test_tokenize():
    code = "var x = 42;"
    tokens = tokenize(code)
    assert tokens == [('VAR', 'var', 1), ('ID', 'x', 1), ('ASSIGN', '=', 1), ('INTEGER', '42', 1), ('SEMI', ';', 1)]

def test_invalid_char():
    code = "var x = @;"
    with pytest.raises(SyntaxError):
        tokenize(code)

def test_unterminated_comment():
    code = "/* Esto es un comentario no terminado"
    with pytest.raises(SyntaxError):
        tokenize(code)