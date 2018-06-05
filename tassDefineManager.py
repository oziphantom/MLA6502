from tassLineGroup import TassLineGroupType
from tassLineGroup import TassLineGroup
from tassDefineLine import TassDefineLine
from tassIFBlockResolver import TassIFBlockResolver
from pyLog import pylog
import midLevelAssem
from assemNumHelper import AssemNumHelper


class TassDefineManager:
    def __init__(self):
        self.variables = {}
        self.python_variables = {}

    def recurse_tree_and_add_strings(self, parent, out_lines):
        for item in parent:
            if isinstance(item, TassLineGroup):  # a full child type
                if (item.type == TassLineGroupType.preprocessor_assign or
                   item.type == TassLineGroupType.assign):
                    self.recurse_tree_and_add_strings(item, out_lines)
                else:
                    self.recurse_tree_for_assigns(item, out_lines)
            else:  # string we want
                out_lines.append([item, False, False])

    def recurse_tree_for_assigns(self, parent, out_lines):
        for item in parent:
            if isinstance(item, TassLineGroup):
                if (item.type == TassLineGroupType.preprocessor_assign or
                   item.type == TassLineGroupType.assign):
                    self.recurse_tree_and_add_strings(item, out_lines)
                else:
                    self.recurse_tree_for_assigns(item, out_lines)

    def parse_from_classified_lines(self, tass_define_lines):
        curr_pass = 0
        while True:
            looked_at = 0
            evaluated = 0
            for key in tass_define_lines:
                entry = tass_define_lines[key]
                if (not entry.resolved) and (not entry.cant_be_resolved):
                    looked_at = looked_at + 1
                    # line = entry.full_string
                    # parts = entry.get_sub_labels_from_RHS()
                    var = entry.name
                    python_var = var.replace(".", "_")
                    value = entry.RHS.strip()
                    value_int = 0
                    value_string = ""
                    is_string = False
                    found = False
                    if not AssemNumHelper.is_equation(value):
                        if AssemNumHelper.is_hex(value):
                            value_int = AssemNumHelper.get_int_from_hex(value)
                            found = True
                        elif AssemNumHelper.is_binary(value):
                            value_int = AssemNumHelper.get_int_from_binary(value)
                            found = True
                        elif value.isnumeric():
                            value_int = int(value, 10)
                            found = True
                        elif value.lower() in self.variables:
                            value_int = self.variables[value.lower()]
                            found = True
                        elif '"' in value:
                            is_string = True
                            value_string = value
                            found = True
                    else:
                        try:                            
                            value = AssemNumHelper.convert_equation_to_python(value).lower()
                            if '"' not in value:
                                value_int = eval(value, self.python_variables)
                            else:
                                value_string = eval(value, self.python_variables)
                                is_string = True
                            found = True
                        except Exception as e:
                            pass

                    if found:
                        lvar = var.lower()
                        lpvar = python_var.lower()
                        if is_string:
                            self.variables[lvar] = value_string
                            self.python_variables[lpvar] = value_string
                        else:
                            self.variables[lvar] = value_int
                            self.python_variables[lpvar] = value_int
                        entry.resolved = True
                        entry.int_value = value_int
                        entry.is_string = is_string
                        entry.string_value = value_string
                        evaluated = evaluated + 1
            if looked_at == 0:
                break  # our job is done

            # pylog.write_log("Pass :"+str(curr_pass))
            curr_pass = curr_pass + 1
            # pylog.write_dic(self.variables)

            if evaluated == 0:
                # print("error unable to evaluate all pre processor variables")
                break

    @staticmethod
    def parse_from_tass_args_file(filename):
        ret = {}
        with open(filename, "r") as args:
            for line in args.readlines():
                if line.startswith("-D"):
                    define = line[3:].strip()
                    define = define.replace('\\"', '"')  # un escape the "
                    tdl = TassDefineLine()
                    tdl.set_line(define)
                    ret[tdl.name] = tdl
        return ret

    @staticmethod
    def do_replacements_in(replacements, parent):
        pylog.write_log("doing replacements")
        for block in replacements:
            pylog.write_block_string(block)
            replace = replacements[block]
            idx = parent.index(block)
            if len(replace) > 0:
                if isinstance(replace[0], str):
                    new_group = TassLineGroup()
                    for item in replace:
                        new_group.add_child(item)
                    pylog.write_log("found string")
                    new_group.type = TassLineGroup.identify_line(replace[0])
                    pylog.write_log("identified as " + str(new_group.type))
                    replace = new_group
                # else:
                #     pylog.write_log("this is a group of type " + str(replace[0].type))
                #     new_group.type = replace[0].type
                #new_group.children = replace
                #parent[idx] = new_group
                parent[idx:idx+1] = replace
                # pylog.write_log("replacing with")
                # pylog.write_block_string(replace)
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
        if len(replacements) > 0:
            self.do_replacements_in(replacements, classified_lines)
        return counter

    def resolve_mid_level_blocks(self, parent, segment_dm):
        replacements = {}
        counter = 0
        for block in parent:
            if not isinstance(block, str):
                if block.type == TassLineGroupType.midlevel:
                    # get the strings out of this block
                    strings = block.get_all_child_strings()
                    # mid level parse it
                    out = midLevelAssem.convert_lines_to_asm(strings, segment_dm, self)
                    pylog.write_log("<code><table><tr><td>")
                    for s in strings:
                        pylog.write_log(s)
                    pylog.write_log("</td><td>")
                    group = ""
                    if isinstance(out, str):
                        pylog.write_log(l)
                    else:
                        for l in out:
                            if len(l) == 1:
                                group += l
                            else:
                                pylog.write_log(l)
                        if len(group):
                            pylog.write_log(group)
                    pylog.write_log("</td></tr></table></code>")
                    # replace it
                    replacements[block] = out
                elif TassLineGroup.get_does_type_make_sub_blocks(block.type):
                    if not block.is_child_string(0):
                        counter += self.resolve_mid_level_blocks(block.children, segment_dm)
        counter += len(replacements)
        self.do_replacements_in(replacements, parent)
        return counter

    def lookup_value_for(self, value):
        found = False
        original = value
        value = value.strip()
        extra = ""

        if value.startswith("#"):
            value = value[1:]  # remove the #
        if "," in value:
            splits = value.split(",")
            value = splits[0]
            for ex in splits[1:]:
                extra += ","+ex

        if AssemNumHelper.is_equation(value):
            try:
                value = AssemNumHelper.convert_equation_to_python(value)
                value = eval(value, self.python_variables)
                found = True
            except:
                found = False
        elif AssemNumHelper.is_hex(value):
            value = AssemNumHelper.get_int_from_hex(value)
            found = True
        elif AssemNumHelper.is_binary(value):
            value = AssemNumHelper.get_int_from_binary(value)
            found = True
        elif value.isnumeric():
            value = int(value, 10)
            found = True
        elif value.lower() in self.variables:
            value = self.variables[value.lower()]
            found = True
        if found:
            pylog.write_log(original+" was substituted with "+str(value)+extra)
            if len(extra):
                return str(value)+extra
            return value
        pylog.write_log(original+" not found")
        return original
