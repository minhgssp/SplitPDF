import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import PyPDF2
import pandas as pd
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import re
import json

SECTION_BREAK = "<<<SECTION_BREAK>>>"

def clean_text_for_excel(text):
    # Loại bỏ ký tự điều khiển ngoại trừ \n và \t
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    
    # Thay thế các ký tự Unicode không hợp lệ bằng '?'
    text = text.encode('ascii', 'replace').decode('ascii')
    
    # Xử lý ký tự '=' ở đầu ô
    text = re.sub(r'(?m)^=', "'=", text)
    
    # Loại bỏ các ký tự không in được
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    return text

class PDFManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Manager")
        self.master.state('zoomed')  # Start maximized

        self.pdf_dir = ""
        self.selected_files = []
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_content = {}
        self.quick_edit_mode = tk.BooleanVar()
        self.clean_text_var = tk.BooleanVar()
        self.clean_text_var.set(True)  # Mặc định là làm sạch văn bản

        # Create Data directory if it doesn't exist
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.setup_ui()
        self.bind_events()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for file tree
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # File tree
        self.file_tree = ttk.Treeview(left_frame)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        self.file_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right frame for PDF viewer and text editor
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # PDF viewer
        self.pdf_canvas = tk.Canvas(right_frame, bg="white")
        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Text editor
        self.text_editor = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.text_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bottom frame for buttons
        bottom_frame = ttk.Frame(self.master)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        # Buttons
        ttk.Button(bottom_frame, text="Select PDF File", command=self.select_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Export to Excel", command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Delete Selected File", command=self.delete_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Break Section", command=self.break_section).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Save Session", command=self.save_session).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="Load Session", command=self.load_session).pack(side=tk.LEFT, padx=5)

        # Quick Edit Mode checkbox
        self.quick_edit_checkbox = ttk.Checkbutton(bottom_frame, text="Quick Edit Mode", variable=self.quick_edit_mode)
        self.quick_edit_checkbox.pack(side=tk.LEFT, padx=5)

        # Clean Text checkbox
        ttk.Checkbutton(bottom_frame, text="Clean Text", variable=self.clean_text_var).pack(side=tk.LEFT, padx=5)

    def bind_events(self):
        self.text_editor.bind("<<Modified>>", self.on_text_modified)
        self.text_editor.bind('<Key>', self.on_key_press)
        self.text_editor.bind('<Shift_L>', self.on_shift_press)
        self.text_editor.bind('<Shift_R>', self.on_shift_press)
        
        # Bind mouse events for PDF navigation
        self.pdf_canvas.bind("<Button-1>", self.on_pdf_click)
        self.pdf_canvas.bind("<MouseWheel>", self.on_mouse_wheel)

    def on_pdf_click(self, event):
        if self.current_pdf:
            self.next_page()

    def on_mouse_wheel(self, event):
        if self.current_pdf:
            if event.delta > 0:
                self.previous_page()
            else:
                self.next_page()

    def on_key_press(self, event):
        if self.quick_edit_mode.get():
            if event.keysym in ['Return', 'Delete', 'BackSpace', 'space']:
                if event.keysym == 'Delete':
                    self.text_editor.delete("insert", "insert+1c")
                elif event.keysym == 'BackSpace':
                    self.text_editor.delete("insert-1c", "insert")
                # Allow 'Return' (Enter) and 'space' to work normally
            else:
                return 'break'  # Prevent default behavior for other keys

    def on_shift_press(self, event):
        if self.quick_edit_mode.get():
            self.break_section()
            return 'break'  # Prevent default behavior of Shift key

    def on_text_modified(self, event):
        if self.text_editor.edit_modified():
            self.update_pdf_content()
            self.text_editor.edit_modified(False)

    def update_pdf_content(self):
        if self.current_pdf and self.current_pdf in self.pdf_content:
            current_text = self.text_editor.get(1.0, tk.END).strip()
            self.pdf_content[self.current_pdf][self.current_page] = current_text

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.current_pdf = file_path
            self.pdf_dir = os.path.dirname(file_path)
            self.update_file_tree(file_path)
            self.current_page = 0
            self.display_pdf(file_path)

    def update_file_tree(self, selected_file):
        self.file_tree.delete(*self.file_tree.get_children())
        
        def sort_key(file):
            match = re.search(r'split_(\d+)_(\d+)', file)
            if match:
                return int(match.group(1)), int(match.group(2))
            return (0, 0)  # For non-split files or files that don't match the pattern
        
        base_name = os.path.basename(selected_file)
        base_name_without_ext = os.path.splitext(base_name)[0]
        
        files_to_display = [f for f in os.listdir(self.pdf_dir) if f.startswith(base_name_without_ext) and f.endswith('.pdf')]
        sorted_files = sorted(files_to_display, key=sort_key)
        
        for file in sorted_files:
            file_path = os.path.join(self.pdf_dir, file)
            if "_split_" in file:
                parent_file = base_name
                parent_id = parent_file  # Use the filename as the ID
                
                if not self.file_tree.exists(parent_id):
                    self.file_tree.insert('', 'end', parent_id, text=parent_file, open=True)
                
                self.file_tree.insert(parent_id, 'end', file, text=file)
            else:
                self.file_tree.insert('', 'end', file, text=file, open=True)
        
        # Select the initially selected file
        self.file_tree.selection_set(base_name)

    def on_tree_select(self, event):
        selected_items = self.file_tree.selection()
        self.selected_files = [os.path.join(self.pdf_dir, self.file_tree.item(item)["text"]) for item in selected_items]
        
        if len(self.selected_files) == 1:
            if self.current_pdf:
                self.update_pdf_content()  # Save changes before switching files
            self.current_pdf = self.selected_files[0]
            self.current_page = 0
            self.display_pdf(self.current_pdf)

    def display_pdf(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
        if pdf_path not in self.pdf_content:
            self.load_pdf_content(pdf_path)
        self.show_current_page()

    def show_current_page(self):
        if 0 <= self.current_page < self.total_pages:
            page = self.doc.load_page(self.current_page)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Scale the image to fit the canvas
            canvas_width = self.pdf_canvas.winfo_width()
            canvas_height = self.pdf_canvas.winfo_height()
            img.thumbnail((canvas_width, canvas_height), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(image=img)
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(canvas_width//2, canvas_height//2, anchor=tk.CENTER, image=photo)
            self.pdf_canvas.image = photo  # Keep a reference
            
            # Update text editor with current page content
            self.update_text_editor()

    def load_pdf_content(self, pdf_path):
        if pdf_path not in self.pdf_content:
            reader = PyPDF2.PdfReader(pdf_path)
            content = []
            for page in reader.pages:
                content.append(page.extract_text())
            self.pdf_content[pdf_path] = content

    def update_text_editor(self):
        if self.current_pdf in self.pdf_content:
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(tk.END, self.pdf_content[self.current_pdf][self.current_page])
            self.text_editor.edit_modified(False)  # Reset the modified flag

    def break_section(self):
        cursor_position = self.text_editor.index(tk.INSERT)
        self.text_editor.insert(cursor_position, SECTION_BREAK)
        self.update_pdf_content()  # Save changes after adding section break

    def export_to_excel(self):
        data = []
        for pdf_file in self.selected_files:
            if pdf_file in self.pdf_content:
                content = "\n".join(self.pdf_content[pdf_file])
                sections = content.split(SECTION_BREAK)
                for section in sections:
                    if self.clean_text_var.get():
                        cleaned_section = clean_text_for_excel(section.strip())
                    else:
                        cleaned_section = section.strip()
                    data.append({"File": os.path.basename(pdf_file), "Content": cleaned_section})
        
        if data:
            df = pd.DataFrame(data)
            excel_file = filedialog.asksaveasfilename(defaultextension=".xlsx")
            if excel_file:
                try:
                    df.to_excel(excel_file, index=False, engine='openpyxl')
                    messagebox.showinfo("Export Complete", f"Data exported to {excel_file}")
                except Exception as e:
                    messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")
        else:
            messagebox.showwarning("No Data", "No content found for the selected PDFs.")

    def delete_file(self):
        if not self.selected_files:
            messagebox.showwarning("No Selection", "Please select a file to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected file(s)?"):
            for file_path in self.selected_files:
                try:
                    os.remove(file_path)
                    self.file_tree.delete(os.path.basename(file_path))
                    if file_path in self.pdf_content:
                        del self.pdf_content[file_path]
                except Exception as e:
                    messagebox.showerror("Delete Error", f"Error deleting {file_path}: {str(e)}")
            
            self.selected_files = []
            messagebox.showinfo("Delete Complete", "Selected file(s) have been deleted.")
            
            # If we deleted the current PDF, clear the display
            if not os.path.exists(self.current_pdf):
                self.current_pdf = None
                self.pdf_canvas.delete("all")
                self.text_editor.delete(1.0, tk.END)

    def previous_page(self):
        if self.current_page > 0:
            self.update_pdf_content()  # Save changes before switching pages
            self.current_page -= 1
            self.show_current_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.update_pdf_content()  # Save changes before switching pages
            self.current_page += 1
            self.show_current_page()

    def save_session(self):
        session_data = {
            "pdf_dir": self.pdf_dir,
            "selected_files": self.selected_files,
            "current_pdf": self.current_pdf,
            "current_page": self.current_page,
            "pdf_content": self.pdf_content
        }
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=self.data_dir
        )
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(session_data, f)
            messagebox.showinfo("Session Saved", f"Current session has been saved to {file_path}")

    def load_session(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir=self.data_dir
        )
        if file_path:
            with open(file_path, 'r') as f:
                session_data = json.load(f)
            
            self.pdf_dir = session_data["pdf_dir"]
            self.selected_files = session_data["selected_files"]
            self.current_pdf = session_data["current_pdf"]
            self.current_page = session_data["current_page"]
            self.pdf_content = session_data["pdf_content"]

            if self.current_pdf:
                self.update_file_tree(self.current_pdf)
                self.display_pdf(self.current_pdf)
            
            messagebox.showinfo("Session Loaded", f"Session has been loaded from {file_path}")

# Đoạn code này nên nằm ngoài class PDFManagerApp
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFManagerApp(root)
    root.mainloop()