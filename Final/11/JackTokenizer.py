import re

class JackTokenizer:
    # Regex Patterns for Jack Language
    # Tambahkan \b di awal dan akhir grup keyword
    # Gunakan raw string r'' biar backslash aman
    KEYWORD = r'(?P<KEYWORD>\b(?:class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)\b)'
    SYMBOL = '(?P<SYMBOL>[\\{\\}\\(\\)\\[\\]\\.\\,\\;\\+\\-\\*\\/\\&\\|\\<\\>\\=\\~])'
    INT_CONST = '(?P<INT_CONST>\\d+)'
    STRING_CONST = '(?P<STRING_CONST>\\"[^\\n\\"]*\\")'
    IDENTIFIER = '(?P<IDENTIFIER>[a-zA-Z_]\\w*)'
    
    # Master Regex: Gabungin semua pattern jadi satu
    TOKEN_REGEX = f'{KEYWORD}|{SYMBOL}|{INT_CONST}|{STRING_CONST}|{IDENTIFIER}'

    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            self.content = f.read()
        
        self.tokens = self._tokenize(self.content)
        self.cursor = 0
        self.current_token = None

    def _tokenize(self, text):
        # 1. Hapus Comments
        # Hapus /* ... */ (multiline)
        text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.DOTALL)
        # Hapus // ... (single line)
        text = re.sub(r'//.*', ' ', text)
        
        # 2. Find all tokens
        tokens = []
        for match in re.finditer(self.TOKEN_REGEX, text):
            # match.lastgroup ngasih tau tipe token (KEYWORD, SYMBOL, dll)
            # match.group() ngasih tau isi textnya
            token_type = match.lastgroup
            token_value = match.group()
            
            if token_type == 'STRING_CONST':
                token_value = token_value[1:-1] # Buang kutip " di awal dan akhir
                
            tokens.append((token_type, token_value))
            
        return tokens

    def has_more_tokens(self):
        return self.cursor < len(self.tokens)

    def advance(self):
        if self.has_more_tokens():
            self.current_token = self.tokens[self.cursor]
            self.cursor += 1

    def token_type(self):
        return self.current_token[0]

    def keyword(self):
        return self.current_token[1]

    def symbol(self):
        return self.current_token[1]

    def identifier(self):
        return self.current_token[1]

    def int_val(self):
        return self.current_token[1]

    def string_val(self):
        return self.current_token[1]
    
    def token_type_xml_tag(self):
        # Mapping tipe regex ke tag XML
        tag_map = {
            'KEYWORD': 'keyword',
            'SYMBOL': 'symbol',
            'IDENTIFIER': 'identifier',
            'INT_CONST': 'integerConstant',
            'STRING_CONST': 'stringConstant'
        }
        return tag_map[self.token_type()]

    def current_token_value_xml(self):
        t_type = self.token_type()
        if t_type == 'KEYWORD': return self.keyword()
        if t_type == 'SYMBOL': return self.symbol()
        if t_type == 'IDENTIFIER': return self.identifier()
        if t_type == 'INT_CONST': return self.int_val()
        if t_type == 'STRING_CONST': return self.string_val()
        return ""