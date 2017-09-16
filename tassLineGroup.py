from enum import Enum
import re

class TassLineGroupType(Enum):
    not_special = 0
    weak = 1
    if_block = 2
    block = 3
    comment = 4
    struct = 5
    section = 6
    macro = 7
    segment = 8
    union = 9
    include = 10
    binary = 11
    midlevel = 12
    root = 13
    end_if = 14
    end_block = 15
    end_comment = 16
    end_struct = 17
    end_macro = 18
    end_union = 19
    end_section = 20
    end_weak = 21
    preprocessor_assign = 22
    assign = 23
    if_else = 24
    just_else = 25
    function = 26
    end_function = 27

                #string, id, start(0) or contains(1),not sub(0) makes sub(1)
g_lineIDstrings = [[".weak", TassLineGroupType.weak, 0, 1],
                   [".if", TassLineGroupType.if_block, 0, 1],
                   [".block", TassLineGroupType.block, 1, 1],
                   [".comment", TassLineGroupType.comment, 0, 0],
                   [".struct", TassLineGroupType.struct, 1, 1],
                   [".section", TassLineGroupType.section, 1, 1],
                   [".macro", TassLineGroupType.macro, 1, 1],
                   [".segment", TassLineGroupType.segment, 1, 1],
                   [".union", TassLineGroupType.union, 1, 1],
                   [".include", TassLineGroupType.include, 0, 0],
                   [".binary", TassLineGroupType.binary, 1, 0],
                   ["!", TassLineGroupType.midlevel, 0, 0],
                   ["!!", TassLineGroupType.midlevel, 0, 0],
                   [".bend", TassLineGroupType.end_block, 0, 0],
                   [".endc", TassLineGroupType.end_comment, 0, 0],
                   [".ends", TassLineGroupType.end_struct, 0, 0],
                   [".endm", TassLineGroupType.end_macro, 0, 0],
                   [".endu", TassLineGroupType.end_union, 0, 0],
                   [".send", TassLineGroupType.end_section, 0, 0],
                   [".endweak", TassLineGroupType.end_weak, 0, 0],
                   [".endif", TassLineGroupType.end_if, 0, 0],
                   [".fi", TassLineGroupType.end_if, 0, 0],
                   [".else", TassLineGroupType.just_else, 0, 0],
                   [".elsif", TassLineGroupType.if_else, 0, 0],
                   [".function", TassLineGroupType.function, 1, 1],
                   [".endf", TassLineGroupType.end_function, 0, 0]
                  ]

g_no_runs = [TassLineGroupType.if_block, TassLineGroupType.block, TassLineGroupType.struct, 
             TassLineGroupType.section, TassLineGroupType.include, TassLineGroupType.binary,
             TassLineGroupType.end_block, TassLineGroupType.end_comment, TassLineGroupType.end_struct,
             TassLineGroupType.end_macro, TassLineGroupType.end_union, TassLineGroupType.end_section,
             TassLineGroupType.end_weak, TassLineGroupType.end_if]

g_regex_Preprocess_assign = re.compile(r"^\s*[A-Z0-9_]+[\s]*={1}[\s]*[$%]{0,1}[a-zA-Z0-9\"]+")
g_regex_assign = re.compile(r"^\s*[a-zA-Z0-9_]+[\s]*={1}[\s]*[$%]{0,1}[a-zA-Z0-9_\"]+")
g_dont_expand_if = [TassLineGroupType.macro, TassLineGroupType.segment, TassLineGroupType.function]

class TassLineGroup(object):
    def __init__(self):
        self.type = TassLineGroupType.not_special
        self.children = []
        self.fully_colapsed = False

    def __iter__(self):
        return iter(self.children)

    def __next__(self):
        return next(self.children)

    def add_child(self, child):
        self.children.append(child)

    def is_child_string(self, x):
        return isinstance(self.children[x], str)

    def get_all_child_strings(self):
        strings = []
        for c in self.children:
            if isinstance(c, str):
                # Handle both !! and ! at the start of the line
                if c.strip().startswith("!!"):
                    c = c.replace("!!" , "!" , 1)

                strings.append(c)
            else:
                strings += c.get_all_child_strings()
        return strings

    def should_evaluate_if(self):
        return not self.type in g_dont_expand_if

    @staticmethod
    def type_allows_runs(group_type):
        if group_type in g_no_runs:
            return False
        return True

    @staticmethod
    def get_end_type_for_type(group_type):
        if group_type == TassLineGroupType.weak:
            return TassLineGroupType.end_weak
        elif group_type == TassLineGroupType.if_block:
            return TassLineGroupType.end_if 
        elif group_type == TassLineGroupType.block:
            return TassLineGroupType.end_block
        elif group_type == TassLineGroupType.comment:
            return TassLineGroupType.end_comment
        elif group_type == TassLineGroupType.struct:
            return TassLineGroupType.end_struct
        elif (group_type == TassLineGroupType.macro or
              group_type == TassLineGroupType.segment):
            return TassLineGroupType.end_macro
        elif group_type == TassLineGroupType.union:
            return TassLineGroupType.end_union
        elif group_type == TassLineGroupType.section:
            return TassLineGroupType.end_section
        elif group_type == TassLineGroupType.function:
            return TassLineGroupType.end_function
        return TassLineGroupType.not_special

    @staticmethod
    def get_does_type_make_sub_blocks(group_type):
        for row in g_lineIDstrings:
            if row[1] == group_type:
                return row[3]
        return 0

    @staticmethod
    def identify_line(line):
        stripped_line = line.strip()
        for pair in g_lineIDstrings:
            if pair[2]:
                if pair[0] in stripped_line:
                    return pair[1]
            elif stripped_line.startswith(pair[0]):
                return pair[1]
        match = g_regex_Preprocess_assign.match(line)
        if match:
            return TassLineGroupType.preprocessor_assign
        match = g_regex_assign.match(line)
        if match:
            return TassLineGroupType.assign
        return TassLineGroupType.not_special
