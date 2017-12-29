from tassLineGroup import TassLineGroupType
from tassLineGroup import TassLineGroup
from tassDefineLine import TassDefineLine
from pyLog import pylog
from enum import Enum
import assemNumHelper


class IFBlockState(Enum):
    enter = 0
    copy_to_else_end = 1
    ditch_till_end = 2
    ditch_till_else_end = 3


class TassIFBlockResolver:
    def resolveIFBlock(self, block, python_variables):
        i = 0
        count = len(block.children)
        replacement = []
        state = IFBlockState.enter
        pylog.write_log("looking at block ")
        pylog.write_block_string(block)
        while i < count:
            child = block.children[i]
            block_type = child.type
            if state == IFBlockState.enter:
                if (block_type == TassLineGroupType.if_block or
                   block_type == TassLineGroupType.if_else):
                    expr = child.children[0].strip()
                    first_dot = expr.find('.')
                    command_len = 3
                    if ".elsif" in expr:
                        command_len = 6
                    expr_no_if = expr[first_dot+command_len:].strip()
                    pylog.write_log("evaluating "+expr_no_if)
                    result = False
                    try:
                        value = assemNumHelper.AssemNumHelper.convert_equation_to_python(expr_no_if).lower()
                        result = eval(value, python_variables)
                        # found = True
                    except Exception as e:
                        pass
                    pylog.write_log(str(result))
                    if result:
                        # if true, keep all until we hit an end
                        state = IFBlockState.copy_to_else_end
                    else:
                        # if false, ditch until we hit an else or end
                        state = IFBlockState.ditch_till_else_end

            elif state == IFBlockState.copy_to_else_end:
                if (block_type == TassLineGroupType.if_else or
                        block_type == TassLineGroupType.just_else):
                    state = IFBlockState.ditch_till_end
                elif block_type == TassLineGroupType.end_if:
                    state = IFBlockState.enter
                else:
                    replacement.extend([child])
            elif state == IFBlockState.ditch_till_end:
                if block_type == TassLineGroupType.end_if:
                    state = IFBlockState.enter
            elif state == IFBlockState.ditch_till_else_end:
                if block_type == TassLineGroupType.if_else:
                    state = IFBlockState.enter
                    i -= 1  # so we vist this node again in the enter to do the IF
                elif block_type == TassLineGroupType.just_else:
                    state = IFBlockState.copy_to_else_end  # this is an else we need to take
                    pylog.write_log("taking else")
                elif block_type == TassLineGroupType.end_if:
                    state = IFBlockState.enter
            i += 1

        return replacement
