import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

class JackAnalyzer:
    def __init__(self, input_path):
        self.input_path = input_path

    def analyze(self):
        files = []
        if os.path.isdir(self.input_path):
            files = [os.path.join(self.input_path, f) for f in os.listdir(self.input_path) if f.endswith(".jack")]
        else:
            files = [self.input_path]

        for file in files:
            self.process_file(file)

    def process_file(self, input_file):
        tokenizer = JackTokenizer(input_file)
        # Output file sekarang .xml (bukan T.xml lagi)
        output_file = input_file.replace('.jack', '.xml') 
        
        print(f"Compiling {input_file} -> {output_file}")
        
        # Panggil CompilationEngine
        engine = CompilationEngine(tokenizer, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py <file.jack or dir>")
    else:
        analyzer = JackAnalyzer(sys.argv[1])
        analyzer.analyze()