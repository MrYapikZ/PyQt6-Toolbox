from PyQt6.QtWidgets import QWidget

from app.ui.img2mp4_widget_iu import Ui_Form


class Img2Mp4Handler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)