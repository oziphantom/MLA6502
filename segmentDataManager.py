
class segmentDataManager(object):
    def __init__(self):
        self.segments = {}
        self.temp_segment = False
        self.standard_segment_name = "assemData"
        self.temp_segment_name = ""
        self.block_num = 0

    def set_standard_seg_name(self, name):
        self.standard_segment_name = name
    
    def set_temp_seg_name(self, name):
        self.temp_segment_name = name
        self.temp_segment = True

    def clear_temp_seg_name(self):
        self.temp_segment_name = ""
        self.temp_segment = False

    def add_data(self, name, data):
        seg = self.standard_segment_name
        if self.temp_segment:
            seg = self.temp_segment_name
        if seg in self.segments:
            l = self.segments[seg]
        else:
            l = {}
        if name in l:
            print("ERROR - duplicate name " + name + " found in segment " + seg)
            return
        l[name] = data
        self.segments[seg] = l

    def write_segements_to_file(self, out):
        for seg in self.segments:
            out.write(seg + " .section\n")
            for var in self.segments[seg]:
                out.write("\t"+var+" .byte "+self.segments[seg][var]+"\n")
            out.write(".send " + seg+"\n")

    def get_block_num(self):
        return self.block_num

    def inc_block_num(self):
        self.block_num += 1
