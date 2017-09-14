
class TassScopeIterator:
    def __init__(self, scope):
        self.scope = scope
        self.intermit = self.scope

    def __iter__(self):
        return self

    def __next__(self):
        ret = self.intermit
        if self.intermit != None:
            if "." in self.intermit:
                last = self.intermit.rfind('.')
                stripped = self.intermit[0:last]
                self.intermit = stripped
            elif len(self.intermit) == 0:
                self.intermit = None
            else:
                self.intermit = ""

        if ret != None:
            return ret
        raise StopIteration

       