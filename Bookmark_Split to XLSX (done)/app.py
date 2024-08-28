import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QScrollArea, QGridLayout, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize
import fitz  # PyMuPDF
import openpyxl

class PDFReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.pdf_document = None
        self.current_page = 0
        self.bookmarks = set()
        self.bookmark_mode = False

    def initUI(self):
        self.setWindowTitle('PDF Reader')
        self.setGeometry(100, 100, 1400, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel for PDF display
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.load_button = QPushButton('Load PDF')
        self.prev_button = QPushButton('Previous')
        self.next_button = QPushButton('Next')
        self.bookmark_toggle = QPushButton('Toggle Bookmark Mode')
        self.export_button = QPushButton('Export XLSX')

        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.bookmark_toggle)
        button_layout.addWidget(self.export_button)

        left_layout.addLayout(button_layout)

        # PDF display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        left_layout.addWidget(self.scroll_area)

        self.page_labels = [QLabel() for _ in range(3)]
        for i, label in enumerate(self.page_labels):
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(True)
            label.mousePressEvent = lambda event, index=i: self.page_clicked(index)
            self.scroll_layout.addWidget(label, 0, i)

        main_layout.addWidget(left_panel, 4)  # Left panel takes 4/5 of the width

        # Right panel for bookmarks
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        bookmark_label = QLabel("Bookmarks:")
        right_layout.addWidget(bookmark_label)

        self.bookmark_list = QListWidget()
        right_layout.addWidget(self.bookmark_list)

        delete_bookmark_button = QPushButton("Delete Selected Bookmark")
        delete_bookmark_button.clicked.connect(self.delete_selected_bookmark)
        right_layout.addWidget(delete_bookmark_button)

        main_layout.addWidget(right_panel, 1)  # Right panel takes 1/5 of the width

        # Connect buttons to functions
        self.load_button.clicked.connect(self.load_pdf)
        self.prev_button.clicked.connect(self.prev_pages)
        self.next_button.clicked.connect(self.next_pages)
        self.bookmark_toggle.clicked.connect(self.toggle_bookmark_mode)
        self.export_button.clicked.connect(self.export_xlsx)

    def load_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF file", "", "PDF files (*.pdf)")
        if file_name:
            self.pdf_document = fitz.open(file_name)
            self.current_page = 0
            self.update_display()

    def update_display(self):
        if self.pdf_document:
            available_width = self.scroll_area.width() - 30  # Subtract some padding
            max_width_per_page = available_width // 3

            for i in range(3):
                page_num = self.current_page + i
                if page_num < len(self.pdf_document):
                    page = self.pdf_document[page_num]
                    pix = page.get_pixmap()
                    img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(img)
                    
                    # Calculate the scaling factor to fit the width
                    scale_factor = max_width_per_page / pixmap.width()
                    new_height = int(pixmap.height() * scale_factor)
                    
                    scaled_pixmap = pixmap.scaled(max_width_per_page, new_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.page_labels[i].setPixmap(scaled_pixmap)
                    self.page_labels[i].setFixedSize(QSize(max_width_per_page, new_height))
                else:
                    self.page_labels[i].clear()
                    self.page_labels[i].setFixedSize(QSize(max_width_per_page, 1))  # Set minimum height

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def prev_pages(self):
        if self.current_page > 0:
            self.current_page -= 3
            self.update_display()

    def next_pages(self):
        if self.current_page + 3 < len(self.pdf_document):
            self.current_page += 3
            self.update_display()

    def toggle_bookmark_mode(self):
        self.bookmark_mode = not self.bookmark_mode
        self.bookmark_toggle.setText("Bookmark Mode: ON" if self.bookmark_mode else "Bookmark Mode: OFF")

    def page_clicked(self, index):
        if self.bookmark_mode and self.pdf_document:
            page_num = self.current_page + index
            if page_num < len(self.pdf_document):
                if page_num in self.bookmarks:
                    self.bookmarks.remove(page_num)
                else:
                    self.bookmarks.add(page_num)
                self.update_bookmark_list()

    def update_bookmark_list(self):
        self.bookmark_list.clear()
        for page_num in sorted(self.bookmarks):
            self.bookmark_list.addItem(QListWidgetItem(f"Page {page_num + 1}"))

    def delete_selected_bookmark(self):
        selected_items = self.bookmark_list.selectedItems()
        for item in selected_items:
            page_num = int(item.text().split()[1]) - 1
            self.bookmarks.remove(page_num)
        self.update_bookmark_list()

    def export_xlsx(self):
        if not self.pdf_document:
            return

        sorted_bookmarks = sorted(self.bookmarks)
        sections = []

        for i in range(len(sorted_bookmarks)):
            start = sorted_bookmarks[i]
            end = sorted_bookmarks[i+1] if i+1 < len(sorted_bookmarks) else len(self.pdf_document)
            section_text = ""
            for page_num in range(start, end):
                page = self.pdf_document[page_num]
                section_text += page.get_text()
            sections.append(section_text)

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        for i, section in enumerate(sections, start=1):
            sheet.cell(row=i, column=1, value=section)

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel file", "", "Excel files (*.xlsx)")
        if file_name:
            workbook.save(file_name)
            print(f"Exported to {file_name}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFReaderApp()
    ex.show()
    sys.exit(app.exec_())