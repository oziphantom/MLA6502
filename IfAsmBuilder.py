import midLevelAssem
from assemNumHelper import AssemNumHelper
from pyLog import pylog

class IfAsmBuilder(object):
    @staticmethod
    def get_asm_string_for_if(if_type, if_input, compare, destination, register):
        skip_load = if_input.lower() == register;
        if register:
            load = IfAsmBuilder.get_load_for_register(register)
            cmp = IfAsmBuilder.get_compare_for_register(register)
        else:
            load = "bit "
            cmp = " N/A "

        if not skip_load:
            output = ["\t" + load + if_input + "\n"]
        else:
            output = ["\t"]
        if if_type == midLevelAssem.MLAOperator.equal:
            output += ["\t" + cmp + compare + "\n"]
            output += ["\tbeq " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.not_equal:
            output += ["\t" + cmp + compare + "\n"]
            output += ["bne " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.less_than:
            output += ["\t" + cmp + compare + "\n"]
            output += ["\tbcc " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.greater_than:
            output += ["\t" + cmp + compare + "\n"]
            output += ["\tbeq + \n"]
            output += ["\tbcs " + destination + "\n"]
            output += ["+ \n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.less_than_equal_to:
            output += [cmp + compare + "\n"]
            output += ["\tbeq " + destination + "\n"]
            output += ["\tbcc " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.greater_than_equal_to:
            output += ["\t" + cmp + compare + "\n"]
            output += ["\tbcs " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.zero:
            output += ["\tbeq " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.not_zero:
            output += ["\tbne " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.positive:
            output += ["\tbpl " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.negative:
            output += ["\tbmi " + destination + "\n"]
            return output
        elif if_type == midLevelAssem.MLAOperator.unknown:
            return ["!!--------MLA ERROR"]

    @staticmethod
    def get_asm_string_for_if_bit(match_results, tdm):
        src = match_results.group(2).strip()
        src_lower = src.lower()
        not_version = match_results.group(1)
        bit_value = match_results.group(3).strip()
        dest = match_results.group(4).strip()
        can_use_bit = True
        use_bit = False
        use_bpl_bmi = False
        use_bvc_bvs = False

        if (src_lower.endswith(",x") or src_lower.endswith(",y") ):
            can_use_bit = False

        if AssemNumHelper.is_immediate(bit_value):
            value = tdm.lookup_value_for(bit_value)
            if isinstance(value, int):
                if value == 128:
                    if can_use_bit:
                        pylog.write_log("bit #128 to BIT/BPL/BMI")
                        use_bit = True
                        use_bpl_bmi = True
                    else:
                        pylog.write_log("bit #128 to LDA/BPL/BMI")
                        use_bpl_bmi = True
                if value == 64:
                    if can_use_bit:
                        pylog.write_log("bit #64 to BIT/BVC/BVS")
                        use_bit = True
                        use_bvc_bvs = True

        if src_lower != "a":
            if use_bit:
                out_string = "\tbit " + src + "\n"
            else:
                out_string = "\tlda " + src + "\n"
        else:
            out_string = ""
        if not use_bit and not use_bpl_bmi:
            out_string += "\tand " + match_results.group(3).strip()+"\n"
        if not_version:  # then we have a 'not'
            if use_bpl_bmi:
                out_string += "\tbmi " + dest
            elif use_bvc_bvs:
                out_string += "\tbvs " + dest
            else:
                out_string += "\tbne " + dest
        else:
            if use_bpl_bmi:
                out_string += "\tbpl " + dest
            elif use_bvc_bvs:
                out_string += "\tbvc " + dest
            else:
                out_string += "\tbeq " + dest
        if match_results.group(5):
            out_string += "; " + match_results.group(5).strip() + "\n"
        else:
            out_string += "\n"
        return out_string

    @staticmethod
    def get_load_for_register(register):
        if register == "a":
            return "lda "
        if register == "x":
            return "ldx "
        if register == "y":
            return "ldy "
        return "Unknown register " + register

    @staticmethod
    def get_compare_for_register(register):
        if register == "a":
            return "cmp "
        if register == "x":
            return "cpx "
        if register == "y":
            return "cpy "
        return "Unknown register " + register
