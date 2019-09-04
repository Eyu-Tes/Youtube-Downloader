from pytube import YouTube, exceptions
from urllib import error
from threading import Thread
import re
import os
import time


class MyUtubeDownloader:

    def __init__(self):
        self.yt = None
        self.streams = []
        self.stream = None
        self.path = ''
        self.file_name = ''
        self.res = ''
        self.ext = ''
        self.size = 0.0

    def progress(self):
        counter = 0
        i = 0
        full_path = os.path.join(self.path, self.file_name)
        print(full_path)
        destination_size = self.size
        while counter < 100:
            time.sleep(1)
            try:
                current_size = os.stat(full_path).st_size
            except (FileNotFoundError, ZeroDivisionError) as err:
                print(err)
            else:
                counter = int((current_size / destination_size) * 100)
                if i < 5:
                    print(f'{counter} %', end='\t')
                    i += 1
                else:
                    i = 0
                    print()
        print(f'{counter} %')

    def start_download(self, folder=None, file=None):
        # self.path = 'C:/Users/Eyoab/Desktop'
        # progressbar_thread = Thread(target=self.progress)
        # progressbar_thread.start()
        print('\nDownload started ...\n')
        # output_path - where u want to save file
        # filename - user defined file name instead of the default
        # self.stream.download(output_path=self.path, filename=None)
        self.stream.download(output_path=folder, filename=file)
        # progressbar_thread.join()
        print('\nDownload done!\n')

    def choose_stream(self):
        while True:
            current_index = input('\nEnter the corresponding number: ')
            try:
                self.stream = self.streams[int(current_index)]
                self.file_name = self.stream.default_filename
                self.res = self.stream.resolution
                self.size = float(self.stream.filesize)
                self.ext = get_extension(self.stream.mime_type)
                break
            except (IndexError, ValueError):
                # IndexError - if user chose stream out of index
                # ValueError - if user entered non numeral character
                print('Choose the correct number.')

    def display_streams(self):
        for n, stream in enumerate(self.streams):
            # file_name = stream.default_filename       # file name + ext
            res = stream.resolution                     # resolution
            size = float(stream.filesize)               # convert byte to float
            mime = stream.mime_type                     # MIME
            ext = get_extension(mime)
            print(f'{n} - {ext} \t\t {res} \t\t {size / (1024 ** 2):.2f} MB')
            print()

    def get_streams(self):
        # progressive - contain the audio and video in a single file.
        self.streams = self.yt.streams.filter(progressive=True).all()

    def yt_obj(self, url):
        error_txt = ''
        try:
            self.yt = YouTube(url)  # Youtube object
        except exceptions.RegexMatchError as err:
            error_txt = 'Wrong youtube url format'
            print(err)  # Wrong url format
        except error.URLError as err:
            error_txt = 'Unable to connect to the youtube url'
            print(err)  # Unable to connect to url
        return error_txt

    def run(self, url):
        print('\neutube downloader\n')
        self.yt_obj(url)
        if self.yt:
            self.get_streams()
            if self.streams:
                self.display_streams()
                self.choose_stream()
                if self.stream:
                    self.start_download()


def safe_filename(filename):
    valid_filename = re.sub(r'[<>:"/\\|?*]', ' ', filename)
    return valid_filename.rstrip()


def get_extension(mime):
    ext = ''
    mo = re.search(r'/(.*)', mime)                  # extract ext from MIME
    if mo:
        try:
            ext = mo.group(1)
        except IndexError:
            pass
    return ext


if __name__ == '__main__':
    path = 'https://www.youtube.com/watch?v=dRRpbDFnMHI'
    downloader = MyUtubeDownloader()
    downloader.run(path)
