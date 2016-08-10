import requests
import re
import os
import urlparse
import zipfile
import shutil
from datetime import datetime

class Dumper():
    def __init__(self, base):
        self.base = base

    def get_page_count(self):
        url = self.base
        r = requests.head(url, allow_redirects=True)
        content = requests.get(r.url)
        result = re.search("<a class=\"last\" href=\"http:\/\/www\.f0nt\.com\/release\/page\/(\d+)\/\">", content.text)
        if result:
            return int(result.group(1))
        else:
            return 0

    def get_page_fonts(self, page_no):
        print "Open page " + str(page_no)
        url = self.base + 'page/' + str(page_no)
        r = requests.head(url, allow_redirects=True)
        content = requests.get(r.url)
        result = re.findall("<a href=\"http:\/\/www\.f0nt\.com\/release\/([^\/]+)\/\" rel=\"bookmark\">", content.text)
        return result

    def get_font(self, font_name):
        print "Get font " + font_name
        url = self.base + font_name + '/'
        r = requests.head(url, allow_redirects=True)
        content = requests.get(r.url)
        download_pos = content.text.find("<div id=\"download\">")
        if download_pos >= 0:
            trimmed_content = content.text[download_pos + len("<div id=\"download\">"):]
            result = re.search("<a href=\"(http:\/\/www\.f0nt\.com\/[^\"]+)\">", trimmed_content)
            if result:
                font_url = result.group(1)
                self.download_and_unpack(font_url, font_name)
        else:
            self.err_log("Font " + font_name + " cannot be download. May be it contains external link. Check " + url + " for detail.")

    def err_log(self, txt):
        print txt
        stamp = datetime.now()
        text_file = open("error_log.txt", "w+")
        text_file.write(stamp.strftime("%Y-%m-%d %H:%M:%S") + " - " + txt)
        text_file.close()

    def stamp(self):
        stamp = datetime.now()
        text_file = open("dump_stamp.txt", "w")
        text_file.write("Last dump: " + stamp.strftime("%Y-%m-%d %H:%M:%S"))
        text_file.close()

    def download_and_unpack(self, url, font_name):
        print "Downloading " + url + " ..."
        file_name = os.path.basename(urlparse.urlsplit(url).path)
        headers = {"Referer": "http://www.f0nt.com/release/" + font_name}
        content = requests.get(url, stream=True, headers=headers)
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        with open('tmp/' + file_name, 'wb') as f:
            for chunk in content.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

        if content.headers['Content-Type'] == "application/zip":
            if not os.path.exists('tmp/t'):
                os.makedirs('tmp/t')
            print "Ripping fonts from " + file_name + " ..."
            try:
                zip = zipfile.ZipFile('tmp/' + file_name)
                file_list = zip.namelist()
                file_list = filter(lambda x: (x[-4:].lower() == ".ttf") and (x[:1] != ".") and (x.find("/.") == -1), file_list)
                zip.extractall('tmp/t/')
            except RuntimeError:
                if not os.path.exists('zip'):
                    os.makedirs('zip')
                shutil.copyfile('tmp/' + file_name, 'zip/' + file_name)
                self.err_log("Unable to extract " + file_name + ". See zip/" + file_name + " for detail.")

                shutil.rmtree('tmp/')
                return

            if not os.path.exists('ttf'):
                os.makedirs('ttf')
            for ttf in file_list:
                ttf_name = os.path.basename(ttf)
                shutil.copyfile('tmp/t/' + ttf, 'ttf/' + ttf_name)
        else:
            self.err_log("Font " + font_name + " cannot be download. May be it contains external link. Check " + url + " for detail.")

        shutil.rmtree('tmp/')

        return
