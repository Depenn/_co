import sys

class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output = open(output_file, 'w')
        self.indent_level = 0
        
        # Mulai proses parsing dari root: Class
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            self.compile_class()
            
        self.output.close()

    # --- HELPER: XML Writing ---
    def write_token(self):
        # Tulis token saat ini (keyword/symbol/identifier/etc) dalam format XML
        tag = self.tokenizer.token_type_xml_tag()
        val = self.tokenizer.current_token_value_xml()
        self.write_line(f"<{tag}> {val} </{tag}>")
        self.tokenizer.advance()

    def write_line(self, line):
        self.output.write(('  ' * self.indent_level) + line + '\n')

    def open_tag(self, tag):
        self.write_line(f"<{tag}>")
        self.indent_level += 1

    def close_tag(self, tag):
        self.indent_level -= 1
        self.write_line(f"</{tag}>")

    # --- GRAMMAR: Program Structure ---

    def compile_class(self):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.open_tag('class')
        
        self.write_token() # class
        self.write_token() # className
        self.write_token() # {
        
        # Handle classVarDec (static/field)
        while self.tokenizer.keyword() in ['static', 'field']:
            self.compile_class_var_dec()
            
        # Handle subroutineDec (constructor/function/method)
        while self.tokenizer.keyword() in ['constructor', 'function', 'method']:
            self.compile_subroutine()
            
        self.write_token() # }
        self.close_tag('class')

    def compile_class_var_dec(self):
        self.open_tag('classVarDec')
        self.write_token() # static/field
        self.write_token() # type
        self.write_token() # varName
        
        while self.tokenizer.symbol() == ',':
            self.write_token() # ,
            self.write_token() # varName
            
        self.write_token() # ;
        self.close_tag('classVarDec')

    def compile_subroutine(self):
        self.open_tag('subroutineDec')
        self.write_token() # constructor/function/method
        self.write_token() # void/type
        self.write_token() # subroutineName
        self.write_token() # (
        self.compile_parameter_list()
        self.write_token() # )
        self.compile_subroutine_body()
        self.close_tag('subroutineDec')

    def compile_parameter_list(self):
        self.open_tag('parameterList')
        # Check if parameter list is not empty (check for type)
        if self.tokenizer.token_type() != 'SYMBOL': 
            self.write_token() # type
            self.write_token() # varName
            while self.tokenizer.symbol() == ',':
                self.write_token() # ,
                self.write_token() # type
                self.write_token() # varName
        self.close_tag('parameterList')

    def compile_subroutine_body(self):
        self.open_tag('subroutineBody')
        self.write_token() # {
        while self.tokenizer.keyword() == 'var':
            self.compile_var_dec()
        self.compile_statements()
        self.write_token() # }
        self.close_tag('subroutineBody')

    def compile_var_dec(self):
        self.open_tag('varDec')
        self.write_token() # var
        self.write_token() # type
        self.write_token() # varName
        while self.tokenizer.symbol() == ',':
            self.write_token() # ,
            self.write_token() # varName
        self.write_token() # ;
        self.close_tag('varDec')

    # --- GRAMMAR: Statements ---

    def compile_statements(self):
        self.open_tag('statements')
        while self.tokenizer.token_type() == 'KEYWORD':
            kw = self.tokenizer.keyword()
            if kw == 'let': self.compile_let()
            elif kw == 'if': self.compile_if()
            elif kw == 'while': self.compile_while()
            elif kw == 'do': self.compile_do()
            elif kw == 'return': self.compile_return()
            else: break
        self.close_tag('statements')

    def compile_let(self):
        self.open_tag('letStatement')
        self.write_token() # let
        self.write_token() # varName
        if self.tokenizer.symbol() == '[':
            self.write_token() # [
            self.compile_expression()
            self.write_token() # ]
        self.write_token() # =
        self.compile_expression()
        self.write_token() # ;
        self.close_tag('letStatement')

    def compile_do(self):
        self.open_tag('doStatement')
        self.write_token() # do
        # Subroutine call is tricky: identifier.identifier(exprList) or identifier(exprList)
        # We handle it by peeking ahead logic or just parsing blindly
        self.write_token() # name (class or var or func)
        if self.tokenizer.symbol() == '.':
            self.write_token() # .
            self.write_token() # subroutineName
            
        self.write_token() # (
        self.compile_expression_list()
        self.write_token() # )
        self.write_token() # ;
        self.close_tag('doStatement')

    def compile_while(self):
        self.open_tag('whileStatement')
        self.write_token() # while
        self.write_token() # (
        self.compile_expression()
        self.write_token() # )
        self.write_token() # {
        self.compile_statements()
        self.write_token() # }
        self.close_tag('whileStatement')

    def compile_return(self):
        self.open_tag('returnStatement')
        self.write_token() # return
        if self.tokenizer.symbol() != ';':
            self.compile_expression()
        self.write_token() # ;
        self.close_tag('returnStatement')

    def compile_if(self):
        self.open_tag('ifStatement')
        self.write_token() # if
        self.write_token() # (
        self.compile_expression()
        self.write_token() # )
        self.write_token() # {
        self.compile_statements()
        self.write_token() # }
        if self.tokenizer.keyword() == 'else':
            self.write_token() # else
            self.write_token() # {
            self.compile_statements()
            self.write_token() # }
        self.close_tag('ifStatement')

    # --- GRAMMAR: Expressions (The Hard Part) ---

    def compile_expression(self):
        self.open_tag('expression')
        self.compile_term()
        # (op term)*
        while self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=', '&lt;', '&gt;', '&amp;']:
            self.write_token() # op
            self.compile_term()
        self.close_tag('expression')

    def compile_term(self):
        self.open_tag('term')
        tt = self.tokenizer.token_type()
        
        if tt == 'INT_CONST' or tt == 'STRING_CONST' or tt == 'KEYWORD':
            self.write_token()
        elif tt == 'IDENTIFIER':
            # Check lookahead for array [ or subroutine ( or .
            # But wait, JackTokenizer in this speedrun doesn't peek. 
            # Simplified Logic:
            self.write_token() # varName / className
            sym = self.tokenizer.symbol()
            if sym == '[':
                self.write_token() # [
                self.compile_expression()
                self.write_token() # ]
            elif sym == '(' or sym == '.':
                # Subroutine call
                if sym == '.':
                    self.write_token() # .
                    self.write_token() # subroutineName
                self.write_token() # (
                self.compile_expression_list()
                self.write_token() # )
        elif self.tokenizer.symbol() == '(':
            self.write_token() # (
            self.compile_expression()
            self.write_token() # )
        elif self.tokenizer.symbol() in ['-', '~']:
            self.write_token() # unaryOp
            self.compile_term()
            
        self.close_tag('term')

    def compile_expression_list(self):
        self.open_tag('expressionList')
        if self.tokenizer.symbol() != ')':
            self.compile_expression()
            while self.tokenizer.symbol() == ',':
                self.write_token() # ,
                self.compile_expression()
        self.close_tag('expressionList')