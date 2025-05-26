# debug_test.py - Test simple para debugging

# Crear archivo de prueba muy simple
test_content = """
var x int = 5;
print x;
"""

with open("debug_simple.gox", "w", encoding="utf-8") as f:
    f.write(test_content)

print("Archivo debug_simple.gox creado")
print("Ejecuta: python main.py debug_simple.gox --vm-debug")