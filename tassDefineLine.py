from tassScopeIterator import TassScopeIterator
from pyLog import pylog
import assemNumHelper
import re

class TassDefineLine:
    def __init__(self):
        self.full_string = ""
        self.name = ""
        self.RHS = ""
        self.int_value = assemNumHelper.AssemNumHelper.get_invalid_value()
        self.fully_expanded = False
        self.resolved = False
        self.cant_be_resolved = False
        self.prefix = ""
        self.is_string = False
        self.string_value = ""

    def set_line(self, line):
        self.full_string = line
        parts = re.split('=', line.strip())
        self.name = parts[0].strip()
        localRHS = parts[1].strip()
        if ';' in localRHS:
            idx = localRHS.find(";")
            localRHS = localRHS[0:idx]
        self.RHS = localRHS

    def attach_prefix(self, prefix):
        if len(prefix) > 0:
            self.prefix = prefix
            self.name = prefix + "." + self.name

    def get_sub_labels_from_RHS(self):
        parts = re.split('[=,+,\-,*,(,),#,<,>,&,|,/, ]', self.RHS)
        ret = []
        for part in parts:
            stripped = part.strip()
            if not( stripped.startswith('"') and stripped.endswith('"')):
                if self._is_part_label(part):
                    ret.append(part)
        return ret

    def add_prefix_to_sub_label(self,label,prefix):
        start = 0
        while True:
            index = self.RHS.find(label, start)
            if index == -1:
                break
            start = start + len(label)
            if index > 0:
                if self.RHS[index-1] == '.':
                    break
            self.RHS = self.RHS[0:index]+prefix+"."+self.RHS[index:]

    def resolve_all_sub_names(self, all_know_vars_dictionary):
        subs = self.get_sub_labels_from_RHS()
        done = {}
        found_them_all = True
        for sub in subs:
            TSI = TassScopeIterator(self.prefix)
            found = False
            for scope in TSI:
                if len(scope) > 0:
                    extend = scope + "." + sub
                else:
                    extend = sub

                if extend in all_know_vars_dictionary:
                    if len(scope) > 0:
                        done[sub] = scope
                    found = True
                    break
            if not found:
                pylog.write_log("could not resolve "+ sub +" from "+ self.full_string.strip())
                found_them_all = False
        if not found_them_all:
            self.fully_expanded = False
            self.cant_be_resolved = True
        else:
            self.fully_expanded = True

        for key in done:
            self.add_prefix_to_sub_label(key, done[key])

    def _is_part_label(self, part):
        s = part.strip()
        if ((len(s) > 0) and
                ('$' not in s) and
                ('%' not in s) and
                (not s.isnumeric())
           ):
            return True
        return False
            