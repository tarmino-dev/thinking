from math import ceil
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import os
import zipfile
import datetime
import sys

class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.setWindowTitle("Бекапер базы") # заголовок окна
        self.setGeometry(300, 250, 550, 200) # отступы окна от верхнего левого угла экрана и размеры окна (вправо, вниз, ширина окна, высота окна)

        self.backup_success_text = QtWidgets.QLabel(self)

        self.main_text = QtWidgets.QLabel(self)
        self.main_text.setText("Закройте программу и вставьте флешку")
        self.main_text.move(150, 20)
        self.main_text.adjustSize() # подстроить ширину объекта под его содержимое

        self.btn = QtWidgets.QPushButton(self)
        self.btn.move(150, 50)
        self.btn.setText("Упаковать")
        self.btn.setFixedWidth(250) # вместо метода adjustSize() , который автоматически подстраивает ширину, зададим фиксированную ширину в ручную
        self.btn.clicked.connect(self.pack_base)

        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setGeometry(150, 80, 250, 20)
        self.pbar.setValue(0)
        self.pbar_value = 0

        self.path_to_backup = "/Users/tarmino/Documents/Basa"
        self.path_to_archive = f"/Users/tarmino/Documents/Basa_{self.get_archive_name()}.zip"

    def pack_base(self): # метод, который будет привязан к нажатию на кнопку
        step = self.get_update_pbar_step()
        zf = zipfile.ZipFile(self.path_to_archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9)
        for dirname, subdirs, files in os.walk(self.path_to_backup):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
                self.update_pbar(step)
        zf.close()
        self.backup_success_text.setText("Бекап успешно завершен")
        self.backup_success_text.move(150, 150)
        self.backup_success_text.adjustSize()

    def update_pbar(self, step):
        QApplication.processEvents()
        self.pbar_value += step
        self.pbar.setValue(ceil(self.pbar_value))

    def get_update_pbar_step(self):
        count = 0
        for root_dir, cur_dir, files in os.walk(self.path_to_backup):
            count += len(files)
        step = 100/count
        return step

    @staticmethod
    def get_archive_name():
        return str(datetime.datetime.now()).replace(" ", "T").replace(":", "-")[:19]
        

def application():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_()) # параметры корректного завершения программы


if __name__ == "__main__":
    application()
