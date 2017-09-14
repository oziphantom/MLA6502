from tassLineGroup import TassLineGroupType
from tassLineGroup import TassLineGroup
from tassDefineLine import TassDefineLine
from tassIFBlockResolver import TassIFBlockResolver
from pyLog import pylog
import midLevelAssem
import assemNumHelper

class TassDefineManager:
    def __init__(self):
        self.variables = {}
        self.python_variables = {}

    def recurse_tree_and_add_strings(self,parent,out_lines):
        for item in parent:
            if isinstance(item,TassLineGroup): # a full child type
                if (item.type == TassLineGroupType.preprocessor_assign or
                    item.type == TassLineGroupType.assign):
                    self.recurse_tree_and_add_strings(item,out_lines)
                else:
                    self.recurse_tree_for_assigns(item,out_lines)
            else: #string we want
                out_lines.append([item,False,False])

    def recurse_tree_for_assigns(self,parent,out_lines):
        for item in parent:
            if isinstance(item,TassLineGroup):
                if (item.type == TassLineGroupType.preprocessor_assign or
                    item.type == TassLineGroupType.assign):
                    self.recurse_tree_and_add_strings(item,out_lines)                            
                else:
                    self.recurse_tree_for_assigns(item,out_lines)

    def parse_from_classified_lines(self, tass_define_lines):
        curr_pass = 0
        while True:
            lookedAt = 0
            evaulated = 0
            for key in tass_define_lines:
                if key == "kBird.spawnY":
                    print("test")
                entry = tass_define_lines[key]
                if (not entry.resoved) and ( not entry.cant_be_resolved):
                    lookedAt = lookedAt + 1
                    line = entry.full_string
                    parts = entry.get_sub_labels_from_RHS()
                    var = entry.name
                    python_var = var.replace(".", "_")
                    value = entry.RHS.strip()
                    valueInt = 0
                    valueString = ""
                    isString = False
                    found = False
                    if not assemNumHelper.is_equation(value):
                        if assemNumHelper.is_hex(value):
                            valueInt = assemNumHelper.get_int_from_hex(value)
                            found = True
                        elif assemNumHelper.is_binary(value):
                            valueInt = assemNumHelper.get_int_from_binary(value)
                            found = True
                        elif value.isnumeric():
                            valueInt = int(value, 10)
                            found = True
                        elif value.lower() in self.variables:
                            valueInt = self.variables[value.lower()]
                            found = True
                        elif '"' in value:
                            isString = True
                            valueString = value
                            found = True
                    else:
                        try:                            
                            value = assemNumHelper.convert_equation_to_python(value).lower()
                            if '"' not in value:
                                valueInt = eval(value, self.python_variables)
                            else:
                                valueString = eval(value, self.python_variables)
                                isString = True
                            found = True
                        except Exception as e:
                            pass

                    if found:
                        lvar = var.lower()
                        lpvar = python_var.lower()
                        if isString:
                            self.variables[lvar] = valueString
                            self.python_variables[lpvar] = valueString
                        else:
                            self.variables[lvar] = valueInt
                            self.python_variables[lpvar] = valueInt
                        entry.resoved = True
                        entry.int_value = valueInt
                        entry.is_string = isString
                        entry.string_value = valueString
                        evaulated = evaulated + 1
            if lookedAt == 0:
                break #our job is done

            #pylog.write_log("Pass :"+str(curr_pass))
            curr_pass = curr_pass + 1
            #self.variables.pop('__builtins__')
            #pylog.write_dic(self.variables)

            if evaulated == 0:
            #    print("error unable to evaluate all pre processor variables")
                break

    def parse_from_tass_args_file(self, filename):
        ret = {}
        with open(filename,"r") as args:
            for line in args.readlines():
                if line.startswith("-D"):
                    define = line[3:].strip()
                    define = define.replace('\\"', '"') #un escape the "
                    TDL = TassDefineLine()
                    TDL.set_line(define)
                    ret[TDL.name] = TDL
        return ret

    def do_repalcements_in(self,replacements,parent):
        for block in replacements:
            replace = replacements[block]
            idx = parent.index(block)
            if len(replace) > 0:
                new_group = TassLineGroup()
                if isinstance(replace[0], str):
                    new_group.type = TassLineGroupType.not_special
                else:
                    new_group.type = replace[0].type
                new_group.children = replace
                parent[idx] = new_group
            else:
                del parent[idx]
    
    def resolve_if_blocks(self, classified_lines):
        replacements = {}
        counter = 0
        ifbr = TassIFBlockResolver()
        for block in classified_lines:
            if block.type == TassLineGroupType.if_block:
                out = ifbr.resolveIFBlock(block, self.python_variables)
                replacements[block] = out
            elif TassLineGroup.get_does_type_make_sub_blocks(block.type):
                if block.should_evaluate_if():
                    if not block.is_child_string(0):
                        counter += self.resolve_if_blocks(block.children)
        counter += len(replacements)
        self.do_repalcements_in(replacements, classified_lines)
        return counter

    def resolve_mid_level_blocks(self,parent,segmentDM):
        replacements = {}
        counter = 0
        for block in parent:
            if block.type == TassLineGroupType.midlevel:
                #get the strings out of this block
                strings = block.get_all_child_strings()
                #mid level parse it
                out = midLevelAssem.convert_lines_to_asm(strings,segmentDM,self)
                pylog.write_log("<code><table><tr><td>")
                for s in strings:
                    pylog.write_log(s)
                pylog.write_log("</td><td>")
                for l in out:
                    pylog.write_log(l)
                pylog.write_log("</td></tr></table></code>")
                #replace it
                replacements[block] = out
            elif TassLineGroup.get_does_type_make_sub_blocks(block.type):
                if not block.is_child_string(0):
                    counter += self.resolve_mid_level_blocks(block.children,segmentDM)
        counter += len(replacements)
        self.do_repalcements_in(replacements, parent)
        return counter

    def lookupValueFor(self,value):
        found = False
        original = value

        if value.startswith("#"):
            value = value[1:] #remove the #
            
        if assemNumHelper.is_hex(value):
            value = assemNumHelper.get_int_from_hex(value)
            found = True
        elif assemNumHelper.is_binary(value):
            value = assemNumHelper.get_int_from_binary(value)
            found = True
        elif value.isnumeric():
            value = int(value, 10)
            found = True
        elif value.lower() in self.variables:
            value = self.variables[value.lower()]
            found = True
        if found:
            pylog.write_log(original+" was subsituted with "+str(value))
            return value
        pylog.write_log(original+" not found")
        return original