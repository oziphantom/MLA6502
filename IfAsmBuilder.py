import midLevelAssem


class IfAsmBuilder(object):
    @staticmethod
    def get_asm_string_for_if(if_type, if_input, compare, destination, register):
        skip_load = if_input.lower() == register;
        load = IfAsmBuilder.get_load_for_register(register)
        cmp = IfAsmBuilder.get_compare_for_register(register)
        if not skip_load:
            output = "\t" + load + if_input + "\n"
        else:
            output = "\t"
        if if_type == midLevelAssem.MLAOperator.equal:
            output += "\t" + cmp + compare + "\n"
            output += "\tbeq " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.not_equal:
            output += "\t" + cmp + compare + "\n"
            output += "bne " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.less_than:
            output += "\t" + cmp + compare + "\n"
            output += "\tbcc " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.greater_than:
            output += "\t" + cmp + compare + "\n"
            output += "\tbeq + \n"
            output += "\tbcs " + destination + "\n"
            output += "+ \n"
            return output
        elif if_type == midLevelAssem.MLAOperator.less_than_equal_to:
            output += cmp + compare + "\n"
            output += "\tbeq " + destination + "\n"
            output += "\tbcc " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.greater_than_equal_to:
            output += "\t" + cmp + compare + "\n"
            output += "\tbcs " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.zero:
            output += "\tbeq " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.not_zero:
            output += "\tbne " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.positive:
            output += "\tbpl " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.negative:
            output += "\tbmi " + destination + "\n"
            return output
        elif if_type == midLevelAssem.MLAOperator.unknown:
            return "MLA ERROR"

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
