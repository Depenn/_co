import sys
import os

class VMTranslator:
    def __init__(self, input_path):
        self.input_path = input_path
        self.label_counter = 0
        self.ret_counter = 0
        self.lines = []
        
        # Determine output filename
        if os.path.isdir(input_path):
            self.dir_name = os.path.basename(os.path.normpath(input_path))
            self.output_file = os.path.join(input_path, f"{self.dir_name}.asm")
            self.is_dir = True
        else:
            self.output_file = input_path.replace('.vm', '.asm')
            self.dir_name = os.path.basename(input_path).replace('.vm', '')
            self.is_dir = False
            
        self.current_filename = "" # For static variables

    def translate(self):
        vm_files = []
        if self.is_dir:
            # Get all .vm files in directory
            vm_files = [os.path.join(self.input_path, f) for f in os.listdir(self.input_path) if f.endswith('.vm')]
        else:
            vm_files = [self.input_path]

        with open(self.output_file, 'w') as f:
            # 1. Write Bootstrap Code
            # Cuma inject bootstrap kalo ada Sys.vm (indikator Full Program)
            # SimpleFunction, BasicLoop, dll GAK BOLEH pake bootstrap.
            if 'Sys.vm' in [os.path.basename(vf) for vf in vm_files]:
                f.write("// Bootstrap Code\n")
                f.write("@256\nD=A\n@SP\nM=D\n") # SP = 256
                # Call Sys.init
                f.write("\n".join(self.write_call("Sys.init", 0)) + "\n")

            # 2. Process each file
            for vm_file in vm_files:
                self.current_filename = os.path.basename(vm_file).replace('.vm', '')
                f.write(f"// --- Processing {self.current_filename} ---\n")
                
                with open(vm_file, 'r') as vf:
                    for line in vf:
                        line = line.split('//')[0].strip()
                        if not line: continue
                        
                        f.write(f"// {line}\n")
                        parts = line.split()
                        command = parts[0]
                        
                        code = []
                        if command == 'push':
                            code = self.write_push(parts[1], int(parts[2]))
                        elif command == 'pop':
                            code = self.write_pop(parts[1], int(parts[2]))
                        elif command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
                            code = self.write_arithmetic(command)
                        elif command == 'label':
                            code = [f"({parts[1]})"]
                        elif command == 'goto':
                            code = [f"@{parts[1]}", "0;JMP"]
                        elif command == 'if-goto':
                            # Pop logic: value != 0 means True
                            code = self.pop_stack_to_D() + [f"@{parts[1]}", "D;JNE"]
                        elif command == 'function':
                            code = self.write_function(parts[1], int(parts[2]))
                        elif command == 'return':
                            code = self.write_return()
                        elif command == 'call':
                            code = self.write_call(parts[1], int(parts[2]))
                            
                        f.write('\n'.join(code) + '\n')
                        
        print(f"Generated: {self.output_file}")

    # --- HELPERS ---
    def pop_stack_to_D(self):
        return ["@SP", "AM=M-1", "D=M"]
    
    def pop_stack_to_D_and_M(self):
        return ["@SP", "AM=M-1", "D=M", "A=A-1"]

    def push_D_to_stack(self):
        return ["@SP", "A=M", "M=D", "@SP", "M=M+1"]

    # --- LOGIC ---
    def write_arithmetic(self, command):
        if command == 'add': return self.pop_stack_to_D_and_M() + ["M=M+D"]
        if command == 'sub': return self.pop_stack_to_D_and_M() + ["M=M-D"]
        if command == 'and': return self.pop_stack_to_D_and_M() + ["M=M&D"]
        if command == 'or':  return self.pop_stack_to_D_and_M() + ["M=M|D"]
        if command == 'neg': return ["@SP", "A=M-1", "M=-M"]
        if command == 'not': return ["@SP", "A=M-1", "M=!M"]
        
        if command in ['eq', 'gt', 'lt']:
            lbl_t = f"TRUE_{self.label_counter}"
            lbl_e = f"END_{self.label_counter}"
            self.label_counter += 1
            jmp = {'eq':'JEQ', 'gt':'JGT', 'lt':'JLT'}[command]
            return self.pop_stack_to_D_and_M() + [
                "D=M-D", f"@{lbl_t}", f"D;{jmp}",
                "@SP", "A=M-1", "M=0", f"@{lbl_e}", "0;JMP",
                f"({lbl_t})", "@SP", "A=M-1", "M=-1", f"({lbl_e})"
            ]
        return []

    def write_push(self, segment, index):
        if segment == 'constant': return [f"@{index}", "D=A"] + self.push_D_to_stack()
        
        ptr_map = {'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT'}
        if segment in ptr_map:
            return [f"@{ptr_map[segment]}", "D=M", f"@{index}", "A=D+A", "D=M"] + self.push_D_to_stack()
        
        if segment == 'temp': return [f"@{5+index}", "D=M"] + self.push_D_to_stack()
        if segment == 'pointer': return [f"@{3+index}", "D=M"] + self.push_D_to_stack()
        if segment == 'static': return [f"@{self.current_filename}.{index}", "D=M"] + self.push_D_to_stack()
        return []

    def write_pop(self, segment, index):
        ptr_map = {'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT'}
        if segment in ptr_map:
            return [f"@{ptr_map[segment]}", "D=M", f"@{index}", "D=D+A", "@R13", "M=D"] + \
                   self.pop_stack_to_D() + ["@R13", "A=M", "M=D"]
                   
        if segment == 'temp': return self.pop_stack_to_D() + [f"@{5+index}", "M=D"]
        if segment == 'pointer': return self.pop_stack_to_D() + [f"@{3+index}", "M=D"]
        if segment == 'static': return self.pop_stack_to_D() + [f"@{self.current_filename}.{index}", "M=D"]
        return []

    # --- PROJECT 8 SPECIFIC ---
    
    def write_function(self, func_name, num_locals):
        # (func_name)
        # repeat num_locals times: push 0
        code = [f"({func_name})"]
        for _ in range(num_locals):
            code.extend(["@0", "D=A"] + self.push_D_to_stack())
        return code

    def write_call(self, func_name, num_args):
        ret_label = f"{func_name}$ret.{self.ret_counter}"
        self.ret_counter += 1
        
        # 1. Push return-address
        code = [f"@{ret_label}", "D=A"] + self.push_D_to_stack()
        # 2. Push LCL, ARG, THIS, THAT
        for seg in ['LCL', 'ARG', 'THIS', 'THAT']:
            code.extend([f"@{seg}", "D=M"] + self.push_D_to_stack())
        
        # 3. ARG = SP - n - 5
        code.extend(["@SP", "D=M", f"@{num_args}", "D=D-A", "@5", "D=D-A", "@ARG", "M=D"])
        # 4. LCL = SP
        code.extend(["@SP", "D=M", "@LCL", "M=D"])
        # 5. goto f
        code.extend([f"@{func_name}", "0;JMP"])
        # 6. (return-address)
        code.append(f"({ret_label})")
        return code

    def write_return(self):
        # FRAME = LCL (saved in R13)
        # RET = *(FRAME-5) (saved in R14)
        code = ["@LCL", "D=M", "@R13", "M=D", # R13 = FRAME
                "@5", "A=D-A", "D=M", "@R14", "M=D"] # R14 = RET
        
        # *ARG = pop()
        code.extend(self.pop_stack_to_D() + ["@ARG", "A=M", "M=D"])
        
        # SP = ARG + 1
        code.extend(["@ARG", "D=M+1", "@SP", "M=D"])
        
        # Restore THAT, THIS, ARG, LCL
        # THAT = *(FRAME-1), THIS=*(FRAME-2), etc.
        offsets = {'THAT':1, 'THIS':2, 'ARG':3, 'LCL':4}
        for seg, off in offsets.items():
            code.extend(["@R13", "D=M", f"@{off}", "A=D-A", "D=M", f"@{seg}", "M=D"])
            
        # goto RET
        code.extend(["@R14", "A=M", "0;JMP"])
        return code

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <input_file.vm OR input_directory>")
    else:
        translator = VMTranslator(sys.argv[1])
        translator.translate()