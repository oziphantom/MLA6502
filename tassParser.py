from tassLineGroup import TassLineGroupType
from tassLineGroup import TassLineGroup
from tassBlockExpander import tassBlockNamespaceExpander
from tassDefineLine import TassDefineLine
from segmentDataManager import segmentDataManager 
from pyLog import pylog
import tassDefineManager
import os.path
import sys


class TassParser(object):
    def __init__(self):
        self.defines = {}
        self.classifiedLines = []

    def parse_lines(self, file):
        assert isinstance(file, str)
        with open(file, "r") as inc:
            lines = inc.readlines()
            line_inter = iter(lines)
            while True:
                try:
                    curr_line = TassLineGroup()
                    full_line = next(line_inter)
                    curr_line.children = [full_line]
                    curr_line.type = TassLineGroup.identify_line(full_line)
                    if curr_line.type == TassLineGroupType.include:
                        # then we need to open it and dump it inline
                        working_dir = os.path.dirname(file)
                        first_quote = full_line.find('"')
                        end_quote = full_line.find('"', first_quote+1)
                        new_file_name = full_line[first_quote+1:end_quote]
                        new_full_path = os.path.join(working_dir, new_file_name)
                        pylog.write_log("found include '"+full_line+"' opening file '"+new_full_path+"'")
                        enter_line = TassLineGroup()
                        enter_line.children = ["\n; MidLevelAssem Including file - "+new_file_name+"\n"]
                        enter_line.type = TassLineGroupType.not_special
                        self.classifiedLines.append(enter_line)

                        self.parse_lines(new_full_path)

                        leave_line = TassLineGroup()
                        leave_line.children = ["\n; MidLevelAssem leaving file - "+new_file_name+"\n"]
                        leave_line.type = TassLineGroupType.not_special
                        self.classifiedLines.append(leave_line)
                    else:    
                        self.classifiedLines.append(curr_line)
                except StopIteration:
                    break

    def strip_comment_blocks(self):
        line_inter = iter(self.classifiedLines)
        new_groups = []
        while True:
            try:
                group = next(line_inter)
                if group.type == TassLineGroupType.comment:
                    while True:
                        if next(line_inter).type == TassLineGroupType.end_comment:
                            break
                else:
                    new_groups.append(group)
            except StopIteration:
                break
        self.classifiedLines = new_groups

    def fold_classified_lines(self, start, end, curr_type):
        new_group = TassLineGroup()
        new_group.type = curr_type
        new_group.children = []
        for group in self.classifiedLines[start:end+1]:  # make inclusive
            new_group.children.append(group)
        new_group.fully_collapsed = False
        self.classifiedLines[start] = new_group
        del self.classifiedLines[start+1:end+1]  # make inclusive

    def collapse_identical_sub_blocks(self):
        lines_length = len(self.classifiedLines)
        i = lines_length-1
        t = TassLineGroupType.not_special
        curr_type = self.classifiedLines[lines_length-1].type
        while i >= 0:
            end = i
            while i >= 0:
                t = self.classifiedLines[i].type
                if t != curr_type:
                    break
                i = i - 1
            if end-i > 1:
                if TassLineGroup.type_allows_runs(curr_type):
                    self.fold_classified_lines(i+1, end, curr_type)
            curr_type = t

    def make_sub_blocks(self):
        found = True
        while found:
            found = False
            lines_length = len(self.classifiedLines)
            i = 0
            while i < lines_length:
                t = self.classifiedLines[i].type
                if not self.classifiedLines[i].fully_collapsed:
                    if TassLineGroup.get_does_type_make_sub_blocks(t):
                        start = i
                        i = i + 1  # next
                        base_type = t
                        target = TassLineGroup.get_end_type_for_type(t)
                        while i < lines_length:
                            new_t = self.classifiedLines[i].type
                            if new_t == target:  # found it
                                self.fold_classified_lines(start, i, base_type)
                                self.classifiedLines[start].fully_collapsed = True
                                found = True
                                break
                            elif TassLineGroup.get_does_type_make_sub_blocks(new_t):  # this also wants to make children
                                if self.classifiedLines[i].fully_collapsed:  # did we already collapse it
                                    i = i + 1  # yes step over and carry on
                                else:
                                    start = i
                                    i = i + 1  # next
                                    base_type = new_t
                                    target = TassLineGroup.get_end_type_for_type(new_t)  # make new target and carry on
                            else:
                                i = i + 1
                        break  # restart from the top to make sure
                    else:
                        self.classifiedLines[i].fully_collapsed = True
                        i = i + 1
                else:
                    i = i + 1   

    def print_blocks(self, indent):
        for block in self.classifiedLines:
            self.print_block_internal(indent, block)

    def print_block_internal(self, indent, parent):
        print(indent+str(parent.type)+"------")
        next_indent = indent + ">"
        for local_line in parent.children:
            if isinstance(local_line, str):
                print(indent + local_line.strip())
            else:
                self.print_block_internal(next_indent, local_line)

    def write_out_file(self, local_output):
        for block in self.classifiedLines:
            self.write_out_file_internal(local_output, block)
    
    def write_out_file_internal(self, local_output, parent):
        if isinstance(parent, str):
            local_output.write(parent)
        else:
            for local_line in parent.children:
                if isinstance(local_line, str):
                    local_output.write(local_line)
                else:
                    self.write_out_file_internal(local_output, local_line)

    def evaluate_block_assigns(self, classified_lines, block_assign_lines, weak_block_assign, tbe):
        for cl in classified_lines:
            if cl.type == TassLineGroupType.block:
                block_assign_lines.update(tbe.expandBlock(cl))
            elif (cl.type == TassLineGroupType.assign or
                  cl.type == TassLineGroupType.preprocessor_assign):
                for y in cl.children:
                    local_line = TassDefineLine()
                    if isinstance(y, str):
                        local_line.set_line(y)
                    else:
                        local_line.set_line(y.children[0])
                    block_assign_lines[local_line.name] = local_line
            elif cl.type == TassLineGroupType.weak:
                weak_block_assign.update(tbe.expandBlock(cl))
            elif cl.type == TassLineGroupType.section:
                self.evaluate_block_assigns(cl.children[1:-1], block_assign_lines, weak_block_assign, tbe)


try:
    inputFile = sys.argv[1]
    tassArgsFile = None
    if len(sys.argv) > 2:
        tassArgsFile = sys.argv[2]
    outputFile = inputFile[:inputFile.rfind('.')+1]+"mla"

    pylog.open(inputFile[:-3]+"html")

    tp = TassParser()
    tp.parse_lines(inputFile)

    pylog.write_log("stripping comment blocks")
    tp.strip_comment_blocks()
    pylog.write_log("collapsing identical blocks")
    tp.collapse_identical_sub_blocks()
    # tp.print_blocks("")
    pylog.write_log("making sub blocks")
    tp.make_sub_blocks()
    # tp.print_blocks("")
    pylog.write_log("expanding namespaces to abs paths")
    TBE = tassBlockNamespaceExpander()
    block_assign_lines_to_evaluate = {}
    weak_block_assign_to_evaluate = {}
    tp.evaluate_block_assigns(tp.classifiedLines, block_assign_lines_to_evaluate, weak_block_assign_to_evaluate, TBE)

    for x in block_assign_lines_to_evaluate:
        line = block_assign_lines_to_evaluate[x]        
        line.resolve_all_sub_names(block_assign_lines_to_evaluate)

    TDM = tassDefineManager.TassDefineManager()
    tass_args_to_evaluate = None
    if tassArgsFile is not None:
        tass_args_to_evaluate = TDM.parse_from_tass_args_file(tassArgsFile)

    TDM.parse_from_classified_lines(weak_block_assign_to_evaluate)
    pylog.write_log("Weak Values")
    pylog.write_dic(TDM.variables)
    if tass_args_to_evaluate is not None:
        TDM.parse_from_classified_lines(tass_args_to_evaluate)
    pylog.write_log("Command line Values")
    pylog.write_dic(TDM.variables)
    TDM.parse_from_classified_lines(block_assign_lines_to_evaluate)
    pylog.write_log("Final set Values")
    pylog.write_dic(TDM.variables)
    pylog.write_log("If blocks")
    while True:
        counter = TDM.resolve_if_blocks(tp.classifiedLines)
        if counter == 0:
            break
    pylog.write_log("Mid Level blocks")
    SDM = segmentDataManager()
    while True:
        counter = TDM.resolve_mid_level_blocks(tp.classifiedLines, SDM)
        if counter == 0:
            break

    with open(outputFile, "w") as output:
        tp.write_out_file(output)
        output.write("\n; MID LEVEL DATA SEGMENTS\n")
        SDM.write_segements_to_file(output)
        pylog.close()

except ValueError as err:
    pylog.close()
    print(repr(err))
    sys.exit(1)
