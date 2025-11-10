import os
import asyncio
from typing import List, Set

from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QAbstractItemView, QListView
from PyQt6.QtCore import Qt, QSortFilterProxyModel

from app.services.csv_manager import CSVManager
from app.services.ffmpeg_manager import FFMPEGManager
from app.services.file_manager import FileManager
from app.ui.img2mp4_widget_iu import Ui_Form
from app.config.img2mp4 import Data as img2mp4_data


class Img2Mp4Handler(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Models
        self.model_available = QStandardItemModel(self)
        self.model_convert = QStandardItemModel(self)
        self.ui.listView_available.setModel(self.model_available)
        self.ui.listView_listConvert.setModel(self.model_convert)

        # Proxy scan
        self.proxyScan = QSortFilterProxyModel(self.ui.listView_available)
        self.proxyScan.setSourceModel(self.model_available)
        self.proxyScan.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxyScan.setFilterKeyColumn(0)
        self.ui.listView_available.setModel(self.proxyScan)
        self.ui.lineEdit_availableSearch.textChanged.connect(self.proxyScan.setFilterFixedString)

        # List view
        self.ui.listView_available.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.ui.listView_available.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ui.listView_listConvert.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.ui.listView_listConvert.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        # Buttons
        self.ui.pushButton_locateCSV.clicked.connect(self.on_browse_csv)
        self.ui.pushButton_scan.clicked.connect(self.on_scan_csv_into_list)
        self.ui.pushButton_addFile.clicked.connect(self.on_move_selected_from_scan_to_convert)
        self.ui.pushButton_clearFile.clicked.connect(self.on_clear_convert_list)
        self.ui.pushButton_convert.clicked.connect(self.on_convert_all_in_convert_list)

        # Combobox data
        for project in img2mp4_data.project_list:
            self.ui.comboBox_projectLetter.addItem(project[0])
        self.ui.comboBox_projectType.addItems(img2mp4_data.project_types)

        # Spinbox value
        self.ui.spinBox_qualityLevel.setMinimum(1)
        self.ui.spinBox_qualityLevel.setMaximum(31)
        self.ui.spinBox_qualityLevel.setValue(15)

        # Other
        self.enable_drag_drop_lineedits()

    def enable_drag_drop_lineedits(self):
        self.ui.lineEdit_pathCSV.setAcceptDrops(True)

        def handle_drag_enter(event):
            if event.mimeData().hasUrls():
                for url in event.mimeData().urls():
                    if url.isLocalFile() and url.toLocalFile().lower().endswith(".csv"):
                        event.acceptProposedAction()
                        return
            event.ignore()

        def handle_drop(event):
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".csv"):
                    self.ui.lineEdit_pathCSV.setText(url.toLocalFile())
                    event.acceptProposedAction()
                    return
            event.ignore()

        # tempelkan event handler langsung ke widget aslinya
        self.ui.lineEdit_pathCSV.dragEnterEvent = handle_drag_enter
        self.ui.lineEdit_pathCSV.dropEvent = handle_drop

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
            csv_data = CSVManager(path).read_csv(skip_header=True)
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
        self.model_available.clear()
        for text in items:
            self.model_available.appendRow(QStandardItem(text))
        self.model_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_move_selected_from_scan_to_convert(self):
        selected = self.ui.listView_available.selectionModel().selectedIndexes()
        if not selected:
            return

        to_move_texts: List[str] = []
        source_rows = set()
        for proxy_idx in selected:
            src_idx = self.proxyScan.mapToSource(proxy_idx)
            source_rows.add(src_idx.row())
            text = self.model_available.item(src_idx.row()).text()
            to_move_texts.append(text)

        existing = {self.model_convert.item(i).text() for i in range(self.model_convert.rowCount())}
        for t in to_move_texts:
            if t not in existing:
                self.model_convert.appendRow(QStandardItem(t))

        for row in sorted(source_rows, reverse=True):
            self.model_available.removeRow(row)

        self.model_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_delete_in_convert(self):
        selected = self.ui.listView_listConvert.selectionModel().selectedIndexes()
        if not selected:
            return

        texts = sorted({self.model_convert.item(idx.row()).text() for idx in selected})
        for idx in sorted({i.row() for i in selected}, reverse=True):
            self.ui.listView_listConvert.removeRow(idx)

        existing_scan = {self.model_available.item(i).text() for i in
                         range(self.ui.listView_available.rowCount())}
        for t in texts:
            if t not in existing_scan:
                self.model_available.appendRow(QStandardItem(t))
        self.model_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_clear_convert_list(self):
        all_texts = [self.model_convert.item(i).text() for i in
                     range(self.model_convert.rowCount())]
        self.model_convert.clear()

        existing_scan = {self.model_available.item(i).text() for i in
                         range(self.model_available.rowCount())}
        for t in all_texts:
            if t not in existing_scan:
                self.model_available.appendRow(QStandardItem(t))
        self.model_available.sort(0, Qt.SortOrder.AscendingOrder)

    def on_convert_all_in_convert_list(self):
        row_count = self.model_convert.rowCount()
        if row_count == 0:
            QMessageBox.information(self, "Info", "Tidak ada item di daftar konversi.")
            return

        try:
            quality = int(self.ui.spinBox_qualityLevel.value())
        except Exception:
            quality = 15

        failed: List[str] = []

        # Ambil pilihan project
        project = self.ui.comboBox_projectLetter.currentText().upper() if self.ui.comboBox_projectLetter else "RIMBA"
        tipe = self.ui.comboBox_projectType.currentText().upper() if self.ui.comboBox_projectType else "VFX"

        for i in range(row_count):
            token = self.model_convert.item(i).text()
            try:
                parts = token.split("_")

                if len(parts) == 3:
                    ep, sq, sh = parts
                elif len(parts) == 4:
                    ep, sq, a, sh = parts
                    sq = f"{sq}_{a}"
                else:
                    raise ValueError(f"Invalid token format: {token}")

            except ValueError:
                failed.append(f"{token} (format tidak valid)")
                continue

            input_seq, output_file = FileManager().img2mp4_build_paths(ep=ep, sq=sq, sh=sh, project=project, tipe=tipe)
            output_folder = os.path.dirname(output_file)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder, exist_ok=True)
                print(f"Created folder: {output_folder}")

            try:
                asyncio.run(FFMPEGManager().img_to_mp4(input_sequence=input_seq, output_file=output_file, quality=quality))
            except Exception as e:
                failed.append(f"{token} -> {e}")

        if failed:
            msg = "Beberapa konversi gagal:\n\n" + "\n".join(failed)
            QMessageBox.critical(self, "Selesai dengan error", msg)
        else:
            QMessageBox.information(self, "Selesai", "Semua item berhasil dikonversi.")