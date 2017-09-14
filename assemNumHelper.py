def is_immediate(value):
    if value.lstrip().startswith('#') > 0:
        return True
    return False

def is_binary(value):
    stripped = value.lstrip()
    if stripped.startswith('%') > 0 or stripped.startswith('#%'):
        return True
    return False

def is_hex(value):
    stripped = value.lstrip()
    if stripped.startswith('$') > 0 or stripped.startswith('#$'):
        return True
    return False

def get_int_from_hex(value):
    return int(value.strip()[1:], 16)

def get_int_from_binary(value):
    return int(value.strip()[1:], 2)

def is_equation(value):
    if (("+" in value) or
        ("-" in value) or
        ("*" in value) or
        ("/" in value)):
        return True
    return False

def convert_equation_to_python(value):
    value = value.replace("$", "0x")
    value = value.replace("%", "0b")
    return value.replace(".", "_")

def get_invalid_value():
    return 64*1024+1

def is_invalid_value(value):
    if value >= ((64*1024)+1):
        return True
    return False

def is_number_negative(value):
    if (value >= 128) and (value <= 255):
        return True
    return False

def is_number_positive(value):
    if (value >= 0) and (value <= 127 ):
        return True
    return False
