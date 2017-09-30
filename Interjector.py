import requests
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel

INTERJECT = """\n I’d just like to interject for a moment. What you’re refering to as Linux, is in fact, GNU/Lnux, \
or as I’ve recently taken to calling it, GNU plus Linux. Linux is not an operating system unto itself, but rather \
another free component of a fully functioning GNU system made useful by the GNU corelibs, shell utilities and vital 
system components comprising a full OS as defined by POSIX.\
Many computer users run a modified version of the GNU system every day, without realizing it. Through a peculiar turn \
of events, the version of GNU which is widely used today is often called “Linux”, and many of its users are not aware \
that it is basically the GNU system, developed by the GNU Project.
There really is a Linux, and these people are using it, but it is just a part of the system they use. Linux is the \
kernel: the program in the system that allocates the machine’s resources to the other programs that you run. The kernel\
 is an essential part of an operating system, but useless by itself; it can only function in the context of a complete \
 operating system. Linux is normally used in combination with the GNU operating system: the whole system is basically \
 GNU with Linux added, or GNU/Linux. All the so-called “Linux” distributions are really distributions of GNU/Linux."""

def text_matches(text):
    w1 = "линукс"
    w2 = "linux"
    wn1 = "gnu/linux"
    wn2 = "gnu-linux"
    wn3 = "archlinux"
    if (w1 in text or w2 in text) and wn1 not in text and wn2 not in text and wn3 not in text:
        return True
    else:
        return False


class Interjector(QMainWindow):
    def __init__(self, x, y, width, height, s):
        super().__init__()
        # Graphical variables
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.textField = QLineEdit(self)

        # HTTP variables
        self.s = s
        self.BOARD_NAME = "s"

        self.image_id = 0
        self.messages = []
        self.current_message = ()
        self.search_threads()
        ####################
        self.init_gui()
        ####################

    def init_gui(self):
        self.setGeometry(self.x, self.y, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.setWindowIcon(QIcon('dick.jpg'))
        self.setWindowTitle("The Interjector")

        btn = QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.clicked.connect(self.submit_user_input)
        btn.resize(btn.sizeHint())
        btn.move(220, 250)

        self.textField.move(10, 252)
        self.textField.resize(200, 20)
        self.textField.setText("")

        self.label = QLabel(self)

        self.current_message = self.messages.pop()
        self.load_and_display_captcha()

        self.show()

    def load_and_display_captcha(self):
        self.image_id = \
            self.make_json(
                "https://2ch.hk/api/captcha/2chaptcha/id?board=" + self.BOARD_NAME + "&thread=" + self.current_message[
                    0])[
                "id"]
        image_address = "https://2ch.hk/api/captcha/2chaptcha/image/" + self.image_id

        img = QImage()
        img.loadFromData(self.s.get(image_address).content, "png")

        self.label.setPixmap(QPixmap.fromImage(img))
        self.label.setGeometry(20, 20, 364, 150)

    def make_soup(self, url):
        return BeautifulSoup(self.s.get(url, timeout=None).text, 'html.parser')

    def make_json(self, url):
        return self.s.get(url, timeout=None).json()

    def search_threads(self):
        thread_catalog = self.make_json("https://2ch.hk/" + self.BOARD_NAME + "/threads.json")["threads"]
        thread_catalog = thread_catalog[33:40]
        print("There are currently", len(thread_catalog), "threads on /" + self.BOARD_NAME)
        i = 0

        for t in thread_catalog:
            print("=== SEARCHING THROUGH THREAD " + str(i + 1) + "/" + str(len(thread_catalog)) + " ===")
            self.search_thread_for_linux(t)
            i += 1
        print(self.messages)

    def search_thread_for_linux(self, thread):
        thread_number = thread["num"]
        soup = self.make_soup("https://2ch.hk/" + self.BOARD_NAME + "/res/" + thread_number + ".html")

        messages = soup.find_all("blockquote")

        # TODO: What if quote AND message contain the word?
        for message in messages:
            if text_matches(message.text):  # if it's somewhere in the message
                # (including quotes from previous messages)
                quotes = message.find_all("span", attrs={"class": "unkfunc"})
                if len(quotes) > 0:  # if there are any quotes in the message
                    for quote in quotes:
                        if text_matches(quote.text):  # check every quote
                            break
                    else:  # if not in any of the quotes, must be in the message itself
                        self.messages.append((thread_number, message["id"][1:]))
                else:  # if there are no quotes, the word is in the message
                    self.messages.append((thread_number, message["id"][1:]))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return or e.key() == Qt.Key_Enter:
            self.submit_user_input()

    def closeEvent(self, *args, **kwargs):
        self.s.close()

    def submit_user_input(self):
        print(s.post("https://2ch.hk/makaba/posting.fcgi?json=1",
                     files={"task": (None, "post"), "board": (None, (self.BOARD_NAME)),
                            "thread": (None, str(self.current_message[0])),
                            "captcha_type": (None, "2chaptcha"),
                            "comment": (None, ">>" + str(self.current_message[1]) + INTERJECT),
                            "2chaptcha_id": (None, str(self.image_id)),
                            "2chaptcha_value": (None, str(self.textField.text()))}).json()["Error"])
        print("https://2ch.hk/" + self.BOARD_NAME + "/res/" + self.current_message[0] + ".html#" + self.current_message[1])
        self.textField.clear()
        if len(self.messages) > 0:
            self.current_message = self.messages.pop()
            self.load_and_display_captcha()
        else:
            print("You've run out of messages. (WOW!)")


if __name__ == "__main__":
    s = requests.session()
    app = QApplication(sys.argv)
    interjector = Interjector(500, 600, 400, 300, s)

    sys.exit(app.exec())
