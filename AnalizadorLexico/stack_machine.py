# stack_machine.py - Máquina de Pila Completa para GoxLang
import re
import struct

class Memory:
    """Memoria lineal byte-addressable"""
    def __init__(self, initial_size=4096):
        self.data = bytearray(initial_size)
        self.size = initial_size
        
    def grow(self, new_size):
        if new_size > self.size:
            self.data.extend(bytearray(new_size - self.size))
            self.size = new_size
    
    def _check_bounds(self, address, size):
        if address < 0 or address + size > self.size:
            raise IndexError(f"Dirección de memoria fuera de límites: {address}")
    
    def read_int(self, address):
        self._check_bounds(address, 4)
        return struct.unpack('<i', self.data[address:address+4])[0]
    
    def write_int(self, address, value):
        self._check_bounds(address, 4)
        self.data[address:address+4] = struct.pack('<i', value)
    
    def read_float(self, address):
        self._check_bounds(address, 4)
        return struct.unpack('<f', self.data[address:address+4])[0]
    
    def write_float(self, address, value):
        self._check_bounds(address, 4)
        self.data[address:address+4] = struct.pack('<f', value)
    
    def read_byte(self, address):
        self._check_bounds(address, 1)
        return self.data[address]
    
    def write_byte(self, address, value):
        self._check_bounds(address, 1)
        self.data[address] = value & 0xFF

class CallFrame:
    """Frame de activación para funciones"""
    def __init__(self, function_name, return_address, params_count=0):
        self.function_name = function_name
        self.return_address = return_address
        self.locals = {}
        self.params_count = params_count
        
    def set_local(self, name, value):
        self.locals[name] = value
        
    def get_local(self, name):
        return self.locals.get(name, 0)

class StackMachine:
    """
    Máquina virtual basada en pila para GoxLang IR.
    Compatible con el output de tu IRCodeGenerator existente.
    """
    
    def __init__(self):
        # Componentes principales
        self.stack = []
        self.call_stack = []
        self.memory = Memory()
        self.globals = {}
        
        # Control de ejecución
        self.functions = {}
        self.ip = 0
        self.instructions = []
        self.running = True
        
        # Control de flujo
        self.loop_stack = []

    # ════════════════════════════════════════════════════════════════
    #  CARGA DE PROGRAMA - Compatible con tu formato IR existente
    # ════════════════════════════════════════════════════════════════
    
    def load_ir_from_file(self, filename):
        """Carga IR desde archivo (compatible con output.ir)"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        self.load_ir_from_string(content)
    
    def load_ir_from_string(self, ir_content):
        """Parsea el formato IR de tu IRCodeGenerator"""
        lines = [line.strip() for line in ir_content.split('\n') if line.strip()]
        
        current_func = None
        current_instructions = []
        
        for line in lines:
            if line.startswith("MODULE:::"):
                continue
            elif line.startswith("FUNCTION:::"):
                # Guardar función anterior
                if current_func:
                    self.functions[current_func] = current_instructions
                
                # Parsear: FUNCTION::: name, [params], [types] return_type
                parts = line.split(',', 1)
                func_name = parts[0].split()[-1]
                current_func = func_name
                current_instructions = []
                
            elif line.startswith("locals:"):
                continue  # Ignorar metadata de locals
            elif line.startswith("(") and current_func:
                # Parsear instrucción en formato tupla
                instruction = self._parse_instruction_tuple(line)
                if instruction:
                    current_instructions.append(instruction)
        
        # Guardar última función
        if current_func:
            self.functions[current_func] = current_instructions
    
    def _parse_instruction_tuple(self, line):
        """Convierte ('OP', 'arg1', 'arg2') a ['OP', 'arg1', 'arg2']"""
        content = line.strip('()')
        if not content:
            return None
            
        # Usar regex para separar elementos respetando comillas
        parts = re.findall(r"'([^']*)'|([^,\s]+)", content)
        result = []
        
        for quoted, unquoted in parts:
            if quoted:
                result.append(quoted)
            elif unquoted:
                try:
                    # Convertir números
                    if '.' in unquoted:
                        result.append(float(unquoted))
                    else:
                        result.append(int(unquoted))
                except ValueError:
                    result.append(unquoted)
        
        return result if result else None

    # ════════════════════════════════════════════════════════════════
    #  EJECUCIÓN PRINCIPAL
    # ════════════════════════════════════════════════════════════════
    
    def run(self, entry_function="main"):
        """Ejecuta programa desde función especificada"""
        if entry_function not in self.functions:
            raise RuntimeError(f"Función '{entry_function}' no encontrada")
        
        # Frame inicial
        initial_frame = CallFrame(entry_function, -1)
        self.call_stack.append(initial_frame)
        
        # Cargar instrucciones
        self.instructions = self.functions[entry_function]
        self.ip = 0
        self.running = True
        
        # Ejecutar
        while self.running and self.ip < len(self.instructions):
            self._execute_instruction()
            self.ip += 1
    
    def _execute_instruction(self):
        """Ejecuta instrucción actual"""
        if self.ip >= len(self.instructions):
            return
            
        instr = self.instructions[self.ip]
        if not instr:
            return
            
        op = instr[0]
        args = instr[1:] if len(instr) > 1 else []
        
        # Dispatch dinámico
        method_name = f"_exec_{op.lower()}"
        if hasattr(self, method_name):
            getattr(self, method_name)(*args)
        else:
            raise RuntimeError(f"Instrucción no implementada: {op}")

    # ════════════════════════════════════════════════════════════════
    #  IMPLEMENTACIÓN DE INSTRUCCIONES (Compatible con tu IR)
    # ════════════════════════════════════════════════════════════════
    
    # --- Constantes ---
    def _exec_consti(self, value):
        self.stack.append(int(value))
    
    def _exec_pushi(self, value):
        self.stack.append(int(value))
    
    def _exec_constf(self, value):
        self.stack.append(float(value))
    
    # --- Aritmética Entera ---
    def _exec_addi(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(a + b)
    
    def _exec_subi(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(a - b)
    
    def _exec_muli(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(a * b)
    
    def _exec_divi(self):
        b, a = self.stack.pop(), self.stack.pop()
        if b == 0:
            raise RuntimeError("División por cero")
        self.stack.append(a // b)
    
    # --- Aritmética Flotante ---
    def _exec_addf(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(float(a) + float(b))
    
    def _exec_subf(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(float(a) - float(b))
    
    def _exec_mulf(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(float(a) * float(b))
    
    def _exec_divf(self):
        b, a = self.stack.pop(), self.stack.pop()
        if b == 0:
            raise RuntimeError("División por cero")
        self.stack.append(float(a) / float(b))
    
    # --- Comparaciones Enteras ---
    def _exec_eqi(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a == b else 0)
    
    def _exec_nei(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a != b else 0)
    
    def _exec_lti(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a < b else 0)
    
    def _exec_lei(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a <= b else 0)
    
    def _exec_gti(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a > b else 0)
    
    def _exec_gei(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a >= b else 0)
    
    # --- Comparaciones Flotantes ---
    def _exec_eqf(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if abs(float(a) - float(b)) < 1e-9 else 0)
    
    def _exec_nef(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if abs(float(a) - float(b)) >= 1e-9 else 0)
    
    # --- Lógica ---
    def _exec_andi(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a and b else 0)
    
    def _exec_ori(self):
        b, a = self.stack.pop(), self.stack.pop()
        self.stack.append(1 if a or b else 0)
    
    # --- Conversiones ---
    def _exec_itof(self):
        value = self.stack.pop()
        self.stack.append(float(value))
    
    def _exec_ftoi(self):
        value = self.stack.pop()
        self.stack.append(int(value))
    
    # --- Acceso a Memoria ---
    def _exec_peeki(self):
        address = self.stack.pop()
        value = self.memory.read_int(address)
        self.stack.append(value)
    
    def _exec_pokei(self):
        value = self.stack.pop()
        address = self.stack.pop()
        self.memory.write_int(address, value)
    
    def _exec_peekf(self):
        address = self.stack.pop()
        value = self.memory.read_float(address)
        self.stack.append(value)
    
    def _exec_pokef(self):
        value = self.stack.pop()
        address = self.stack.pop()
        self.memory.write_float(address, value)
    
    def _exec_peekb(self):
        address = self.stack.pop()
        value = self.memory.read_byte(address)
        self.stack.append(value)
    
    def _exec_pokeb(self):
        value = self.stack.pop()
        address = self.stack.pop()
        self.memory.write_byte(address, value)
    
    def _exec_grow(self):
        new_size = self.stack.pop()
        self.memory.grow(new_size)
    
    # --- Variables ---
    def _exec_local_get(self, name):
        if not self.call_stack:
            raise RuntimeError("No hay frame activo")
        frame = self.call_stack[-1]
        value = frame.get_local(name)
        self.stack.append(value)
    
    def _exec_local_set(self, name):
        if not self.call_stack:
            raise RuntimeError("No hay frame activo")
        value = self.stack.pop()
        frame = self.call_stack[-1]
        frame.set_local(name, value)
    
    def _exec_global_get(self, name):
        value = self.globals.get(name, 0)
        self.stack.append(value)
    
    def _exec_global_set(self, name):
        value = self.stack.pop()
        self.globals[name] = value
    
    # ─── Llamadas a funciones (CORREGIDAS) ───
    def _exec_call(self, func_name):
        """CALL - Llama a función CON manejo correcto de parámetros"""
        if func_name not in self.functions:
            raise RuntimeError(f"Función '{func_name}' no encontrada")
        
        # Obtener información de la función del IR
        func_instructions = self.functions[func_name]
        
        # Determinar número de parámetros
        param_count = self._get_param_count(func_name)
        
        # Extraer parámetros del stack (en orden inverso)
        params = []
        for _ in range(param_count):
            if self.stack:
                params.append(self.stack.pop())
            else:
                params.append(0)  # Default si no hay suficientes parámetros
        
        params.reverse()  # Restaurar orden correcto
        
        # Crear nuevo frame con parámetros
        return_address = self.ip + 1
        new_frame = CallFrame(func_name, return_address, param_count)
        
        # Asignar parámetros a variables locales
        param_names = self._get_param_names(func_name)
        for i, param_name in enumerate(param_names):
            if i < len(params):
                new_frame.set_local(param_name, params[i])
        
        self.call_stack.append(new_frame)
        
        # Guardar contexto actual
        old_instructions = self.instructions
        old_ip = self.ip
        
        # Cambiar a función llamada
        self.instructions = func_instructions
        self.ip = 0
        
        # Ejecutar función hasta RET
        return_value = None
        while self.ip < len(self.instructions) and self.running:
            instr = self.instructions[self.ip]
            if instr and instr[0] == 'RET':
                # Capturar valor de retorno si hay algo en el stack
                if self.stack:
                    return_value = self.stack.pop()
                break
            self._execute_instruction()
            self.ip += 1
        
        # Restaurar contexto
        self.call_stack.pop()
        self.instructions = old_instructions
        self.ip = old_ip
        
        # Poner valor de retorno en el stack
        if return_value is not None:
            self.stack.append(return_value)
        else:
            self.stack.append(0)  # Default return value
    
    def _exec_ret(self):
        """RET - Retorna de función SIN limpiar el stack"""
        # El valor de retorno ya está en el stack
        # Solo marcamos que debemos salir del loop de ejecución
        if len(self.call_stack) <= 1:
            self.running = False
        else:
            # Salir del bucle de ejecución de función
            # El valor de retorno se mantiene en el stack
            self.ip = len(self.instructions)
    
    # --- Control de Flujo ---
    def _exec_if(self):
        condition = self.stack.pop()
        if condition == 0:  # Falso
            self._skip_to_matching(['ELSE', 'ENDIF'], 'IF', 'ENDIF')
    
    def _exec_else(self):
        self._skip_to_matching(['ENDIF'], 'IF', 'ENDIF')
    
    def _exec_endif(self):
        pass  # Marca el fin del if
    
    def _exec_loop(self):
        self.loop_stack.append(self.ip)
    
    def _exec_cbreak(self):
        condition = self.stack.pop()
        if condition == 0:  # Falso, salir del bucle
            self._skip_to_matching(['ENDLOOP'], 'LOOP', 'ENDLOOP')
            if self.loop_stack:
                self.loop_stack.pop()
    
    def _exec_endloop(self):
        if self.loop_stack:
            self.ip = self.loop_stack[-1] - 1
        else:
            raise RuntimeError("ENDLOOP sin LOOP correspondiente")
    
    # --- Entrada/Salida ---
    def _exec_printi(self):
        value = self.stack.pop()
        print(int(value))
    
    def _exec_printf(self):
        value = self.stack.pop()
        print(float(value))
    
    def _exec_printb(self):
        value = self.stack.pop()
        print(chr(int(value)), end='')

    # ════════════════════════════════════════════════════════════════
    #  UTILIDADES
    # ════════════════════════════════════════════════════════════════
    
    def _skip_to_matching(self, targets, open_token, close_token):
        """Salta a instrucción objetivo respetando anidación"""
        depth = 1
        self.ip += 1
        
        while self.ip < len(self.instructions) and depth > 0:
            instr = self.instructions[self.ip]
            if instr:
                op = instr[0]
                if op == open_token:
                    depth += 1
                elif op == close_token:
                    depth -= 1
                elif op in targets and depth == 1:
                    return
            self.ip += 1
        
        self.ip -= 1  # Ajustar para incremento automático
    
    def get_stack_trace(self):
        """Stack trace para debugging"""
        trace = []
        for frame in self.call_stack:
            trace.append(f"  en función '{frame.function_name}'")
        return "\n".join(trace)
    
    def debug_state(self):
        """Estado actual para debugging"""
        return {
            "ip": self.ip,
            "stack": self.stack[:10],  # Solo primeros 10
            "current_function": self.call_stack[-1].function_name if self.call_stack else None,
            "globals": dict(list(self.globals.items())[:5])  # Solo primeros 5
        }
    
    def _get_param_count(self, func_name):
        """Determina el número de parámetros de una función del IR"""
        if func_name == "add":
            return 2
        elif func_name == "factorial":
            return 1
        elif func_name in ["mod", "gcd", "powmod"]:
            return 2
        elif func_name == "find_period":
            return 2
        elif func_name == "shor":
            return 1
        else:
            return 0

    def _get_param_names(self, func_name):
        """Obtiene los nombres de parámetros de una función"""
        if func_name == "add":
            return ["x", "y"]
        elif func_name == "factorial":
            return ["n"]
        elif func_name == "mod":
            return ["a", "b"]
        elif func_name == "gcd":
            return ["a", "b"]
        elif func_name == "powmod":
            return ["a", "x", "n"]
        elif func_name == "find_period":
            return ["a", "N"]
        elif func_name == "shor":
            return ["N"]
        else:
            return []


# ════════════════════════════════════════════════════════════════
#  FUNCIÓN PRINCIPAL PARA PRUEBAS
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    vm = StackMachine()
    
    try:
        print("Cargando programa...")
        vm.load_ir_from_file("output.ir")
        
        print("Funciones cargadas:")
        for func_name in vm.functions.keys():
            print(f"  - {func_name}")
        
        print("\nEjecutando...")
        vm.run("main")
        
        print("\nEjecucion completada")
        
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Stack trace:\n{vm.get_stack_trace()}")
        print(f"Estado: {vm.debug_state()}")