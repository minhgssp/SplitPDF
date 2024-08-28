# PDF Manager

PDF Manager là một ứng dụng desktop được phát triển bằng Python, cho phép người dùng xem, chỉnh sửa và quản lý các file PDF một cách hiệu quả.

## Tính năng chính

- Xem và chỉnh sửa nội dung của file PDF
- Chia file PDF thành các phần
- Xuất nội dung PDF sang file Excel
- Chế độ chỉnh sửa nhanh
- Làm sạch văn bản khi xuất ra Excel
- Lưu và tải lại phiên làm việc

## Yêu cầu hệ thống

- Python 3.7+
- Các thư viện Python: tkinter, PyPDF2, pandas, Pillow, PyMuPDF (fitz)

## Cài đặt

1. Clone repository này về máy của bạn:
   ```
   git clone https://github.com/your-username/pdf-manager.git
   ```

2. Di chuyển vào thư mục dự án:
   ```
   cd pdf-manager
   ```

3. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

## Sử dụng

Để chạy ứng dụng, thực hiện lệnh sau trong terminal:

```
python app.py
```

## Hướng dẫn sử dụng

1. Chọn file PDF: Nhấn nút "Select PDF File" để chọn file PDF bạn muốn xử lý.
2. Xem và chỉnh sửa: Sử dụng thanh cuộn hoặc click chuột để di chuyển giữa các trang PDF. Chỉnh sửa nội dung trong khung văn bản bên phải.
3. Chia phần: Nhấn nút "Break Section" để thêm dấu ngắt phần tại vị trí con trỏ.
4. Xuất Excel: Nhấn nút "Export to Excel" để xuất nội dung đã chỉnh sửa ra file Excel.
5. Chế độ chỉnh sửa nhanh: Bật "Quick Edit Mode" để chỉ cho phép chỉnh sửa giới hạn.
6. Làm sạch văn bản: Bật "Clean Text" để loại bỏ các ký tự không hợp lệ khi xuất ra Excel.
7. Lưu/Tải phiên: Sử dụng "Save Session" và "Load Session" để lưu và tải lại trạng thái làm việc.

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng mở một issue để thảo luận về những thay đổi bạn muốn thực hiện trước khi gửi pull request.

## Giấy phép

[MIT License](https://opensource.org/licenses/MIT)

## Liên hệ

Nếu bạn có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ qua email:hoangducminh.biz@gmail.com

---

Cảm ơn bạn đã sử dụng PDF Manager!
