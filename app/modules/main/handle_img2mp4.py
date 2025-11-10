import os
from typing import List, Set

from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

from app.services.csv_manager import CSVManager
from app.ui.img2mp4_widget_iu import Ui_Form


class Img2Mp4Handler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

    def on_browse_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Pilih file CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            self.ui.lineEdit_pathCSV.setText(path)

    def on_scan_csv_into_list(self):
        path = self.ui.lineEdit_pathCSV.text().strip()
        if not path or not os.path.isfile(path):
            QMessageBox.critical(self, "Error", "File CSV tidak ditemukan atau path kosong.")
            return

        try:
            items: Set[str] = set()
            csv_data = CSVManager(path).read_csv()
            for row in csv_data:
                if len(row) < 3:
                    continue
                ep, sq, sh = row[0].strip(), row[1].strip(), row[2].strip()
                if ep and sq and sh:
                    token = f"{ep}_{sq}_{sh}"
                    items.add(token)

            self._populate_scan_list(sorted(items))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membaca CSV:\n{e}")

    def _populate_scan_list(self, items: List[str]):
        self.ui.listView_available.clear()
        for text in items:
            self.ui.listView_available.appendRow(QStandardItem(text))
        self.ui.listView_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_move_selected_from_scan_to_convert(self):
        selected = self.ui.listView_listConvert.selectionModel().selectedIndexes()
        if not selected:
            return

        to_move_texts: List[str] = []
        source_rows = set()
        for proxy_idx in selected:
            src_idx = self.ui.lineEdit_availableSearch.mapToSource(proxy_idx)
            source_rows.add(src_idx.row())
            text = self.ui.listView_available.item(src_idx.row()).text()
            to_move_texts.append(text)

        existing = {self.ui.listView_listConvert.item(i).text() for i in range(self.ui.listView_listConvert.rowCount())}
        for t in to_move_texts:
            if t not in existing:
                self.ui.listView_listConvert.appendRow(QStandardItem(t))

        for row in sorted(source_rows, reverse=True):
            self.ui.listView_available.removeRow(row)

        self.ui.listView_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_delete_in_convert(self):
        selected = self.ui.listView_listConvert.selectionModel().selectedIndexes()
        if not selected:
            return

        texts = sorted({self.ui.listView_listConvert.item(idx.row()).text() for idx in selected})
        for idx in sorted({i.row() for i in selected}, reverse=True):
            self.ui.listView_listConvert.removeRow(idx)

        existing_scan = {self.ui.listView_available.item(i).text() for i in range(self.ui.listView_available.rowCount())}
        for t in texts:
            if t not in existing_scan:
                self.ui.listView_available.appendRow(QStandardItem(t))
        self.ui.listView_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_clear_convert_list(self):
        all_texts = [self.ui.listView_listConvert.item(i).text() for i in range(self.ui.listView_listConvert.rowCount())]
        self.ui.listView_listConvert.clear()

        existing_scan = {self.ui.listView_available.item(i).text() for i in range(self.ui.listView_available.rowCount())}
        for t in all_texts:
            if t not in existing_scan:
                self.ui.listView_available.appendRow(QStandardItem(t))
        self.ui.listView_available.sort(0, Qt.SortOrder.AscendingOrder)

