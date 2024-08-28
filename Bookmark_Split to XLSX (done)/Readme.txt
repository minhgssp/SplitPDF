# PDF Reader Application

## Overview
This PDF Reader Application is a Python-based desktop application that allows users to view PDF files, bookmark pages, and export content between bookmarks to an Excel file. It provides a user-friendly interface for navigating through PDF documents and managing bookmarks efficiently.

## Features
1. **PDF Viewing**: Load and display PDF files with a three-page view.
2. **Navigation**: Easily move between pages using 'Previous' and 'Next' buttons.
3. **Bookmarking**: Add or remove bookmarks by clicking on pages.
4. **Bookmark Management**: View a list of bookmarked pages and delete bookmarks as needed.
5. **Content Export**: Export text content between bookmarks to an Excel file.

## Requirements
- Python 3.6+
- PyQt5
- PyMuPDF (fitz)
- openpyxl

## Installation
1. Ensure you have Python installed on your system.
2. Install the required libraries:
   ```
   pip install PyQt5 PyMuPDF openpyxl
   ```
3. Download the PDF Reader Application script.

## Usage

### Starting the Application
Run the script using Python:
```
python pdf_reader_app.py
```

### Loading a PDF
1. Click the 'Load PDF' button.
2. Select a PDF file from your file system.

### Navigating the PDF
- Use the 'Previous' and 'Next' buttons to move between pages.
- The application displays three pages at a time for easy viewing.

### Bookmarking Pages
1. Click the 'Toggle Bookmark Mode' button to enter bookmark mode.
2. Click on a displayed page to add or remove it from bookmarks.
3. The bookmark mode status is shown on the button (ON/OFF).

### Managing Bookmarks
- Bookmarked pages are listed in the right panel.
- To remove a bookmark:
  1. Select the bookmark in the list.
  2. Click the 'Delete Selected Bookmark' button.

### Exporting Content
1. Add bookmarks to the desired pages.
2. Click the 'Export XLSX' button.
3. Choose a location to save the Excel file.
4. The application will export the text content between each set of bookmarks to the Excel file.

## Tips
- Resize the application window to adjust the view of PDF pages.
- The application automatically scales pages to fit the available space.
- Use bookmark mode to easily add or remove bookmarks without affecting navigation.

## Troubleshooting
- If the PDF doesn't load, ensure it's not corrupted and you have the necessary permissions to read the file.
- For export issues, check that you have write permissions in the selected directory.
