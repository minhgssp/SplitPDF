import tkinter as tk
from tkinter import ttk, messagebox
import fitz
from PIL import Image, ImageTk
import os
import sqlite3

class PDFReader:
    def __init__(self, master, pdf_dir):
        self.master = master
        self.pdf_dir = pdf_dir

        self.pdf_document = None
        self.current_page = 0
        self.bookmarks = {}
        self.bookmark_mode = False
        self.view_mode = True

        self.bookmark_changed_callback = None

        self.setup_ui()
        self.setup_database()

    def setup_ui(self):
        self.main_frame = tk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # File tree section
        self.file_frame = tk.Frame(self.main_frame, width=200)
        self.main_frame.add(self.file_frame)

        self.file_tree = ttk.Treeview(self.file_frame)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind('<<TreeviewSelect>>', self.on_file_select)

        # PDF viewer section
        self.pdf_frame = tk.Frame(self.main_frame)
        self.main_frame.add(self.pdf_frame)

        self.canvas_frame = tk.Frame(self.pdf_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvases = []
        for i in range(4):
            canvas = tk.Canvas(self.canvas_frame)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            canvas.bind("<Button-1>", lambda e, i=i: self.on_canvas_click(e, i))
            self.canvases.append(canvas)

        # Bookmark tree
        self.bookmark_frame = tk.Frame(self.pdf_frame)
        self.bookmark_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.bookmark_tree = ttk.Treeview(self.bookmark_frame, columns=("Page"), show="headings")
        self.bookmark_tree.heading("Page", text="Page")
        self.bookmark_tree.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_prev = tk.Button(self.button_frame, text="Previous", command=self.prev_page, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT)

        self.btn_next = tk.Button(self.button_frame, text="Next", command=self.next_page, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT)

        self.btn_bookmark = tk.Button(self.button_frame, text="Bookmark", command=self.toggle_bookmark_mode)
        self.btn_bookmark.pack(side=tk.LEFT)

        self.btn_remove_bookmark = tk.Button(self.button_frame, text="Remove Bookmark", command=self.remove_bookmark)
        self.btn_remove_bookmark.pack(side=tk.LEFT)

        self.btn_delete_file = tk.Button(self.button_frame, text="Delete File", command=self.delete_file)
        self.btn_delete_file.pack(side=tk.LEFT)

        self.page_label = tk.Label(self.button_frame, text="Pages: 0-0 / 0")
        self.page_label.pack(side=tk.RIGHT)

        self.update_file_tree()

    def setup_database(self):
        self.conn = sqlite3.connect('bookmarks.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks
            (filename TEXT, page INTEGER, PRIMARY KEY (filename, page))
        ''')
        self.conn.commit()

    def update_file_tree(self):
        self.file_tree.delete(*self.file_tree.get_children())
        for root, dirs, files in os.walk(self.pdf_dir):
            parent = ''
            if root != self.pdf_dir:
                parent = os.path.relpath(os.path.dirname(root), self.pdf_dir)
            for file in sorted(files):
                if file.endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.pdf_dir)
                    
                    # Check if the file is a split file
                    if "_split_" in file:
                        parent_file = file.split("_split_")[0] + ".pdf"
                        parent_path = os.path.join(os.path.dirname(relative_path), parent_file)
                        
                        # If parent doesn't exist in the tree, add it
                        if not self.file_tree.exists(parent_path):
                            self.file_tree.insert('', 'end', parent_path, text=parent_file, open=True)
                        
                        # Insert the split file as a child of its parent
                        self.file_tree.insert(parent_path, 'end', relative_path, text=file)
                    else:
                        # Insert non-split files at the root level
                        self.file_tree.insert('', 'end', relative_path, text=file, open=True)

    def on_file_select(self, event):
        selection = self.file_tree.selection()
        if selection:
            file_path = os.path.join(self.pdf_dir, selection[0])
            self.open_pdf(file_path)

    def open_pdf(self, file_path):
        self.pdf_document = fitz.open(file_path)
        self.current_page = 0
        self.bookmarks = self.load_bookmarks(os.path.basename(file_path))
        self.show_pages()
        self.btn_prev.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)
        self.update_page_label()
        self.update_bookmark_tree()

    def load_bookmarks(self, filename):
        self.cursor.execute("SELECT page FROM bookmarks WHERE filename=?", (filename,))
        return {row[0] for row in self.cursor.fetchall()}

    def save_bookmark(self, filename, page):
        self.cursor.execute("INSERT OR IGNORE INTO bookmarks (filename, page) VALUES (?, ?)", (filename, page))
        self.conn.commit()

    def remove_bookmark_from_db(self, filename, page):
        self.cursor.execute("DELETE FROM bookmarks WHERE filename=? AND page=?", (filename, page))
        self.conn.commit()

    def show_pages(self):
        if self.pdf_document:
            for i in range(4):
                page_num = self.current_page + i
                if page_num < len(self.pdf_document):
                    page = self.pdf_document[page_num]
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    photo = ImageTk.PhotoImage(img)
                    self.canvases[i].delete("all")
                    self.canvases[i].create_image(0, 0, anchor=tk.NW, image=photo)
                    self.canvases[i].image = photo
                    self.draw_bookmarks(i)
                else:
                    self.canvases[i].delete("all")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 4
            if self.current_page < 0:
                self.current_page = 0
            self.show_pages()
            self.update_page_label()

    def next_page(self):
        if self.current_page + 4 < len(self.pdf_document):
            self.current_page += 4
            self.show_pages()
            self.update_page_label()

    def update_page_label(self):
        end_page = min(self.current_page + 3, len(self.pdf_document) - 1)
        self.page_label.config(text=f"Pages: {self.current_page + 1}-{end_page + 1} / {len(self.pdf_document)}")

    def toggle_bookmark_mode(self):
        self.bookmark_mode = not self.bookmark_mode
        if self.bookmark_mode:
            self.btn_bookmark.config(relief=tk.SUNKEN)
        else:
            self.btn_bookmark.config(relief=tk.RAISED)

    def on_canvas_click(self, event, canvas_index):
        if self.bookmark_mode and self.pdf_document:
            page_num = self.current_page + canvas_index
            if page_num not in self.bookmarks:
                self.bookmarks.add(page_num)
                self.save_bookmark(os.path.basename(self.pdf_document.name), page_num)
                self.draw_bookmarks(canvas_index)
                self.update_bookmark_tree()
                if self.bookmark_changed_callback:
                    self.bookmark_changed_callback()

    def draw_bookmarks(self, canvas_index):
        page_num = self.current_page + canvas_index
        if page_num in self.bookmarks:
            self.canvases[canvas_index].create_rectangle(
                0, 0, 20, 20,
                outline="red", fill="red"
            )

    def update_bookmark_tree(self):
        self.bookmark_tree.delete(*self.bookmark_tree.get_children())
        for page_num in sorted(self.bookmarks):
            self.bookmark_tree.insert("", "end", values=(f"Page {page_num + 1}",))

    def remove_bookmark(self):
        selection = self.bookmark_tree.selection()
        if selection:
            item = self.bookmark_tree.item(selection[0])
            page_str = item['values'][0]
            page_num = int(page_str.split()[1]) - 1
            self.bookmarks.remove(page_num)
            self.remove_bookmark_from_db(os.path.basename(self.pdf_document.name), page_num)
            self.update_bookmark_tree()
            self.show_pages()
            if self.bookmark_changed_callback:
                self.bookmark_changed_callback()

    def delete_file(self):
        selection = self.file_tree.selection()
        if selection:
            file_path = os.path.join(self.pdf_dir, selection[0])
            self.file_tree.delete(selection[0])
            if self.pdf_document and self.pdf_document.name == file_path:
                self.pdf_document = None
                self.current_page = 0
                self.bookmarks = set()
                self.show_pages()
                self.btn_prev.config(state=tk.DISABLED)
                self.btn_next.config(state=tk.DISABLED)
                self.update_page_label()
                self.update_bookmark_tree()
                

    def get_bookmarks(self):
        return self.bookmarks