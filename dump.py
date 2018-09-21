#!/usr/bin/env python

from lib.dumper import Dumper

f0nt_base = "https://www.f0nt.com/release/"

if __name__ == "__main__":
    dumper = Dumper(f0nt_base)
    count = dumper.get_page_count()
    for page in range(1, count):
        fonts = dumper.get_page_fonts(page)
        for font in fonts:
            dumper.get_font(font)
    dumper.stamp()
