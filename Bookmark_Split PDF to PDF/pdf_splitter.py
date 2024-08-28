import fitz
import os

class PDFSplitter:
    def __init__(self, pdf_path, output_dir):
        self.pdf_document = fitz.open(pdf_path)
        self.output_dir = output_dir

    def split_pdf(self, bookmarks):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        split_points = self.get_split_points(bookmarks)
        
        base_name = os.path.splitext(os.path.basename(self.pdf_document.name))[0]
        
        for i, (start, end) in enumerate(split_points):
            output = fitz.open()
            output.insert_pdf(self.pdf_document, from_page=start, to_page=end)
            output_filename = f"{base_name}_split_{i+1}_{start+1}-{end+1}.pdf"
            output_path = os.path.join(self.output_dir, output_filename)
            output.save(output_path)
            output.close()

        print(f"PDF split into {len(split_points)} files in {self.output_dir}")

    def get_split_points(self, bookmarks):
        split_points = []
        bookmarked_pages = sorted(bookmarks)
        
        if bookmarked_pages[0] > 0:
            split_points.append((0, bookmarked_pages[0] - 1))
        
        for i in range(len(bookmarked_pages)):
            start = bookmarked_pages[i]
            end = bookmarked_pages[i+1] - 1 if i + 1 < len(bookmarked_pages) else len(self.pdf_document) - 1
            split_points.append((start, end))

        return split_points