import json 
from rich.console import Console
from rich.table import Table

def symtab_to_dict(symtab):
    return {
        "name": symtab.name,
        "symbols": {
            k: v.__class__.__name__ for k, v in symtab.entries.items()
        },
        "children": [symtab_to_dict(child) for child in symtab.children]
    }

def save_symbol_table_json(symtab, output_file="symbol_table.json"):
    data = symtab_to_dict(symtab)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def print_symbol_table(symtab, title="Symbol Table"):
    if not symtab.entries:  # Oculta tablas vacías
        return

    console = Console()
    table = Table(title=f"{title}: '{symtab.name}'", show_lines=True)
    table.add_column("Símbolo", style="cyan", no_wrap=True)
    table.add_column("Tipo de nodo", style="green", no_wrap=True)
    table.add_column("Tipo declarado", style="magenta", no_wrap=True)

    for name, node in symtab.entries.items():
        node_type = node.__class__.__name__
        dtype = getattr(node, "type", getattr(node, "dtype", "-"))
        table.add_row(name, node_type, str(dtype).lower())

    console.print(table)
    for child in symtab.children:
        print_symbol_table(child, title="Subtabla")
