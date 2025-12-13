import sys
import os

class VMTranslator:
    def __init__(self, input_file):
        self.input_file = input_file
        # Nama file tanpa ekstensi untuk static variable (misal: "StaticTest")
        self.filename = os.path.basename(input_file).replace('.vm', '')
        self.label_counter = 0 # Penting buat EQ, GT, LT biar label gak tabrakan

    def translate(self):
        output_file = self.input_file.replace('.vm', '.asm')
        
        with open(self.input_file, 'r') as f:
            lines = f.readlines()

        asm_code = []
        
        for line in lines:
            line = self.clean_line(line)
            if not line: continue
            
            parts = line.split()
            command = parts[0]
            
            asm_code.append(f"// {line}") # Debugging comments di output
            
            if command == 'push':
                segment = parts[1]
                index = int(parts[2])
                asm_code.extend(self.write_push(segment, index))
            
            elif command == 'pop':
                segment = parts[1]
                index = int(parts[2])
                asm_code.extend(self.write_pop(segment, index))
                
            elif command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
                asm_code.extend(self.write_arithmetic(command))

        with open(output_file, 'w') as f:
            f.write('\n'.join(asm_code) + '\n')
        
        print(f"Generated: {output_file}")

    def clean_line(self, line):
        return line.split('//')[0].strip()

    # --- CORE HELPER: STACK OPERATIONS ---
    
    # Template: Ambil nilai paling atas stack ke D, lalu kurangi SP
    def pop_stack_to_D(self):
        return [
            "@SP",
            "M=M-1", # SP mundur 1
            "A=M",   # Point ke data
            "D=M"    # Simpan data di D
        ]
    
    # Template: Ambil nilai stack ke D, dan stack sebelumnya ke M (buat operasi 2 angka)
    # Hasil akhir: D = Top, M = Second Top. SP mundur 1.
    def pop_stack_to_D_and_M(self):
        return [
            "@SP",
            "AM=M-1", # SP mundur, set Address ke data Top
            "D=M",    # D = y (angka pertama yg dipop)
            "A=A-1"   # Address pindah ke x (angka kedua)
            # Sekarang M adalah x, D adalah y. Siap dioperasi (M+D, M-D, dll)
        ]

    # Template: Push nilai D ke Stack
    def push_D_to_stack(self):
        return [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]

    # --- LOGIC WRITERS ---

    def write_arithmetic(self, command):
        code = []
        
        if command == 'add':
            code = self.pop_stack_to_D_and_M()
            code.append("M=M+D") # x + y, hasil disimpan di posisi x (SP-1)
            
        elif command == 'sub': # x - y
            code = self.pop_stack_to_D_and_M()
            code.append("M=M-D") # Hati-hati: M (x) - D (y)
            
        elif command == 'neg': # -y
            code = [
                "@SP",
                "A=M-1", # Akses top stack tanpa mundurin SP
                "M=-M"
            ]
            
        elif command in ['eq', 'gt', 'lt']:
            # Logic Comparison: x - y, lalu cek hasil pake Jump
            label_true = f"TRUE_{self.label_counter}"
            label_end = f"END_{self.label_counter}"
            self.label_counter += 1
            
            jump_type = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}[command]
            
            code = self.pop_stack_to_D_and_M()
            code.extend([
                "D=M-D",        # D = x - y
                f"@{label_true}",
                f"D;{jump_type}", # Kalau kondisi terpenuhi, lompat ke TRUE
                "@SP",
                "A=M-1",
                "M=0",          # False = 0
                f"@{label_end}",
                "0;JMP",
                f"({label_true})",
                "@SP",
                "A=M-1",
                "M=-1",         # True = -1 (0xFFFF)
                f"({label_end})"
            ])
            
        elif command == 'and':
            # TUGAS LU: Isi ini (mirip add, tapi pake &)
             code = self.pop_stack_to_D_and_M()
             code.append("M=M&D")

        elif command == 'or':
            # TUGAS LU: Isi ini (mirip add, tapi pake |)
             code = self.pop_stack_to_D_and_M()
             code.append("M=M|D")

        elif command == 'not':
            # TUGAS LU: Isi ini (mirip neg, tapi pake !)
            code = [
                "@SP",
                "A=M-1",
                "M=!M"
            ]

        return code

    def write_push(self, segment, index):
        code = []
        if segment == 'constant':
            code = [
                f"@{index}",
                "D=A"
            ] + self.push_D_to_stack()
            
        elif segment in ['local', 'argument', 'this', 'that']:
            # Address = RAM[SEGMENT_POINTER] + index
            seg_map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
            code = [
                f"@{seg_map[segment]}",
                "D=M",       # D = Base Address
                f"@{index}",
                "A=D+A",     # A = Base + Index
                "D=M"        # Ambil value dari address target
            ] + self.push_D_to_stack()

        elif segment == 'temp':
            # Address = 5 + index
            code = [
                f"@{5 + index}",
                "D=M"
            ] + self.push_D_to_stack()
            
        elif segment == 'pointer':
            # 0 -> THIS, 1 -> THAT
            pointer_base = "THIS" if index == 0 else "THAT"
            code = [
                f"@{pointer_base}",
                "D=M"
            ] + self.push_D_to_stack()

        elif segment == 'static':
            # Variable: Filename.index
            code = [
                f"@{self.filename}.{index}",
                "D=M"
            ] + self.push_D_to_stack()
            
        return code

    def write_pop(self, segment, index):
        code = []
        # Logic Pop:
        # 1. Hitung target address, simpan di R13 (General Purpose Register)
        # 2. Pop data dari stack ke D
        # 3. Simpan D ke Address yang ditunjuk R13
        
        if segment in ['local', 'argument', 'this', 'that']:
            seg_map = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that': 'THAT'}
            code = [
                f"@{seg_map[segment]}",
                "D=M",
                f"@{index}",
                "D=D+A",   # Hitung target address
                "@R13",
                "M=D"      # Simpan address di R13 sementara
            ] + self.pop_stack_to_D() + [
                "@R13",
                "A=M",     # Ambil address dari R13
                "M=D"      # Taruh data
            ]

        elif segment == 'temp':
             code = self.pop_stack_to_D() + [
                f"@{5 + index}",
                "M=D"
            ]

        elif segment == 'pointer':
            pointer_base = "THIS" if index == 0 else "THAT"
            code = self.pop_stack_to_D() + [
                f"@{pointer_base}",
                "M=D"
            ]

        elif segment == 'static':
            code = self.pop_stack_to_D() + [
                f"@{self.filename}.{index}",
                "M=D"
            ]
            
        return code

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <file.vm>")
    else:
        translator = VMTranslator(sys.argv[1])
        translator.translate()
    