import time, requests
from threading import Thread
from os import mkdir, remove, rename, path
import tkinter as tk
from urllib.parse import urlparse

def formatsize(size):
    if size >= 1000000000:
        result = size/1000000000
        unit = 'gb'
    elif size >= 1000000:
        result = size/1000000
        unit = 'mb'
    elif size >= 1000:
        result = size/1000
        unit = 'kb'
    else:
        result = size
        unit = 'b'
    return str(round(result)) + ' '+ unit
def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False

def resume(url, filename):
    with open(filename, 'rb') as f:
        locallenth = len(f)
    print(f'Connecting to {url}')
    res = requests.get(url, stream=True)
    print(f'Got response : {res.status_code}\nContent Type : {res.headers["content-type"]}')
    filelenth = res.headers['Content-Length']
    if filelenth == locallenth:
        print('What is wrong with you, attempting to resume downloading a file that has finished downloading???')
    elif locallenth < filelenth:
        header = {"Range": f"bytes={locallenth}-"}
        print(f'Resuming {filename} - {formatsize(filesize)}')
        res = requests.get(url, headers = header,stream=True)
        with open('img.jpg','ab') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if(chunk):
                    f.write(chunk)
class ProgressBar:
    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

class Download:
    def download(self,url, filename):
        local_filename = 'tmp/' + filename
        print(f'Connecting to {url}')
        res = requests.get(url, stream=True)
        print(f'Got response : {res.status_code}\nContent Type : {res.headers["content-type"]}')
        filesize = int(res.headers['Content-Length'])
        f = open(local_filename,'wb')
        f.write(b'')
        f.close()
        f = open(local_filename,'ab')
        i = 0
        l = round(filesize/1024)
        print(f'Downloading {filename} - {formatsize(filesize)}')
        printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 30)
        old = time.time()
        downspeed = ''
        for chunk in res.iter_content(chunk_size=1024):
            if(chunk):
                i += 1
                bar.printProgressBar(i, l, prefix = 'Progress:', suffix = 'Complete', length = 30, printEnd = f'{downspeed} mb/sec\r')
                f.write(chunk)
            if i % 1024 == 0:
                curr = time.time()
                downspeed = round(1/(curr-old),2)
                old = curr

class ThreadedDownload:
    def __init__(self):
        self.connectionCount = 16
        self.path = '/home/eric/Downloads'
        self.isdone = {}
        self.error = False
    def download(self, url):
        self.url = url
        filename = url.split('/')[-1]
        local_filename = self.path + filename
        print(f'Connecting to {url}')
        res = requests.get(url, stream=True)
        print(f'Got response : {res.status_code} {res.reason}\nContent Type : {res.headers["content-type"]}')
        self.filesize = int(res.headers['Content-Length'])
        print(f'Downloading {filename} - {formatsize(self.filesize)}')
        print(f'Preparing to Download file with {self.connectionCount} concurrent threads')
        sizePerThread = round(self.filesize/self.connectionCount)
        self.i = 0
        res.close()
        for i in range(0,self.connectionCount):
            self.isdone[i] = False
            Thread(target = self.downloadThread, args = (sizePerThread, i, filename), daemon = True).start()
        flag = True
        l = self.filesize
        bar = ProgressBar()
        bar.printProgressBar(0, l, prefix = 'Progress:', suffix = f' {formatsize(self.i)} Complete     ', length = 40, printEnd = f'\r')
        i = 0
        while flag:
            i += 1
            time.sleep(0.1)
            if i >= 150:
                i = 0
                if self.i == iold:
                    exit()
            bar.printProgressBar(self.i, l, prefix = 'Progress:', suffix = f' {formatsize(self.i)} Complete     ', length = 40, printEnd = f'\r')

            if self.error == True:
                return Download().download(self.url, filename)

            if self.i == l:
                break

        file = open(f'tmp/{filename}', 'wb')
        file.write(b'')
        file.close()
        file = open(f'tmp/{filename}', 'ab')
        for i in range(0,self.connectionCount):
            f = open(f'tmp/{filename}.{i+1}', 'rb')
            data = f.read()
            file.write(data)
            f.close()
            remove(f'tmp/{filename}.{i+1}')
        file.close()
        try:
            rename(f'tmp/{filename}', f'{path.expanduser("~")}\Downloads\{filename}')
        except FileExistsError:
            remove(f'{path.expanduser("~")}\Downloads\{filename}')
            rename(f'tmp/{filename}', f'{path.expanduser("~")}\Downloads\{filename}')


    def downloadThread(self, size, threadnum, filename):
        try:
            endsize = ((threadnum+1)*size)-1
            if endsize > self.filesize:
                endsize = ''
            header = {"Range": f"bytes={threadnum*size}-{endsize}"}

            res = requests.get(self.url, headers = header,stream=True)

            with open(f'tmp/{filename}.{threadnum+1}','wb') as f:
                for chunk in res.iter_content(chunk_size=1024):
                    if(chunk):
                        self.i += 1024

                        f.write(chunk)
            self.isdone[threadnum] = True
        except requests.exceptions.ContentDecodingError as e:
            print('cannot decode compressed data in threaded mode, using normal download')
            self.error = True



if __name__ == "__main__":
    print('***************************')
    print('Accelerated file downloader')
    print('***************************')
    print('\n\n')
    print('Copy the url of the file that you want to download below : \n')
    url = input()
    ThreadedDownload().download(url)
    print('Finished downloading')
    print('File saved to your downloads folder')

    time.sleep(3)
