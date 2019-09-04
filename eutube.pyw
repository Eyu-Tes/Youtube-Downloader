import os
import sys
import time
from datetime import datetime
import pyperclip
from threading import Thread
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import etubeDGUI_0
import etubeDGUI_1
import video_downloader


class URLandQualityWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window = QMainWindow()
        self.ui = etubeDGUI_0.Ui_MainWindow()
        self.ui.setupUi(self)
        txt = pyperclip.paste()
        if txt.startswith('https://www.youtube.com/watch?v='):
            self.ui.lineEditURL.setText(txt)
        self.ui.pushButtonURL.clicked.connect(self.combobox_thread)
        self.ui.lineEditURL.returnPressed.connect(self.combobox_thread)
        self.ui.comboBoxQuality.currentIndexChanged.connect(self.choose_stream)
        self.ui.pushButtonOk.clicked.connect(self.goto_path_and_progress_window)
        self.ui.pushButtonCancel.clicked.connect(sys.exit)
        self.show()

    def choose_stream(self):
        current_index = self.ui.comboBoxQuality.currentIndex()
        downloader.stream = downloader.streams[int(current_index)]
        # downloader.file_name = downloader.stream.default_filename
        downloader.file_name = downloader.yt.title
        downloader.res = downloader.stream.resolution
        downloader.size = float(downloader.stream.filesize)
        downloader.ext = video_downloader.get_extension(downloader.stream.
                                                        mime_type)

    def combobox_thread(self):
        ct = Thread(target=self.populate_combobox)
        # Daemonic threads are threads that can’t be joined,
        # But They are destroyed automatically when the main thread terminates.
        # sys.exit() wont exit only main thread, it will also stop this thread.
        ct.daemon = True
        ct.start()

    def populate_combobox(self):
        url = self.ui.lineEditURL.text()
        no_streams_txt = 'Unable to fetch streams'
        empty_url_txt = 'Empty URL'
        if url:
            self.ui.labelUrlError.setText('')
            self.ui.labelFetchingQuality.setText('fetching streams ...')
            self.ui.labelFetchingQuality.setVisible(True)

            print('Getting Streams')
            err_txt = downloader.yt_obj(url)
            if downloader.yt:
                downloader.get_streams()
                if downloader.streams:
                    self.ui.labelFetchingQuality.setVisible(False)
                    print('Got Streams')
                    for stream in downloader.streams:
                        res = stream.resolution        # resolution
                        size = float(stream.filesize)  # convert byte to float
                        size_str = f'{size/(1024 ** 2):.2f} MB'.rjust(10)
                        mime = stream.mime_type        # MIME
                        ext = video_downloader.get_extension(mime)   # extension
                        combo_str = f'{ext.ljust(4)}, ' \
                                    f'{res.ljust(5)} ' \
                                    f'{size_str.rjust(10)}'
                        self.ui.comboBoxQuality.addItem(combo_str)
                else:
                    self.ui.labelUrlError.setText(no_streams_txt)
                    self.ui.labelFetchingQuality.setVisible(False)
                    self.ui.comboBoxQuality.clear()
            else:
                self.ui.labelUrlError.setText(err_txt)
                self.ui.labelFetchingQuality.setVisible(False)
                self.ui.comboBoxQuality.clear()
        else:
            self.ui.labelUrlError.setText(empty_url_txt)
            self.ui.labelFetchingQuality.setVisible(False)
            self.ui.comboBoxQuality.clear()

    def goto_path_and_progress_window(self):
        if downloader.stream:
            PathandProgressWindow(self.window)
            self.hide()
        else:
            self.ui.lineEditURL.setFocus()


class PathandProgressWindow(QMainWindow):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.ui = etubeDGUI_1.Ui_MainWindow()
        self.ui.setupUi(parent_window)
        self.file_name = ''
        self.full_path = ''
        self.ui.lineEditPath.setText(downloader.file_name+'.'+downloader.ext)
        size_str = f'{downloader.size/(1024 ** 2):.2f} MB'
        self.ui.labelFileSize.setText(size_str)
        self.ui.pushButtonBrowse.clicked.connect(self.browse_path)
        self.ui.pushButtonControl.clicked.connect(self.download_thread)
        self.ui.pushButtonTerminate.clicked.connect(sys.exit)
        parent_window.show()

    def browse_path(self):
        self.file_name, _ = QFileDialog.getSaveFileName(self, 'Save file',
                                                        downloader.file_name,
                                                        'All files(*)')
        if self.file_name:
            print(self.file_name + '.' + downloader.ext)
            self.ui.lineEditPath.setText(self.file_name + '.' + downloader.ext)

    def download_thread(self):
        dt = Thread(target=self.download_video, daemon=True)
        dt.start()

    def start_progress(self):
        progressbar_thread = MyProgressThread(self, daemon=True)
        progressbar_thread.start()

    def download_video(self):
        if len(self.ui.lineEditPath.text().strip()) == 0:
            self.ui.lineEditPath.setFocus()
        else:
            if self.file_name:
                folder_name = os.path.dirname(self.file_name)
                file_name = os.path.basename(self.file_name)
            else:
                self.file_name = self.ui.lineEditPath.text().rstrip(
                    f'.{downloader.ext}')
                folder_name = os.path.dirname(self.file_name)
                file_name = os.path.basename(self.file_name)
                file_name = video_downloader.safe_filename(file_name)
                self.file_name = os.path.join(folder_name, file_name)
            self.full_path = self.file_name + '.' + downloader.ext
            if os.path.exists(self.full_path):
                self.ui.labelETA.setText('File Already Exists!')
                self.ui.labelETA.setStyleSheet("color: #f44336;")
            else:
                self.ui.labelETA.setText('_')
                self.ui.labelETA.setStyleSheet("color: #000;")
                self.start_progress()
                downloader.start_download(folder=folder_name, file=file_name)


class MyProgressThread(Thread):
    def __init__(self, parent=None, daemon=None):
        super().__init__(daemon=daemon)
        self.parent = parent

    def run(self):
        self.parent.ui.pushButtonControl.setEnabled(False)
        start_time = datetime.now()
        counter = 0
        destination_size = downloader.size
        while counter < 100:
            time.sleep(0.5)
            try:
                current_size = os.stat(self.parent.full_path).st_size
            except (FileNotFoundError, ZeroDivisionError) as err:
                print(err)
            else:
                counter = min(int((current_size / destination_size) * 100), 100)
                self.parent.ui.progressBar.setValue(counter)

                # remaining_size = destination_size - current_size
                # current_time = datetime.now()
                # time_elapsed = current_time - start_time
                # time_elapsed_sec = time_elapsed.total_seconds()
                # try:
                #     eta = (time_elapsed_sec * remaining_size) / current_size
                #     if eta < 60:
                #         # eta_lbl = f'{eta:.1f} seconds'
                #         eta_lbl = f'{round(eta)} sec'
                #     elif eta < 3600:
                #         # eta_lbl = f'{(eta/60):.1f} minutes'
                #         m = eta / 60
                #         s = (m - int(m)) * 60
                #         eta_lbl = f'{int(m)} min, {int(s)} sec'
                #     elif eta < 86_400:
                #         # eta_lbl = f'{(eta/3600):.1f} hours'
                #         h = eta / 3600
                #         m = (h - int(h)) * 60
                #         eta_lbl = f'{int(h)} hour(s), {int(m)} min'
                #     elif eta < 2_592_000:
                #         # eta_lbl = f'{(eta/86_400):.1f} days'
                #         d = eta / 86_400
                #         h = (d - int(d)) * 24
                #         eta_lbl = f'{int(d)} day(s) {int(h)} hour(s)'
                #     else:
                #         eta_lbl = ' ... '
                # except ZeroDivisionError:
                #     eta_lbl = ' _ '
                # self.parent.ui.labelETA.setText(eta_lbl)
        self.parent.ui.progressBar.hide()
        self.parent.ui.labelETA.setText('Download done!')
        self.parent.ui.pushButtonTerminate.setText('Close')
        self.parent.ui.pushButtonControl.setEnabled(True)


def exit_app():
    sys.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloader = video_downloader.MyUtubeDownloader()
    url_and_quality_window = URLandQualityWindow()
    sys.exit(app.exec_())
