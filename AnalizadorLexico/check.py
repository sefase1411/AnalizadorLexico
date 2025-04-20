# check.py
'''
Este archivo contendrá la parte de verificación/validación de tipos
del compilador.  Hay varios aspectos que deben gestionarse para
que esto funcione. Primero, debe tener una noción de "tipo" en su compilador.
Segundo, debe administrar los entornos y el alcance para manejar los
nombres de las definiciones (variables, funciones, etc.).

Una clave para esta parte del proyecto es realizar pruebas adecuadas.
A medida que agregue código, piense en cómo podría probarlo.
'''
from rich    import print
from typing  import Union

from model   import *
from symtab  import Symtab
from typesys import typenames, check_binop, check_unaryop


Checker(Visitor):
	@classmethod
	def check(cls, n:Node):
		'''
		1. Crear una nueva tabla de simbolos
		2. Visitar todas las declaraciones
		'''
		check = cls()
		env = Symtab()
		n.accept(check, env)
		return check

	def visit(self, n:Program, env:Symtab):
		'''
		1. recorrer la lista de elementos
		'''
		for stmt in n.stmts:
			stmt.accept(self, env)

	# Statements

	def visit(self, n:Assignment, env:Symtab):
		'''
		1. Validar n.loc
		2. Visitar n.expr
		3. Verificar si son tipos compatibles
		'''
		type1 = env.get(n.name, env).type
		type2 = n.expr.accept(self, env)
		return check_binop('=', type1, type2)

	def visit(self, n:Print, env:Symtab):
		'''
		1. visitar n.expr
		'''
		pass

	def visit(self, n:If, env:Symtab):
		'''
		1. Visitar n.test (validar tipos)
		2. Visitar Stament por n.then
		3. Si existe opcion n.else_, visitar
		'''
		pass
			
	def visit(self, n:While, env:Symtab):
		'''
		1. Visitar n.test (validar tipos)
		2. visitar n.body
		'''
		pass
		
	def visit(self, n:Union[Break, Continue], env:Symtab):
		'''
		1. Verificar que esta dentro de un ciclo while
		'''
		pass
			
	def visit(self, n:Return, env:Symtab):
		'''
		1. Si se ha definido n.expr, validar que sea del mismo tipo de la función
		'''
		pass
	
	# Declarations

	def visit(self, n:Variable, env:Symtab):
		'''
		1. Agregar n.name a la TS actual
		'''
		env.add(n.name, n)
		

	def visit(self, n:Function, env:Symtab):
		'''
		1. Guardar la función en la TS actual
		2. Crear una nueva TS para la función
		3. Agregar todos los n.params dentro de la TS
		4. Visitar n.stmts
		'''
		env.add(n.name, n)
		env = Symtab(env)
		for p in n.params:
			env.add(p.name, p)
		if n.stmts: n.stmts.accept(self, env)

	def visit(self, n:Parameter, env:Symtab):
		'''
		1. Guardar el parametro (name, type) en TS
		'''
		pass
		
	# Expressions

	def visit(self, n:Literal, env:Symtab):
		'''
		1. Retornar el tipo de la literal
		'''
		pass

	def visit(self, n:BinOp, env:Symtab):
		'''
		1. visitar n.left y luego n.right
		2. Verificar compatibilidad de tipos
		'''
		type1 = n.left.accept(self, env)
		type2 = n.right.accept(self, env)
		return check_binop(n.opr, type1, type2)
		
	def visit(self, n:UnaryOp, env:Symtab):
		'''
		1. visitar n.expr
		2. validar si es un operador unario valido
		'''
		type1 = n.expr.accept(self, env)
		return check_unaryop(n.opr, type1)

	def visit(self, n:TypeCast, env:Symtab):
		'''
		1. Visitar n.expr para validar
		2. retornar el tipo del cast n.type
		'''
		pass

	def visit(self, n:FunctionCall, env:Symtab):
		'''
		1. Validar si n.name existe
		2. visitar n.args (si estan definidos)
		3. verificar que len(n.args) == len(func.params)
		4. verificar que cada arg sea compatible con cada param de la función
		'''

	def visit(self, n:NamedLocation, env:Symtab):
		'''
		1. Verificar si n.name existe en TS y obtener el tipo
		2. Retornar el tipo
		'''
		pass

	def visit(self, n:MemoryLocation, env:Symtab):
		'''
		1. Visitar n.address (expression) para validar
		2. Retornar el tipo de datos
		'''
		pass

