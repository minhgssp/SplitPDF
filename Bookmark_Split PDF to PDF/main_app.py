import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from pdf_reader import PDFReader
from pdf_splitter import PDFSplitter

class MainApp:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Processing Tool")
        self.master.state('zoomed')  # Start maximized

        self.base_dir = os.getcwd()
        self.pdf_dir = os.path.join(self.base_dir, "pdf_files")
        
        if not os.path.exists(self.pdf_dir):
            os.makedirs(self.pdf_dir)

        self.pdf_reader = PDFReader(self.master, self.pdf_dir)
        self.setup_ui()

    def setup_ui(self):
        # File management buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_open = tk.Button(self.button_frame, text="Open PDF", command=self.open_pdf)
        self.btn_open.pack(side=tk.LEFT)

        self.btn_split = tk.Button(self.button_frame, text="Split PDF", command=self.split_pdf, state=tk.DISABLED)
        self.btn_split.pack(side=tk.LEFT)

        # Update split button state when bookmarks change
        self.pdf_reader.bookmark_changed_callback = self.update_split_button_state

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            # Copy file to pdf_dir if it's not already there
            if not file_path.startswith(self.pdf_dir):
                new_file_path = os.path.join(self.pdf_dir, self.get_next_filename(os.path.basename(file_path)))
                shutil.copy2(file_path, new_file_path)
                file_path = new_file_path
                self.pdf_reader.update_file_tree()

            self.pdf_reader.open_pdf(file_path)

    def get_next_filename(self, filename):
        name, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(os.path.join(self.pdf_dir, f"{counter:03d}_{name}{ext}")):
            counter += 1
        return f"{counter:03d}_{name}{ext}"

    def update_split_button_state(self):
        if self.pdf_reader.pdf_document and self.pdf_reader.get_bookmarks():
            self.btn_split.config(state=tk.NORMAL)
        else:
            self.btn_split.config(state=tk.DISABLED)

    def split_pdf(self):
        if self.pdf_reader.pdf_document and self.pdf_reader.get_bookmarks():
            pdf_path = self.pdf_reader.pdf_document.name
            splitter = PDFSplitter(pdf_path, self.pdf_dir)
            splitter.split_pdf(self.pdf_reader.get_bookmarks())
            self.pdf_reader.update_file_tree()
            messagebox.showinfo("Split PDF", f"PDF split successfully. Output directory: {self.pdf_dir}")
        else:
            messagebox.showwarning("Split PDF", "Please open a PDF and add bookmarks before splitting.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()