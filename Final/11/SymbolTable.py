class SymbolTable:
    def __init__(self):
        self.class_table = {}      # scope: static, field
        self.subroutine_table = {} # scope: arg, var
        self.counts = {
            'static': 0,
            'field': 0,
            'arg': 0,
            'var': 0
        }

    def start_subroutine(self):
        """Resets the subroutine table for a new method/function."""
        self.subroutine_table = {}
        self.counts['arg'] = 0
        self.counts['var'] = 0

    def define(self, name, type, kind):
        """
        Defines a new identifier of a given name, type, and kind.
        kind: STATIC, FIELD, ARG, or VAR
        """
        # Tentukan mau masuk scope mana
        if kind in ['static', 'field']:
            index = self.counts[kind]
            self.class_table[name] = (type, kind, index)
            self.counts[kind] += 1
        elif kind in ['arg', 'var']:
            index = self.counts[kind]
            self.subroutine_table[name] = (type, kind, index)
            self.counts[kind] += 1

    def var_count(self, kind):
        """Returns the number of variables of the given kind already defined in the current scope."""
        return self.counts.get(kind, 0)

    def kind_of(self, name):
        """
        Returns the kind of the named identifier (STATIC, FIELD, ARG, VAR, or NONE).
        Cek local scope dulu, baru class scope.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name][1]
        elif name in self.class_table:
            return self.class_table[name][1]
        return None

    def type_of(self, name):
        """Returns the type of the named identifier."""
        if name in self.subroutine_table:
            return self.subroutine_table[name][0]
        elif name in self.class_table:
            return self.class_table[name][0]
        return None

    def index_of(self, name):
        """Returns the index assigned to the named identifier."""
        if name in self.subroutine_table:
            return self.subroutine_table[name][2]
        elif name in self.class_table:
            return self.class_table[name][2]
        return None