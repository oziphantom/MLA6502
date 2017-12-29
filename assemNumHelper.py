
class AssemNumHelper:

    @staticmethod
    def is_immediate(value):
        if value.lstrip().startswith('#') > 0:
            return True
        return False

    @staticmethod
    def is_binary(value):
        stripped = value.lstrip()
        if stripped.startswith('%') > 0 or stripped.startswith('#%'):
            return True
        return False

    @staticmethod
    def is_hex(value):
        stripped = value.lstrip()
        if stripped.startswith('$') > 0 or stripped.startswith('#$'):
            return True
        return False

    @staticmethod
    def get_int_from_hex(value):
        if value.startswith("$"):
            return int(value.strip()[1:], 16)
        else:
            raise ValueError("hex value should start with $")

    @staticmethod
    def get_int_from_binary(value):
        if value.startswith("%"):
            return int(value.strip()[1:], 2)
        else:
            raise ValueError("hex value should start with %")

    @staticmethod
    def is_equation(value):
        if (("+" in value) or
           ("-" in value) or
           ("*" in value) or
           ("/" in value)):
            return True
        return False

    @staticmethod
    def convert_equation_to_python(value):
        if ";" in value:
            value = value[0:value.indexof(";")]
        value = value.replace("$", "0x")
        value = value.replace("%", "0b")
        return value.replace(".", "_")

    @staticmethod
    def get_invalid_value():
        return 64 * 1024

    @staticmethod
    def is_invalid_value(value):
        if value >= (64 * 1024):
            return True
        return False

    @staticmethod
    def is_number_negative(value):
        if (value >= 128) and (value <= 255):
            return True
        return False

    @staticmethod
    def is_number_positive(value):
        if (value >= 0) and (value <= 127):
            return True
        return False
