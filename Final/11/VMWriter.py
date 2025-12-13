class VMWriter:
    def __init__(self, output_file):
        self.output = open(output_file, 'w')

    def write_push(self, segment, index):
        # segment: CONSTANT, ARGUMENT, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        # Di Python gw pake lowercase biar gampang: 'constant', 'local', dll
        self.output.write(f"push {segment} {index}\n")

    def write_pop(self, segment, index):
        self.output.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, command):
        # command: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        self.output.write(f"{command.lower()}\n")

    def write_label(self, label):
        self.output.write(f"label {label}\n")

    def write_goto(self, label):
        self.output.write(f"goto {label}\n")

    def write_if(self, label):
        self.output.write(f"if-goto {label}\n")

    def write_call(self, name, n_args):
        self.output.write(f"call {name} {n_args}\n")

    def write_function(self, name, n_locals):
        self.output.write(f"function {name} {n_locals}\n")

    def write_return(self):
        self.output.write("return\n")

    def close(self):
        self.output.close()