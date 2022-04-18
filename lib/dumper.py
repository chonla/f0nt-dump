import requests
import re
import os
from urllib.parse import urlparse, urlsplit
import zipfile
import shutil
from datetime import datetime


class Dumper():
    def __init__(self, base):
        self.base = base
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            "Referer": "https://www.f0nt.com/release"
        }

    def get_page_count(self):
        print("Retrieving page count ...")
        url = "{}/".format(self.base)
        headers = self.default_headers
        content = requests.get(url, allow_redirects=True, headers = headers)
        result = re.search("<a class=\"last\" aria-label=\"Last Page\" href=\"https:\/\/www\.f0nt\.com\/release\/page\/(\d+)\/\">", content.text)
        if result:
            return int(result.group(1))
        return 0

    def get_page_fonts(self, page_no):
        print("Accessing page {} ...".format(str(page_no)))
        headers = self.default_headers
        url = "{}/page/{}".format(self.base, str(page_no))
        content = requests.get(url, allow_redirects=True, headers = headers)
        result = re.findall(
            "<a href=\"https:\/\/www\.f0nt\.com\/release\/([^\/]+)\/\" rel=\"bookmark\">", content.text)
        return result

    def get_font(self, font_name):
        print("Getting font {} ...".format(font_name))
        headers = self.default_headers
        url = "{}/{}/".format(self.base, font_name)
        content = requests.get(url, allow_redirects=True, headers = headers)
        download_pos = content.text.find("<div id=\"download\">")
        if download_pos >= 0:
            trimmed_content = content.text[download_pos +
                                           len("<div id=\"download\">"):]
            result = re.search(
                "<a href=\"(https:\/\/www\.f0nt\.com\/[^\"]+)\">", trimmed_content)
            if result:
                font_url = result.group(1)
                self.download_and_unpack(font_url, font_name)
        else:
            self.err_log("> Font {} cannot be download. May be it contains external link. Check {} for detail.".format(font_name, url))

    def err_log(self, txt):
        print(txt)
        stamp = datetime.now()
        text_file = open("error_log.txt", "a+")
        text_file.write("{} - {}\n".format(stamp.strftime("%Y-%m-%d %H:%M:%S"), txt))
        text_file.close()

    def stamp(self):
        stamp = datetime.now()
        text_file = open("dump_stamp.txt", "w")
        text_file.write("Last dump: {}".format(stamp.strftime("%Y-%m-%d %H:%M:%S")))
        text_file.close()

    def download_and_unpack(self, url, font_name):
        print("> Downloading {} ...".format(url))
        file_name = os.path.basename(urlsplit(url).path)
        headers = self.default_headers | {"Referer": "https://www.f0nt.com/release/" + font_name}
        content = requests.get(url, stream=True, headers=headers)
        os.makedirs('tmp', exist_ok = True)
        file_list = []
        with open('tmp/' + file_name, 'wb') as f:
            for chunk in content.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        if content.headers['Content-Type'] == "application/zip":
            os.makedirs('tmp/t', exist_ok = True)
            print("Ripping fonts from " + file_name + " ...")
            try:
                zip = zipfile.ZipFile('tmp/' + file_name)
                file_list = zip.namelist()
                file_list = list(filter(lambda x: (x[-4:].lower() == ".ttf") and (x[:1] != ".") and ("/." not in x), file_list))
                zip.extractall('tmp/t/', file_list)
            except (ValueError, RuntimeError):
                os.makedirs('zip', exist_ok = True)
                shutil.copyfile('tmp/' + file_name, 'zip/' + file_name)
                self.err_log("Unable to extract " + file_name +
                             ". See zip/" + file_name + " for detail.")

                shutil.rmtree('tmp/')
                return

            os.makedirs('ttf', exist_ok = True)
            for ttf in file_list:
                ttf_name = os.path.basename(ttf)
                print("> Copying tmp/t/{} to ttf/{}".format(ttf, ttf_name))
                shutil.copyfile('tmp/t/' + ttf, 'ttf/' + ttf_name)
        else:
            self.err_log("Font " + font_name +
                         " cannot be download. May be it contains external link. Check " + url + " for detail.")

        shutil.rmtree('tmp/')

        return
