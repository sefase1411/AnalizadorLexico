# symtab.py
from rich.table   import Table
from rich.console import Console
from rich         import print

class Symtab:
    '''
    Una tabla de símbolos.  Este es un objeto simple que sólo
    mantiene una hashtable (dict) de nombres de simbolos y los
    nodos de declaración o definición de funciones a los que se
    refieren.
    Hay una tabla de símbolos separada para cada elemento de
    código que tiene su propio contexto (por ejemplo cada función,
    clase, tendrá su propia tabla de símbolos). Como resultado,
    las tablas de símbolos se pueden anidar si los elementos de
    código están anidados y las búsquedas de las tablas de
    símbolos se repetirán hacia arriba a través de los padres
    para representar las reglas de alcance léxico.
    '''

    class SymbolDefinedError(Exception):
        '''
        Se genera una excepción cuando el código intenta agregar
        un símbolo a una tabla donde el símbolo ya se ha definido.
        Tenga en cuenta que 'definido' se usa aquí en el sentido
        del lenguaje C, es decir, 'se ha asignado espacio para el
        símbolo', en lugar de una declaración.
        '''
        pass

    class SymbolConflictError(Exception):
        '''
        Se produce una excepción cuando el código intenta agregar
        un símbolo a una tabla donde el símbolo ya existe y su tipo
        difiere del existente previamente.
        '''
        pass

    def __init__(self, name, parent=None):
        '''
        Crea una tabla de símbolos vacía con la tabla de
        símbolos padre dada.
        '''
        self.name = name
        self.entries = {}
        self.parent = parent
        self.children = []
        if self.parent:
            self.parent.children.append(self)

    def exists(self, name):
        '''
        Verifica si un símbolo ya fue declarado en esta tabla
        o en sus entornos padres (alcance léxico).
        '''
        env = self
        while env is not None:
            if name in env.entries:
                return True
            env = env.parent
        return False

    def add(self, name, value):
        '''
        Agrega un símbolo con el valor dado a la tabla de símbolos.
        El valor suele ser un nodo AST que representa la declaración
        o definición de una función, variable, etc.
        '''
        if name in self.entries:
            if getattr(self.entries[name], "dtype", None) != getattr(value, "dtype", None):
                raise Symtab.SymbolConflictError()
            else:
                raise Symtab.SymbolDefinedError()
        self.entries[name] = value

    def get(self, name):
        '''
        Recupera el símbolo con el nombre dado de la tabla de
        símbolos, recorriendo hacia arriba a través de las tablas
        de símbolos principales si no se encuentra en la actual.
        '''
        if name in self.entries:
            return self.entries[name]
        elif self.parent:
            return self.parent.get(name)
        return None

    def print(self):
        table = Table(title = f"Symbol Table: '{self.name}'")
        table.add_column('key', style='cyan')
        table.add_column('value', style='bright_green')

        for k, v in self.entries.items():
            value = f"{v.__class__.__name__}({v.name})"
            table.add_row(k, value)
        print(table, '\n')

        for child in self.children:
            child.print()
