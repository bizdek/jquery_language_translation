"""
Usage:
    gen_dict.py <infile> <outfile> <outjsfile> (--merge=<fname> | --langs=<csv>) [--dump=<fname>] [--ignore=<fname>]
    gen_dict.py -h
"""
from docopt import docopt
from bs4 import BeautifulSoup
from collections import OrderedDict

class translate_gen(object):
    def __init__(self, fname, langs=["en"]):
        
        with open(fname, "r") as f:
            content = f.read()

        self.html = BeautifulSoup(content, "html.parser")
        self.langs = langs
        self.cnt = 0
        self.dict = {}
        for lang in self.langs:
            self.dict[lang] = OrderedDict()

    def _add_to_dict(self, name, val):
        for lang in self.langs:
            self.dict[lang][name] = val

    def parse(self, ignore_content=[]):
        for tag in self.html.find_all():
            if tag.string is not None and tag.string not in ignore_content:
                if tag.name not in ["style", "script"]:
                    tstr = tag.string
                    if tag.name == "span":
                        tag["data-trans-t{}".format(self.cnt)] = None
                    else:
                        new_tag = self.html.new_tag("span")
                        new_tag["data-trans-t{}".format(self.cnt)] = None
                        tag.string = ""
                        new_tag.string = tstr
                        tag.append(new_tag)

                    self._add_to_dict("t{}".format(self.cnt), tstr)
                    self.cnt += 1

    def save_context(self, fname):
        pass
    
    def dump(self, outfile, outjsfile):
        out_html = str(self.html)
        with open(outfile, "w") as f:
            f.write(out_html)
        
        out_js = self._format_js()
        with open(outjsfile, "w") as f:
            f.write(out_js)
            
    def _format_js(self):
        ret = ""
        indent = " " * 4
        for lang in self.langs:
            lang_parse = ""
            for n, v in self.dict[lang].items():
                lang_parse += '{}"{}": {},\n'.format(indent, n, self.to_multiline(v))

            ret += '"{}": {{\n{}}}, \n'.format(lang, lang_parse)
        return "const trans = {{\n{}}};\n".format(ret)

    @staticmethod
    def to_multiline(s, line_len = 80, indent=4):
        ind = " " * indent
        r = '"'
        while len(s) > line_len:
            split = [s[line_len:].find(" "), s[line_len].find("\t"), s[line_len:].find("\n")]
            split = list(filter(lambda x: x != -1, split))
            spl = (min(split) + line_len) if len(split) != 0 else line_len
            r , s = r +  translate_gen.fix_line(s[:spl]) + '\\\n' + ind, s[spl:]    
    
        return r + translate_gen.fix_line(s) + '"'

    @staticmethod
    def fix_line(s):
        r = ""
        for c in s:
            if c == "\n":
                c = "\\n"
            elif c == "\t":
                c = "\\t"
            r += c
        return r

def gen_dict(infile, outfile, outjsfile, langs):
    tg = translate_gen(infile, langs)
    print("Parsing", infile, "...")
    tg.parse()
    print("Writing output to ", outfile, outjsfile)
    tg.dump(outfile, outjsfile)


if __name__ == "__main__":
    args = docopt(__doc__)
    print(args)
    langs = None
    if args["--langs"]:
        langs = args["--langs"].split(",")
    gen_dict(args["<infile>"], args["<outfile>"], args["<outjsfile>"], langs)
