import assemNumHelper
import re
from tassLineGroup import TassLineGroupType
from tassLineGroup import TassLineGroup
from tassDefineLine import TassDefineLine
from pyLog import pylog

class tassBlockNamespaceExpander:
    def expandBlock(self, block):
        output_lines = {}
        start = block.children[0]
        if not isinstance(start, str):
            start = start.children[0]
        to_convert = block.children[1:-1] # skip first and last as they are the block start and end
        dot = start.find('.')
        if dot > 0:
            name_space = start[0:dot-1].strip()
            pylog.write_log(name_space)
        else:
            name_space = ""
        self.expandBlockInternal(to_convert, name_space, output_lines)
        return output_lines

    def expandBlockInternal(self, to_look_at, prefix, output_lines):
        for x in to_look_at:
            if (x.type == TassLineGroupType.assign or
                    x.type == TassLineGroupType.preprocessor_assign):
                for y in x.children:
                    if isinstance(y, str):
                        line = TassDefineLine()
                        line.set_line(y)
                        line.attach_prefix(prefix)
                        output_lines[line.name] = line
                    else:
                        for z in y.children:
                            line = TassDefineLine()
                            line.set_line(z)
                            line.attach_prefix(prefix)
                            output_lines[line.name] = line
            elif x.type == TassLineGroupType.block:
                child_name = x.children[0].children[0]
                name_space = child_name[0:child_name.find('.')-1].strip()
                to_convert = x.children[1:-1] # skip first and last as they are the block start and end
                sub_namespace = prefix+"."+name_space
                pylog.write_log("inner namespace = " + name_space)
                pylog.write_log("so complete is :" + sub_namespace)
                self.expandBlockInternal(to_convert, sub_namespace, output_lines)
