g_log = None

class pylog:
    @staticmethod
    def open(name):
        global g_log
        g_log = open(name,"w")
        g_log.write("<!DOCTYPE html><html><head></head><body>")

    @staticmethod
    def close():
        g_log.write("</body></html>")
        g_log.close()

    @staticmethod
    def write_log(thing):
        g_log.write(thing+"<BR/>")

    @staticmethod
    def write_dic(thing):
        keys = list(thing)
        keys.sort()
        for key in keys:
            value = thing[key]
            g_log.write("<b>"+key+"</b>:"+str(value)+"<BR/>")
    
    @staticmethod
    def write_block_string(thing):
        strings = thing.get_all_child_strings()
        g_log.write("<code>")
        for s in strings:
            h = s.replace("\n","<BR/>")
            g_log.write(h)
        g_log.write("</code><BR/>")
