# main.py - Pipeline completo con Stack Machine integrada (version Windows)
import sys
from lexer import tokenize
from parser import Parser
from check import Checker
from ast_utility import generate_json_output, save_ast_graph
from symtab_utility import save_symbol_table_json
from ircode import IRCodeGenerator
from stack_machine import StackMachine  # Nueva máquina de pila

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.gox [opciones]")
        print("   Opciones:")
        print("     --execute     : Ejecuta con Stack Machine")
        print("     --vm-debug    : Ejecuta con informacion de debug")
        print("     --compare-vm  : Compara VM vieja vs Stack Machine")
        return

    filepath = sys.argv[1]
    should_execute = "--execute" in sys.argv
    debug_mode = "--vm-debug" in sys.argv
    compare_vms = "--compare-vm" in sys.argv

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"ERROR: No se pudo encontrar el archivo '{filepath}'")
        return
    except Exception as e:
        print(f"ERROR al leer el archivo: {e}")
        return

    print("Iniciando compilacion de GoxLang...")
    print("=" * 60)

    # ═══════════════════════════════════════════════════════════════
    #  FASE 1: ANÁLISIS LÉXICO
    # ═══════════════════════════════════════════════════════════════
    print("[1/6] Analisis lexico...")
    try:
        tokens = tokenize(source)
        print(f"    OK: {len(tokens)} tokens generados")
        print(tokens)
    except Exception as e:
        print(f"    ERROR lexico: {e}")
        return

    # ═══════════════════════════════════════════════════════════════
    #  FASE 2: ANÁLISIS SINTÁCTICO
    # ═══════════════════════════════════════════════════════════════
    print("[2/6] Analisis sintactico...")
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        if parser.errors:
            print("    ERROR de parsing:")
            for err in parser.errors:
                print(f"      • {err}")
            return
        print(f"    OK: AST generado con {len(ast.decls)} declaraciones")
    except Exception as e:
        print(f"    ERROR sintactico: {e}")
        return

    # ═══════════════════════════════════════════════════════════════
    #  FASE 3: ANÁLISIS SEMÁNTICO
    # ═══════════════════════════════════════════════════════════════
    print("[3/6] Analisis semantico...")
    try:
        checker = Checker()
        errores = checker.check(ast)
        if errores:
            print("    ERROR semanticos:")
            for err in errores:
                print(f"      • {err}")
            return
        print("    OK: Analisis semantico exitoso")
    except Exception as e:
        print(f"    ERROR en analisis semantico: {e}")
        return

    # ═══════════════════════════════════════════════════════════════
    #  FASE 4: GENERACIÓN DE CÓDIGO INTERMEDIO
    # ═══════════════════════════════════════════════════════════════
    print("[4/6] Generando codigo intermedio (IR)...")
    try:
        ir_generator = IRCodeGenerator()
        module_ir = ir_generator.generate(ast.decls)
        ir_content = module_ir.dump()
        
        # Guardar IR
        with open("output.ir", "w", encoding="utf-8") as f:
            f.write(ir_content)
        print("    OK: IR generado y guardado en 'output.ir'")
    except Exception as e:
        print(f"    ERROR generando IR: {e}")
        return

    # ═══════════════════════════════════════════════════════════════
    #  FASE 5: GENERACIÓN DE ARCHIVOS DE ANÁLISIS
    # ═══════════════════════════════════════════════════════════════
    print("[5/6] Generando archivos de analisis...")
    try:
        generate_json_output(ast)
        save_ast_graph(ast)
        save_symbol_table_json(checker.symtab)
        print("    OK: Archivos generados: ast_output.json, ast_graph.png, symbol_table.json")
    except Exception as e:
        print(f"    WARNING: Error generando archivos de analisis: {e}")

    print("=" * 60)
    print("COMPILACION EXITOSA!")

    # ═══════════════════════════════════════════════════════════════
    #  FASE 6: EJECUCIÓN (OPCIONAL)
    # ═══════════════════════════════════════════════════════════════
    
    if compare_vms:
        print("\n[6/6] Comparando VMs...")
        print("=" * 60)
        
        # VM Original
        print("Ejecutando con VM original:")
        try:
            from vm import VirtualMachine  # Tu VM original
            old_vm = VirtualMachine()
            old_vm.load_ir("output.ir")
            old_vm.run("main")
        except Exception as e:
            print(f"    ERROR en VM original: {e}")
        
        print("\n" + "-" * 40)
        
        # Stack Machine Nueva
        print("Ejecutando con Stack Machine:")
        try:
            new_vm = StackMachine()
            new_vm.load_ir_from_string(ir_content)
            new_vm.run("main")
        except Exception as e:
            print(f"    ERROR en Stack Machine: {e}")
            if debug_mode:
                print(f"    Stack trace: {new_vm.get_stack_trace()}")
                print(f"    Estado: {new_vm.debug_state()}")
    
    elif should_execute:
        print("\n[6/6] Ejecutando con Stack Machine...")
        print("=" * 60)
        
        try:
            vm = StackMachine()
            vm.load_ir_from_string(ir_content)
            
            if debug_mode:
                print("Funciones cargadas:")
                for func_name in vm.functions.keys():
                    print(f"    • {func_name}")
                print()
            
            vm.run("main")
            
            if debug_mode:
                print(f"\nEstado final: {vm.debug_state()}")
            
            print("\nEJECUCION COMPLETADA EXITOSAMENTE")
            
        except Exception as e:
            print(f"\nERROR durante la ejecucion: {e}")
            if debug_mode and 'vm' in locals():
                print(f"\nStack trace de la VM:")
                print(vm.get_stack_trace())
                print(f"\nEstado al momento del error:")
                print(vm.debug_state())
    
    else:
        print("\nPara ejecutar el programa:")
        print("   python main.py archivo.gox --execute")
        print("   python main.py archivo.gox --vm-debug")
        print("   python main.py archivo.gox --compare-vm")


if __name__ == "__main__":
    main()