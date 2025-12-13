import sys
import os

# --- 1. THE COMPLETE LOOKUP TABLES ---

# Format Comp: a + c1 c2 c3 c4 c5 c6 (Total 7 bits)
# Kalo di instruction ada 'M', bit 'a' (paling depan) pasti 1. Kalo pake 'A', bit 'a' jadi 0.
comp_table = {
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "M":   "1110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "!M":  "1110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "-M":  "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

dest_table = {
    "null": "000",
    "M":    "001",
    "D":    "010",
    "MD":   "011",
    "A":    "100",
    "AM":   "101",
    "AD":   "110",
    "AMD":  "111"
}

jump_table = {
    "null": "000",
    "JGT":  "001",
    "JEQ":  "010",
    "JGE":  "011",
    "JLT":  "100",
    "JNE":  "101",
    "JLE":  "110",
    "JMP":  "111"
}

# Predefined Symbols
symbol_table = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576
}
# Add R0..R15
for i in range(16):
    symbol_table[f"R{i}"] = i

# --- 2. HELPER FUNCTIONS ---

def clean_line(line):
    # Buang comment dan spasi
    # " D=M // comment" -> "D=M"
    return line.split("//")[0].strip()

def get_command_type(line):
    if not line:
        return "EMPTY"
    if line.startswith("@"):
        return "A_COMMAND"
    if line.startswith("("):
        return "L_COMMAND"
    return "C_COMMAND"

# --- 3. MAIN LOGIC (TWO PASS) ---

def assemble(input_file):
    print(f"Processing {input_file}...")
    
    # Baca file
    try:
        with open(input_file, 'r') as f:
            raw_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return

    # PASS 1: Symbol Table Construction
    rom_address = 0
    clean_lines = []
    
    for line in raw_lines:
        line = clean_line(line)
        if not line: continue 
        
        cmd_type = get_command_type(line)
        
        if cmd_type == "L_COMMAND":
            # (LOOP) -> LOOP
            label = line[1:-1]
            # Label merujuk ke instruksi BERIKUTNYA (rom_address saat ini)
            symbol_table[label] = rom_address
        else:
            # Instruction biasa nambah counter
            rom_address += 1
            clean_lines.append(line)

    # PASS 2: Code Generation
    output_filename = input_file.replace('.asm', '.hack')
    # Handle kalo extensionnya bukan .asm (misal input tanpa extension)
    if output_filename == input_file: 
        output_filename += ".hack"
        
    output_lines = []
    ram_address = 16 # User variables start at 16
    
    for line in clean_lines:
        cmd_type = get_command_type(line)
        
        if cmd_type == "A_COMMAND":
            # @xxx
            symbol = line[1:]
            
            val = 0
            if symbol.isdigit():
                val = int(symbol)
            else:
                # Variable handling
                if symbol not in symbol_table:
                    symbol_table[symbol] = ram_address
                    ram_address += 1
                val = symbol_table[symbol]
            
            # 16-bit binary (0vvvvvvvvvvvvvvv)
            binary = f"{val:016b}"
            output_lines.append(binary)
            
        elif cmd_type == "C_COMMAND":
            # dest=comp;jump
            # Parsing logic
            dest = "null"
            comp = ""
            jump = "null"
            
            temp = line
            
            if ';' in temp:
                parts = temp.split(';')
                comp = parts[0]
                jump = parts[1]
                temp = comp # Sisa bagian comp buat di cek '='
            
            if '=' in temp:
                parts = temp.split('=')
                dest = parts[0]
                comp = parts[1]
            else:
                # Kalo ga ada '=', berarti sisanya adalah comp (setelah split ;)
                if ';' not in line: # Kasus comp doang (jarang, tapi mungkin)
                    comp = temp

            # Translation
            try:
                comp_bits = comp_table[comp]
                dest_bits = dest_table[dest]
                jump_bits = jump_table[jump]
                
                # Format C-instruction: 111 a c1-c6 d1-d3 j1-j3
                # comp_bits di atas udah include 'a' (7 bits)
                output_lines.append(f"111{comp_bits}{dest_bits}{jump_bits}")
                
            except KeyError as e:
                print(f"SYNTAX ERROR: Instruction '{line}' contains unknown mnemonic {e}")
                return

    # Write output
    with open(output_filename, 'w') as f:
        for bit_line in output_lines:
            f.write(bit_line + '\n')
            
    print(f"Done! Output saved to: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <file.asm>")
    else:
        # Support processing multiple files at once if needed, but standard is one
        assemble(sys.argv[1])