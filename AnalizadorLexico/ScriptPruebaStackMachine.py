# test_stack_machine.py - Pruebas para Stack Machine (version Windows)

import os
import subprocess
import tempfile

def test_basic_arithmetic():
    """Prueba operaciones aritmeticas basicas"""
    test_code = """
    var a int = 10;
    var b int = 5;
    var result int = a + b * 2;
    print result;
    """
    return run_test("arithmetic", test_code, expected_output="20")

def test_function_calls():
    """Prueba llamadas a funciones"""
    test_code = """
    func add(x int, y int) int {
        return x + y;
    }
    
    var result int = add(5, 3);
    print result;
    """
    return run_test("functions", test_code, expected_output="8")

def test_conditionals():
    """Prueba condicionales"""
    test_code = """
    var x int = 10;
    if (x > 5) {
        print 1;
    } else {
        print 0;
    }
    """
    return run_test("conditionals", test_code, expected_output="1")

def test_loops():
    """Prueba bucles"""
    test_code = """
    var i int = 0;
    var sum int = 0;
    while (i < 3) {
        sum = sum + i;
        i = i + 1;
    }
    print sum;
    """
    return run_test("loops", test_code, expected_output="3")

def test_recursive_functions():
    """Prueba funciones recursivas"""
    test_code = """
    func factorial(n int) int {
        if (n <= 1) {
            return 1;
        } else {
            return n * factorial(n - 1);
        }
    }
    
    var result int = factorial(4);
    print result;
    """
    return run_test("recursion", test_code, expected_output="24")

def test_complex_program():
    """Prueba el programa shor.gox existente"""
    if os.path.exists("shor.gox"):
        return run_test_file("shor.gox", "complex_shor")
    else:
        print("WARNING: shor.gox no encontrado, saltando prueba compleja")
        return True

def run_test(test_name, code, expected_output=None):
    """Ejecuta una prueba individual"""
    print(f"EJECUTANDO PRUEBA: {test_name}")
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gox', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Ejecutar con stack machine
        result = subprocess.run(
            ['python', 'main.py', temp_file, '--execute'],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            if expected_output and expected_output in result.stdout:
                print(f"    OK: {test_name} - PASSED")
                return True
            elif expected_output:
                print(f"    ERROR: {test_name} - FAILED")
                print(f"       Esperado: {expected_output}")
                print(f"       Obtenido: {result.stdout.strip()}")
                return False
            else:
                print(f"    OK: {test_name} - EXECUTED (sin verificacion de salida)")
                return True
        else:
            print(f"    ERROR: {test_name} - ERROR")
            print(f"       Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"    ERROR: {test_name} - TIMEOUT")
        return False
    except Exception as e:
        print(f"    ERROR: {test_name} - EXCEPTION: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        try:
            os.unlink(temp_file)
        except:
            pass

def run_test_file(filename, test_name):
    """Ejecuta prueba desde archivo existente"""
    print(f"EJECUTANDO PRUEBA DE ARCHIVO: {test_name}")
    
    try:
        result = subprocess.run(
            ['python', 'main.py', filename, '--execute'],
            capture_output=True,
            text=True,
            timeout=15,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"    OK: {test_name} - EXECUTED")
            print(f"       Salida: {result.stdout.strip()[:100]}...")
            return True
        else:
            print(f"    ERROR: {test_name} - ERROR")
            print(f"       Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"    ERROR: {test_name} - TIMEOUT")
        return False
    except Exception as e:
        print(f"    ERROR: {test_name} - EXCEPTION: {e}")
        return False

def test_vm_comparison():
    """Compara VM original vs Stack Machine"""
    test_code = """
    func add(a int, b int) int {
        return a + b;
    }
    
    var x int = add(3, 4);
    print x;
    """
    
    print("COMPARANDO VMs...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gox', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ['python', 'main.py', temp_file, '--compare-vm'],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"    OK: Comparacion completada")
            print("    Salida de comparacion:")
            for line in result.stdout.split('\n')[-10:]:  # Ultimas 10 lineas
                if line.strip():
                    print(f"       {line}")
            return True
        else:
            print(f"    ERROR en comparacion: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"    ERROR: Excepcion en comparacion: {e}")
        return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("INICIANDO SUITE DE PRUEBAS PARA STACK MACHINE")
    print("=" * 60)
    
    tests = [
        test_basic_arithmetic,
        test_function_calls,
        test_conditionals,
        test_loops,
        test_recursive_functions,
        test_complex_program,
        test_vm_comparison
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"    ERROR ejecutando prueba: {e}")
        print()  # Linea en blanco entre pruebas
    
    print("=" * 60)
    print(f"RESULTADOS: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("TODAS LAS PRUEBAS PASARON! Stack Machine funciona correctamente.")
        return True
    else:
        print(f"WARNING: {total - passed} pruebas fallaron. Revisar implementacion.")
        return False

def test_specific_ir_instructions():
    """Prueba instrucciones especificas del IR"""
    print("PROBANDO INSTRUCCIONES ESPECIFICAS DEL IR...")
    
    # Test GLOBAL_SET/GET
    test_code = """
    var global_var int = 42;
    print global_var;
    """
    
    if run_test("global_vars", test_code, "42"):
        print("    OK: Variables globales funcionan")
    else:
        print("    ERROR: Error en variables globales")
    
    # Test LOCAL_SET/GET
    test_code = """
    func test_locals() int {
        var local_var int = 99;
        return local_var;
    }
    
    print test_locals();
    """
    
    if run_test("local_vars", test_code, "99"):
        print("    OK: Variables locales funcionan")
    else:
        print("    ERROR: Error en variables locales")

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("main.py"):
        print("ERROR: main.py no encontrado. Ejecutar desde el directorio del proyecto.")
        exit(1)
    
    if not os.path.exists("stack_machine.py"):
        print("ERROR: stack_machine.py no encontrado. Asegurate de haber creado el archivo.")
        exit(1)
    
    # Ejecutar pruebas
    success = run_all_tests()
    
    # Pruebas adicionales
    print("\nPRUEBAS ADICIONALES DE INSTRUCCIONES:")
    test_specific_ir_instructions()
    
    print("\n" + "=" * 60)
    if success:
        print("STACK MACHINE ESTA LISTA PARA USAR!")
        print("\nCOMANDOS UTILES:")
        print("   python main.py archivo.gox --execute")
        print("   python main.py archivo.gox --vm-debug") 
        print("   python main.py archivo.gox --compare-vm")
    else:
        print("HAY PROBLEMAS QUE NECESITAN SER CORREGIDOS.")
    
    exit(0 if success else 1)