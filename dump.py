#!/usr/bin/env python3

from lib.dumper import Dumper

f0nt_base = "https://www.f0nt.com/release"

if __name__ == "__main__":
    print("Backing up fonts ...")
    dumper = Dumper(f0nt_base)
    count = dumper.get_page_count()
    print("> {} page(s) found ...".format(count))
    for page in range(1, count):
        fonts = dumper.get_page_fonts(page)
        print("> {} font(s) found ...".format(len(fonts)))
        for font in fonts:
            dumper.get_font(font)
    dumper.stamp()
