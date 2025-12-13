from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.vm_writer = VMWriter(output_file)
        self.symbol_table = SymbolTable()
        self.class_name = ""
        self.label_counter = 0
        
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            self.compile_class()
            
        self.vm_writer.close()

    def eat(self, token_text=None):
        self.tokenizer.advance()

    # --- STRUCTURE ---

    def compile_class(self):
        self.eat() # class
        self.class_name = self.tokenizer.identifier()
        self.eat() # className
        self.eat() # {
        while self.tokenizer.keyword() in ['static', 'field']:
            self.compile_class_var_dec()
        while self.tokenizer.keyword() in ['constructor', 'function', 'method']:
            self.compile_subroutine()
        self.eat() # }

    def compile_class_var_dec(self):
        kind = self.tokenizer.keyword()
        self.eat()
        type = self.tokenizer.keyword() if self.tokenizer.token_type() == 'KEYWORD' else self.tokenizer.identifier()
        self.eat()
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type, kind)
        self.eat()
        while self.tokenizer.symbol() == ',':
            self.eat()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, kind)
            self.eat()
        self.eat() # ;

    def compile_subroutine(self):
        self.symbol_table.start_subroutine()
        sub_kind = self.tokenizer.keyword()
        self.eat()
        self.eat() # return type
        sub_name = self.tokenizer.identifier()
        self.eat()
        if sub_kind == 'method':
            self.symbol_table.define('this', self.class_name, 'arg')
        self.eat() # (
        self.compile_parameter_list()
        self.eat() # )
        self.compile_subroutine_body(sub_name, sub_kind)

    def compile_parameter_list(self):
        if self.tokenizer.symbol() != ')':
            type = self.tokenizer.keyword() if self.tokenizer.token_type() == 'KEYWORD' else self.tokenizer.identifier()
            self.eat()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, 'arg')
            self.eat()
            while self.tokenizer.symbol() == ',':
                self.eat()
                type = self.tokenizer.keyword() if self.tokenizer.token_type() == 'KEYWORD' else self.tokenizer.identifier()
                self.eat()
                name = self.tokenizer.identifier()
                self.symbol_table.define(name, type, 'arg')
                self.eat()

    def compile_subroutine_body(self, name, kind):
        self.eat() # {
        while self.tokenizer.keyword() == 'var':
            self.compile_var_dec()
        
        n_vars = self.symbol_table.var_count('var')
        self.vm_writer.write_function(f"{self.class_name}.{name}", n_vars)
        
        if kind == 'constructor':
            n_fields = self.symbol_table.var_count('field')
            self.vm_writer.write_push('constant', n_fields)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        elif kind == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)
            
        self.compile_statements()
        self.eat() # }

    def compile_var_dec(self):
        self.eat() # var
        type = self.tokenizer.keyword() if self.tokenizer.token_type() == 'KEYWORD' else self.tokenizer.identifier()
        self.eat()
        name = self.tokenizer.identifier()
        self.symbol_table.define(name, type, 'var')
        self.eat()
        while self.tokenizer.symbol() == ',':
            self.eat()
            name = self.tokenizer.identifier()
            self.symbol_table.define(name, type, 'var')
            self.eat()
        self.eat() # ;

    # --- STATEMENTS ---

    def compile_statements(self):
        while self.tokenizer.token_type() == 'KEYWORD':
            kw = self.tokenizer.keyword()
            if kw == 'let': self.compile_let()
            elif kw == 'if': self.compile_if()
            elif kw == 'while': self.compile_while()
            elif kw == 'do': self.compile_do()
            elif kw == 'return': self.compile_return()
            else: break

    def compile_do(self):
        self.eat() # do
        name = self.tokenizer.identifier()
        self.eat()
        self._compile_subroutine_call(name)
        self.eat() # ;
        self.vm_writer.write_pop('temp', 0)

    def compile_let(self):
        self.eat() # let
        name = self.tokenizer.identifier()
        self.eat()
        is_array = False
        if self.tokenizer.symbol() == '[':
            is_array = True
            self.eat()
            kind = self.symbol_table.kind_of(name)
            idx = self.symbol_table.index_of(name)
            self.vm_writer.write_push(self._kind_to_segment(kind), idx)
            self.compile_expression()
            self.eat() # ]
            self.vm_writer.write_arithmetic('ADD')
        self.eat() # =
        self.compile_expression()
        self.eat() # ;
        if is_array:
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        else:
            kind = self.symbol_table.kind_of(name)
            idx = self.symbol_table.index_of(name)
            self.vm_writer.write_pop(self._kind_to_segment(kind), idx)

    def compile_while(self):
        l1 = f"WHILE_EXP{self.label_counter}"; l2 = f"WHILE_END{self.label_counter}"
        self.label_counter += 1
        self.vm_writer.write_label(l1)
        self.eat(); self.eat() # while (
        self.compile_expression()
        self.eat() # )
        self.vm_writer.write_arithmetic('NOT')
        self.vm_writer.write_if(l2)
        self.eat() # {
        self.compile_statements()
        self.eat() # }
        self.vm_writer.write_goto(l1)
        self.vm_writer.write_label(l2)

    def compile_return(self):
        self.eat() # return
        if self.tokenizer.symbol() != ';':
            self.compile_expression()
        else:
            self.vm_writer.write_push('constant', 0)
        self.eat() # ;
        self.vm_writer.write_return()

    def compile_if(self):
        l1 = f"IF_TRUE{self.label_counter}"; l2 = f"IF_FALSE{self.label_counter}"; l3 = f"IF_END{self.label_counter}"
        self.label_counter += 1
        self.eat(); self.eat() # if (
        self.compile_expression()
        self.eat() # )
        self.vm_writer.write_arithmetic('NOT')
        self.vm_writer.write_if(l2)
        self.eat() # {
        self.compile_statements()
        self.eat() # }
        self.vm_writer.write_goto(l3)
        self.vm_writer.write_label(l2)
        if self.tokenizer.keyword() == 'else':
            self.eat(); self.eat()
            self.compile_statements()
            self.eat()
        self.vm_writer.write_label(l3)

    # --- EXPRESSIONS ---

    def compile_expression(self):
        self.compile_term()
        while self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op = self.tokenizer.symbol()
            self.eat()
            self.compile_term()
            if op == '+': self.vm_writer.write_arithmetic('ADD')
            elif op == '-': self.vm_writer.write_arithmetic('SUB')
            elif op == '*': self.vm_writer.write_call('Math.multiply', 2)
            elif op == '/': self.vm_writer.write_call('Math.divide', 2)
            elif op == '&': self.vm_writer.write_arithmetic('AND')
            elif op == '|': self.vm_writer.write_arithmetic('OR')
            elif op == '<': self.vm_writer.write_arithmetic('LT')
            elif op == '>': self.vm_writer.write_arithmetic('GT')
            elif op == '=': self.vm_writer.write_arithmetic('EQ')

    def compile_term(self):
        tt = self.tokenizer.token_type()
        if tt == 'INT_CONST':
            self.vm_writer.write_push('constant', self.tokenizer.int_val())
            self.eat()
        elif tt == 'STRING_CONST':
            s = self.tokenizer.string_val()
            self.vm_writer.write_push('constant', len(s))
            self.vm_writer.write_call('String.new', 1)
            for c in s:
                self.vm_writer.write_push('constant', ord(c))
                self.vm_writer.write_call('String.appendChar', 2)
            self.eat()
        elif tt == 'KEYWORD':
            k = self.tokenizer.keyword()
            if k == 'true': 
                self.vm_writer.write_push('constant', 0)
                self.vm_writer.write_arithmetic('NOT')
            elif k in ['false', 'null']: self.vm_writer.write_push('constant', 0)
            elif k == 'this': self.vm_writer.write_push('pointer', 0)
            self.eat()
        elif tt == 'IDENTIFIER':
            name = self.tokenizer.identifier(); self.eat()
            sym = self.tokenizer.symbol()
            if sym == '[':
                self.eat()
                kind = self.symbol_table.kind_of(name)
                idx = self.symbol_table.index_of(name)
                self.vm_writer.write_push(self._kind_to_segment(kind), idx)
                self.compile_expression()
                self.eat() # ]
                self.vm_writer.write_arithmetic('ADD')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)
            elif sym in ['(', '.']:
                self._compile_subroutine_call(name)
            else:
                kind = self.symbol_table.kind_of(name)
                idx = self.symbol_table.index_of(name)
                self.vm_writer.write_push(self._kind_to_segment(kind), idx)
        elif self.tokenizer.symbol() == '(':
            self.eat(); self.compile_expression(); self.eat()
        elif self.tokenizer.symbol() in ['-', '~']:
            op = self.tokenizer.symbol(); self.eat(); self.compile_term()
            if op == '-': self.vm_writer.write_arithmetic('NEG')
            else: self.vm_writer.write_arithmetic('NOT')

    def compile_expression_list(self):
        n = 0
        if self.tokenizer.symbol() != ')':
            self.compile_expression(); n+=1
            while self.tokenizer.symbol() == ',':
                self.eat(); self.compile_expression(); n+=1
        return n

    def _compile_subroutine_call(self, name):
        n_args = 0
        full_name = ""
        if self.tokenizer.symbol() == '.':
            self.eat()
            sub = self.tokenizer.identifier(); self.eat()
            type = self.symbol_table.type_of(name)
            if type is None:
                full_name = f"{name}.{sub}"
            else:
                kind = self.symbol_table.kind_of(name)
                idx = self.symbol_table.index_of(name)
                self.vm_writer.write_push(self._kind_to_segment(kind), idx)
                full_name = f"{type}.{sub}"
                n_args = 1
        else:
            self.vm_writer.write_push('pointer', 0)
            full_name = f"{self.class_name}.{name}"
            n_args = 1
        self.eat() # (
        n_args += self.compile_expression_list()
        self.eat() # )
        self.vm_writer.write_call(full_name, n_args)

    def _kind_to_segment(self, kind):
        return {'var':'local', 'arg':'argument', 'field':'this', 'static':'static'}.get(kind, 'error')