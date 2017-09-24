from assemNumHelper import AssemNumHelper
import segmentDataManager
import tassDefineManager
from enum import Enum
from pyLog import pylog

# inputFile = "D:\\GitHub\\SquidJump\\squid.asm"
# outputFile = "D:\\GitHub\\SquidJump\\squid.psm"
# inputFile = "D:/GitHub/test/midLevel.asm"
# outputFile = "D:/GitHub/test/midLevel.psm"


class MLASpecial(Enum):
    not_special = 0
    neg = 1
    pos = 2
    not_zero = 3


class MLALineClass(Enum):
    straight_assign = 0
    if_comp = 1
    operator = 2
    index_prohibited = 3


class MLAOperator(Enum):
    equal = 0
    not_equal = 1
    less_than = 2
    greater_than = 3
    less_than_equal_to = 4
    greater_than_equal_to = 5
    zero = 6
    not_zero = 7
    positive = 8
    negative = 9
    unknown = 128


g_2operatorList = [MLAOperator.zero, MLAOperator.not_zero, MLAOperator.positive, MLAOperator.negative]


class MLAIndexPrehib(Enum):
    none = 0
    x = 1
    y = 2
    xy = 3


class MLAPair:
    def __init__(self):
        self.dest = None
        self.src = None
        self.dest_original = None
        self.src_original = None
        self.run = False
        self.special = False
        self.special_mode = MLASpecial.not_special
        self.word = False
        self.src_immediate = False

    def make_pair(self, line, tdm):
        line = line.strip()
        equals = line.find('=')
        comment = line.find(';')
        word = line.find('w=')
        if comment < 0:
            comment = len(line)
        first_token_end = equals
        if word > 0:
            first_token_end = word
            self.word = True

        self.dest_original = line[2:first_token_end].strip()
        self.src_original = line[equals+1:comment].strip()
        self.src_immediate = self.src_original.startswith("#")

        if not self.src_immediate:
            if self.src_original.isnumeric():
                if int(self.src_original) < 256:
                    raise ValueError("non immediate assign with decimal - are you really sure? in line " + line)
            if "%" in self.src_original:
                raise ValueError("Assign to % non immediate - are you really sure? in line " + line)

        if self.src_original == "NEG":
            self.special = True
            self.special_mode = MLASpecial.neg
            self.src_immediate = True
        elif self.src_original == "POS":
            self.special = True
            self.special_mode = MLASpecial.pos
            self.src_immediate = True
        elif self.src_original == "NOTZERO":
            self.special = True
            self.special_mode = MLASpecial.not_zero
            self.src_immediate = True

        if "," in self.src_original:
            subs = self.src_original.split(",")
            count = len(subs)
            self.run = False
            if count > 2:
                self.run = True
            elif count == 2:
                if not (subs[1] == 'x' or
                        subs[1] == 'y'):
                    self.run = True
        if self.run:
            self.src = self.src_original
        else:    
            self.src = tdm.lookup_value_for(self.src_original)

        self.dest = tdm.lookup_value_for(self.dest_original)


def is_valid_line(line):
    if line.startswith("!!"):
        if line.find('=') > 0:
            return True
        safe = line.strip().lower()
        if safe == '!!x':
            return True
        if safe == '!!y':
            return True
        if safe == '!!xy':
            return True
        if safe == '!!yx':
            return True
    return False


def is_line_index_prehibit(line):
    safe = strip_lower_remove_comment(line)
    if safe == '!!x':
        return True
    if safe == '!!y':
        return True
    if safe == '!!xy':
        return True
    if safe == '!!yx':
        return True
    return False


def strip_lower_remove_comment(line):
    local = line
    comment = line.find(';')
    if comment > 0:
        local = line[:comment]
    return local.strip().lower()


def get_prehib_enum_for_line(line):
    safe = strip_lower_remove_comment(line)
    if safe == '!!x':
        return MLAIndexPrehib.x
    if safe == '!!y':
        return MLAIndexPrehib.y
    if safe == '!!xy':
        return MLAIndexPrehib.xy
    if safe == '!!yx':
        return MLAIndexPrehib.xy
    return MLAIndexPrehib.none


def get_index_letter_for_prehib(prehib):
    if prehib == MLAIndexPrehib.x:
        return "y"
    if prehib == MLAIndexPrehib.y:
        return "x"
    if prehib == MLAIndexPrehib.none:
        return "x"
    return "f"  # for fail


def get_line_class(line):
    if line.strip().startswith("!!if"):
        return MLALineClass.if_comp
    if ("+=" in line or
            "-=" in line or
            "&=" in line or
            "|=" in line or
            "^=" in line or
            ">>=" in line or
            "<<=" in line or
            "&|=" in line):
        return MLALineClass.operator
    if is_line_index_prehibit(line):
        return MLALineClass.index_prohibited
    return MLALineClass.straight_assign


def get_src_dest_from_line(line, tdm):
    pair = MLAPair()
    pair.make_pair(line, tdm)
    return pair


def addPair(pairs, src, dest):
    if src in pairs:
        dests = pairs[src] # already have this value, so append it
        dests.append(dest)
        pairs[src] = dests
    else:
        pairs[src] = [dest] # just add it


def convert_lines_to_asm(lines, segmentDM, tdm):
    out_string = []
    straights = []
    prehib = MLAIndexPrehib.none
    for line in lines:
        clas = get_line_class(line)
        if clas == MLALineClass.straight_assign:
            straights.append(line)
        elif clas == MLALineClass.if_comp:
            if len(straights) > 0:
                out_string += convert_straight_assignment_block_to_asm(straights, segmentDM, tdm, prehib)
                straights = []
            out_string += (convert_if_line(line, segmentDM, tdm))
        elif clas == MLALineClass.operator:
            if len(straights) > 0:
                out_string += convert_straight_assignment_block_to_asm(straights, segmentDM, tdm, prehib)
                straights = []
            out_string += convert_operator_line(line, segmentDM, tdm)
        elif clas == MLALineClass.index_prohibited:
            prehib = get_prehib_enum_for_line(line)
    if len(straights) > 0:
        out_string += convert_straight_assignment_block_to_asm(straights, segmentDM, tdm, prehib)
    return out_string


def convert_straight_assignment_block_to_asm(lines, segmentDM, tdm, prehib):
    # for each item we need to work out what is the src and the dest
    pairs = {}
    out_string = []
    single = []
    immediate_single = []
    words = []
    runs = []
    for line in lines:
        sd = get_src_dest_from_line(line, tdm)
        if sd.word:
            words.append(sd)
        elif sd.run:
            runs.append(sd)
        elif sd.src_immediate:
            immediate_single.append(sd)
        else:
            single.append(sd)

    for thing in single:
        addPair(pairs, thing.src, thing.dest)

    for thing in words:
        # is it immediate word or address
        if thing.src_immediate:
            local_src = str(thing.src)
            if local_src.startswith("#"):
                local_src = local_src[1:]
            # make lo
            addPair(pairs, "#<"+local_src, thing.dest)
            # make hi
            addPair(pairs, "#>"+local_src, str(thing.dest)+"+1")
        else:  # nope its a word copy
            addPair(pairs, thing.src, thing.dest)
            addPair(pairs, str(thing.src)+"+1", str(thing.dest)+"+1")

    index_letter = get_index_letter_for_prehib(prehib)
    # now we have a list of values that need to go to addresses
    for thing in runs:
        split_key = thing.src.split(',')
        split_key_len = len(split_key)
        if split_key_len > 127:
            print("warning , assigned over 127 entries, will be truncated.. you crazy fool")
        blockCounter = segmentDM.get_block_num()
        line = "\tld"+index_letter+" #"+str(split_key_len-1)
        line += "\n-\tlda blockData_"+str(blockCounter)+","+index_letter+"\n"
        line += "\tsta "+str(thing.dest)+","+index_letter+"\n"
        line += "\tde"+index_letter+"\n"
        line += "\tbpl -\n"
        out_string.append(line)
        # out.write(".segment data\nblockData_"+str(blockCounter)+"\t.byte "+key+"\n.send data\n")
        segmentDM.add_data("blockData_"+str(blockCounter), thing.src)
        segmentDM.inc_block_num()

    numbers = []
    imm_pairs = {}
    specials = []

    for thing in immediate_single:
        if isinstance(thing.src, str):
            if thing.special:
                specials.append(thing)
            else:
                addPair(pairs, thing.src, thing.dest)  # nothing special we can do so add to dest
        else:
            if thing.src_immediate:
                numbers.append(thing.src)
                addPair(imm_pairs, thing.src, thing.dest)
            else:
                addPair(pairs, thing.src, thing.dest)  # nothing special we can do so add to dest

    for spec in specials:
        found = False
        if spec.special_mode == MLASpecial.neg:
            value = 0
            for num in numbers:
                if AssemNumHelper.is_number_negative(num):
                    found = True
                    value = num
                    break
            if not found:
                numbers.append(128)
                value = 128
            addPair(imm_pairs, value, spec.dest)
            spec.special = False
            spec.src = value
        elif spec.special_mode == MLASpecial.pos:
            value = 0
            for num in numbers:
                if AssemNumHelper.is_number_positive(num):
                    found = True
                    value = num
                    break
            if not found:
                numbers.append(0)
                value = 0
            addPair(imm_pairs, value, spec.dest)
            spec.special = False
            spec.src = value
        elif spec.special_mode == MLASpecial.not_zero:
            value = 0
            for num in numbers:
                if num != 0:
                    found = True
                    value = num
                    break
            if not found:
                numbers.append(1)
                value = 1
            addPair(imm_pairs, value, spec.dest)
            spec.special = False
            spec.src = value

    numbers.sort()
    number_safe = []

    num_len = len(numbers)
    if num_len > 0:  # do we have just numbers to deal with
        if prehib == MLAIndexPrehib.xy:
            for key in imm_pairs:
                pair = imm_pairs[key]
                for d in pair:
                    addPair(pairs, "#"+str(key), str(d))
        else:
            # make runs
            i = 1
            start = numbers[0]
            current_run = [start]
            dests = imm_pairs[numbers[0]]
            safe = True
            for dest in dests:
                if isinstance(dest, str):
                    if ",x" in dest or ",y" in dest:
                        safe = False
            number_safe.append(safe)
            num_runs = []
            while i < num_len:
                dests = imm_pairs[numbers[i]]
                safe = True
                break_run = False
                for dest in dests:
                    if isinstance(dest, str):
                        if ",x" in dest or ",y" in dest:
                            safe = False
                if safe:
                    if numbers[i] == start+1:
                        current_run += [numbers[i]]
                        start = start + 1
                    elif numbers[i] != start:
                        break_run = True
                else:
                    break_run = True
                number_safe.append(safe)
                if break_run:
                    num_runs.append(current_run)
                    start = numbers[i]
                    current_run = [start]
                
                i += 1

            num_runs.append(current_run)

            # check for a FF->0 wrap run
            if len(num_runs) >= 2:
                first = num_runs[0]
                safe = number_safe[0]
                last_in_runs = len(num_runs)-1
                last = num_runs[last_in_runs]
                safe = safe & number_safe[last_in_runs]
                if safe:
                    if first[0] == 0:
                        if last[len(last)-1] == 255:
                            num_runs[0] = last + first
                            num_runs = num_runs[0:-1]

            for run in num_runs:
                if len(run) == 1:  # no index = no run
                    pair = imm_pairs[run[0]]
                    for d in pair:
                        addPair(pairs, "#"+str(run[0]), str(d))
                else:
                    pair = imm_pairs[run[0]]
                    out_string.append("\tld"+index_letter+" #"+str(run[0])+"\n")
                    for d in pair:
                        out_string.append("\tst"+index_letter+" "+str(d)+"\n")
                    i = 1
                    while i < len(run):
                        pair = imm_pairs[run[i]]
                        out_string.append("\tin"+index_letter+"\n")
                        for d in pair:
                            out_string.append("\tst"+index_letter+" "+str(d)+"\n")
                        i += 1

    for key in pairs:
        out_string.append("\tlda "+str(key)+"\n")
        for dest in pairs[key]:
            out_string.append("\tsta "+str(dest)+"\n")
    return out_string


def get_if_tokens3(line, operator):
    then_split = line.split("then ")
    operator_split = then_split[0].split(operator)
    branch = then_split[1].strip()
    value = operator_split[1].strip()
    comparer = operator_split[0].strip()[4:]
    return [comparer, value, branch]


def get_if_tokens2(line, operator):
    then_split = line.split("then ")
    operator_split = then_split[0].split(operator)
    branch = then_split[1].strip()
    comparer = operator_split[0].strip()[4:]
    return [comparer, branch]


def convert_if_line(line, segmentDM, tdm):
    operator = MLAOperator.unknown
    out_string = ""
    macro = ""
    if "==" in line:
        operator = MLAOperator.equal
        params = get_if_tokens3(line, "==")
        macro = "#ISAEqualTo"
        if AssemNumHelper.is_immediate(params[1]):
            value = tdm.lookup_value_for(params[1])
            if isinstance(value, int):
                if value == 0:
                    pylog.write_log("converting == #0 to =0")
                    operator = MLAOperator.zero
                    macro = "#ISAZero"
                    params[1] = params[2]
    elif "!=" in line:
        operator = MLAOperator.not_equal
        params = get_if_tokens3(line, "!=")
        macro = "#ISANotEqualTo"
        if AssemNumHelper.is_immediate(params[1]):
            value = tdm.lookup_value_for(params[1])
            if isinstance(value, int):
                if value == 0:
                    pylog.write_log("converting != #0 to !0")
                    operator = MLAOperator.not_zero
                    macro = "#ISANotZero"
                    params[1] = params[2]
    elif ">=" in line:
        operator = MLAOperator.less_than
        params = get_if_tokens3(line, ">=")
        macro = "#ISAGTE"
        if AssemNumHelper.is_immediate(params[1]):
            value = tdm.lookup_value_for(params[1])
            if isinstance(value, int):
                if value == 128:
                    pylog.write_log("converting >= #128 to =+")
                    operator = MLAOperator.positive
                    macro = "#ISAPlus"
                    params[1] = params[2]
                elif value == 1:
                    pylog.write_log("converting >= #1 to !0")
                    operator = MLAOperator.not_zero
                    macro = "#ISANotZero"
                    params[1] = params[2]
    elif "<=" in line:
        operator = MLAOperator.greater_than
        params = get_if_tokens3(line, "<=")
        macro = "#ISALTE"
        if AssemNumHelper.is_immediate(params[1]):
            value = tdm.lookup_value_for(params[1])
            if isinstance(value, int):
                if value == 127:
                    pylog.write_log("converting <= #127 to =-")
                    operator = MLAOperator.negative
                    macro = "#ISAMinus"
                    params[1] = params[2]
                elif value <= 254:
                    pylog.write_log("converting <= #"+str(value)+"+1 to < #"+str(value)+"+1")
                    operator = MLAOperator.less_than
                    macro = "#ISALT"
                    params[1] = params[1]+"+1"
    elif ">" in line:
        operator = MLAOperator.greater_than_equal_to
        params = get_if_tokens3(line, ">")
        macro = "#ISAGT"
        if AssemNumHelper.is_immediate(params[1]):
            value = tdm.lookup_value_for(params[1])
            if isinstance(value, int):
                if value == 127:
                    pylog.write_log("converting > #127 to =+")
                    operator = MLAOperator.positive
                    macro = "#ISAPlus"
                    params[1] = params[2]
                elif value <= 254:
                    pylog.write_log("converting > #"+str(value)+"+1 to >= #"+str(value)+"+1")
                    operator = MLAOperator.greater_than_equal_to
                    macro = "#ISAGTE"
                    params[1] = params[1]+"+1"
    elif "<" in line:
        operator = MLAOperator.less_than_equal_to
        params = get_if_tokens3(line, "<")
        macro = "#ISALT"
        if AssemNumHelper.is_immediate(params[1]):
            value = tdm.lookup_value_for(params[1])
            if isinstance(value, int):
                if value == 128:
                    pylog.write_log("converting < #128 to =-")
                    operator = MLAOperator.negative
                    macro = "#ISAMinus"
                    params[1] = params[2]                
    elif "=0" in line:
        operator = MLAOperator.zero
        params = get_if_tokens2(line, "=0")
        macro = "#ISAZero"
    elif "!0" in line:
        operator = MLAOperator.not_zero
        params = get_if_tokens2(line, "!0")
        macro = "#ISANotZero"
    elif "=+" in line:
        operator = MLAOperator.positive
        params = get_if_tokens2(line, "=+")
        macro = "#ISAPlus"
    elif "=-" in line:
        operator = MLAOperator.negative
        params = get_if_tokens2(line, "=-")
        macro = "#ISAMinus"

    if operator == MLAOperator.unknown:
        print("unknown if statment found ", line)
    elif operator in g_2operatorList:  # 2 operators
        if ",x" in params[0] or ",X" in params[0]:
            out_string = ["\t"+macro+"iX "+params[0][:params[0].find(",")]+","+params[1]+"\n"]
        elif ",y" in params[0] or ",Y" in params[0]:
            out_string = ["\t"+macro+"iY "+params[0][:params[0].find(",")]+","+params[1]+"\n"]
        else:
            out_string = ["\t"+macro+" "+params[0]+","+params[1]+"\n"]
    else:  # 3 operators
        if ",x" in params[0] or ",X" in params[0]:
            params[0] = params[0][:params[0].find(",")]
            macro += "iX"
        if ",y" in params[0] or ",Y" in params[0]:
            params[0] = params[0][:params[0].find(",")]
            macro += "iY"
        if ",x" in params[1] or ",X" in params[1]:
            params[1] = params[1][:params[1].find(",")]
            macro += "_iX"
        if ",y" in params[1] or ",Y" in params[1]:
            params[1] = params[1][:params[1].find(",")]
            macro += "_iY"
        if operator == MLAOperator.greater_than:
            if "+" in params[2]:
                print("ERROR > Operator can not have + as a branch target!")
        out_string = ["\t"+macro+" "+params[0]+","+params[1]+","+params[2]+"\n"]
    return out_string


def getOperatorTokens2(line, operator):
    parts = line.split(operator)
    var = parts[0].strip()[2:]  # remove the !!
    value = parts[1].strip()
    if ";" in value:
        value = value[0:value.find(";")].strip()
    return [var, value]


def getOperatorTokens3(line, operator):
    parts = line.split(operator)
    var = parts[0].strip()[2:]  # remove the !!
    value = parts[1].strip()
    if ";" in value:
        value = value[0:value.find(";")].strip()
    values = value.split(",")
    # 0 1 2 3
    # v v
    # v x v
    # v v x
    # v x v x
    if len(values) == 3:
        # then we need to do some folding
        first = values[1].strip().lower()
        second = values[2].strip().lower()
        found = False
        if (first == "x") or (first == "y"):
            values[0] = values[0]+","+first
            values[1] = second
            found = True
        if (second == "x") or (second == "y"):
            values[1] = values[1]+","+second
            found = True
        if not found:
            pylog.write_log("invalid format for ",line)
    elif len(values) == 4:
            values[0] = values[0]+","+values[1]
            values[1] = values[2]+","+values[3]
    return [var, values[0], values[1]]


def convert_operator_line(line, segmentDM, tdm):
    out_string = ""
    if "+=" in line:
        parts = getOperatorTokens2(line, "+=")
        out_string = ["\tlda " + parts[0]+"\n\tclc\n\tadc "+parts[1]+"\n\tsta "+parts[0]+"\n"]
    elif "-=" in line:
        parts = getOperatorTokens2(line, "-=")
        out_string = ["\tlda " + parts[0]+"\n\tsec\n\tsbc "+parts[1]+"\n\tsta "+parts[0]+"\n"]
    elif "&|=" in line:
        parts = getOperatorTokens3(line, "&|=")
        out_string = ["\tlda " + parts[0]+"\n\tand "+parts[1]+"\n\tora "+parts[2]+"\n\tsta "+parts[0]+"\n"]
    elif "&=" in line:
        parts = getOperatorTokens2(line, "&=")
        out_string = ["\tlda " + parts[0]+"\n\tand "+parts[1]+"\n\tsta "+parts[0]+"\n"]
    elif "|=" in line:
        parts = getOperatorTokens2(line, "|=")
        out_string = ["\tlda " + parts[0]+"\n\tora "+parts[1]+"\n\tsta "+parts[0]+"\n"]
    elif "^=" in line:
        parts = getOperatorTokens2(line, "^=")
        out_string = ["\tlda " + parts[0]+"\n\teor "+parts[1]+"\n\tsta "+parts[0]+"\n"]    
    elif ">>=" in line:
        parts = getOperatorTokens2(line, ">>=")
        out_string = ["\tlda " + parts[0] + "\n\t.rept " + parts[1] + "\n\tlsr a\n\t.next\n\t sta " + parts[0]]
    elif "<<=" in line:
        parts = getOperatorTokens2(line, "<<=")
        out_string = ["\tlda " + parts[0] + "\n\t.rept " + parts[1] + "\n\tasl a\n\t.next\n\t sta " + parts[0]]
    return out_string

'''m_segmentDM = segmentDataManager.segmentDataManager()

with open(inputFile, "r") as inc:
    inLines = inc.readlines()

    conversionLines = []

    with open(outputFile, "w") as m_out:
        line_inter = iter(inLines)
        while True:
            try:
                full_line = next(line_inter)
                trim_line = full_line.lstrip()
                if is_valid_line(trim_line):
                    #we have a conversion line, now loop until we are not on one
                    conversionLines = [trim_line]
                    post_line = ""
                    while True:
                        try:
                            post_line = next(line_inter)
                            post_trim = post_line.lstrip()
                            if is_valid_line(post_trim):
                                conversionLines.append(post_trim)
                            else:
                                break
                        except StopIteration:
                            break
                    # so now I have all the things that are in this block
                    convert_lines_to_asm(m_out, conversionLines, m_segmentDM)
                    conversionLines = []
                    m_out.write(post_line)
                else: #not something we care about, then pass it through
                    m_out.write(full_line)
            except StopIteration:
                break
        m_out.write("\n")
        m_segmentDM.write_segements_to_file(m_out)'''
