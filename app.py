# ĐỀ TÀI: ỨNG DỤNG ĐỌC TIN TỨC PHÁT ÂM THANH TỪ VĂN BẢN LẤY TỪ TẬP TIN

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Combobox
import threading
import time
import os
import logging
from docx import Document
import fitz  # PyMuPDF
from gtts import gTTS
import re
from langdetect import detect

# Cấu hình log
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Module: Xử lý tệp và văn bản
def doc_tep(duong_dan_tep):
    """
    Đọc và trả về nội dung văn bản từ tệp.
    Hỗ trợ định dạng .txt, .docx, và .pdf.
    """
    try:
        if os.path.getsize(duong_dan_tep) > 10 * 1024 * 1024:  # Giới hạn 10 MB
            raise ValueError("Tệp quá lớn, không thể xử lý!")

        if duong_dan_tep.endswith('.txt'):
            with open(duong_dan_tep, 'r', encoding='utf-8') as tep:
                van_ban = tep.read()
        elif duong_dan_tep.endswith('.docx'):
            doc = Document(duong_dan_tep)
            van_ban = '\n'.join(doan.text.strip() for doan in doc.paragraphs)
        elif duong_dan_tep.endswith('.pdf'):
            pdf = fitz.open(duong_dan_tep)
            van_ban = ''.join(trang.get_text() for trang in pdf.pages())
            pdf.close()
        else:
            raise ValueError("Định dạng tệp không được hỗ trợ!")

        van_ban = lam_sach_van_ban(van_ban)
        if not van_ban.strip():
            raise ValueError("Tệp không có nội dung đọc được!")
        return van_ban
    except Exception as e:
        logging.error(f"Lỗi khi đọc tệp: {e}")
        raise RuntimeError(f"Lỗi khi đọc tệp: {e}")


def lam_sach_van_ban(van_ban):
    """
    Làm sạch và chuẩn hóa văn bản bằng cách xóa khoảng trắng không cần thiết
    và các ký tự điều khiển.
    """
    try:
        van_ban = re.sub(r'\s+', ' ', van_ban)  # Thu gọn nhiều khoảng trắng thành một
        van_ban = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', van_ban)  # Xóa ký tự điều khiển
        van_ban = re.sub(r'[^\w\s,.!?-]', '', van_ban)  # Loại bỏ kí tự không mong muốn
        return van_ban.strip()
    except Exception as e:
        logging.error(f"Lỗi khi làm sạch văn bản: {e}")
        raise ValueError(f"Lỗi khi làm sạch văn bản: {e}")

# Module: Chuyển văn bản thành giọng nói
def van_ban_thanh_am_thanh(duong_dan_tep, duong_dan_luu, ngon_ngu='vi', toc_do_doc=False):
    """
    Chuyển văn bản từ tệp đầu vào thành giọng nói và lưu thành tệp âm thanh.
    """
    try:
        van_ban = doc_tep(duong_dan_tep)
        detected_lang = detect(van_ban)
        logging.info(f"Ngôn ngữ phát hiện: {detected_lang}")

        # Nếu ngôn ngữ phát hiện không khớp với lựa chọn, sử dụng ngôn ngữ phát hiện
        if detected_lang != ngon_ngu:
            logging.warning(f"Sử dụng ngôn ngữ phát hiện ({detected_lang}) thay vì ngôn ngữ chọn ({ngon_ngu})")
            ngon_ngu = detected_lang

        toc_do = True if toc_do_doc else False  # Tốc độ đọc (chậm nếu True)
        tts = gTTS(text=van_ban, lang=ngon_ngu, slow=toc_do)

        ten_tep = os.path.splitext(os.path.basename(duong_dan_tep))[0]
        tep_am_thanh = os.path.join(duong_dan_luu, f"{ten_tep}.mp3")
        tts.save(tep_am_thanh)
        return tep_am_thanh
    except Exception as e:
        logging.error(f"Lỗi khi chuyển văn bản thành giọng nói: {e}")
        raise RuntimeError(f"Lỗi khi chuyển văn bản thành giọng nói: {e}")

# Module: Giao diện người dùng
def xu_ly_thanh_tien_do(thanh_tien_do, buoc_bat_dau, buoc_ket_thuc):
    """
    Cập nhật thanh tiến trình từ từ dựa trên trạng thái xử lý cụ thể.
    """
    for i in range(buoc_bat_dau, buoc_ket_thuc + 1):
        thanh_tien_do["value"] = i
        thanh_tien_do.update_idletasks()
        time.sleep(0.01)  # Giảm thời gian chờ để xử lý nhanh hơn

def xu_ly_tep_van_ban(thanh_tien_do, duong_dan_tep, duong_dan_luu, ma_ngon_ngu, toc_do):
    """
    Xử lý chuyển văn bản thành giọng nói và cập nhật giao diện.
    """
    try:
        # Đọc tệp
        logging.info(f"Bắt đầu xử lý tệp: {duong_dan_tep}")
        xu_ly_thanh_tien_do(thanh_tien_do, 0, 20)
        van_ban = doc_tep(duong_dan_tep)

        # Làm sạch văn bản
        xu_ly_thanh_tien_do(thanh_tien_do, 20, 50)
        van_ban = lam_sach_van_ban(van_ban)

        # Chuyển văn bản thành âm thanh
        xu_ly_thanh_tien_do(thanh_tien_do, 50, 90)
        tep_am_thanh = van_ban_thanh_am_thanh(
            duong_dan_tep,
            duong_dan_luu,
            ngon_ngu=ma_ngon_ngu,
            toc_do_doc=toc_do
        )

        # Hoàn tất
        xu_ly_thanh_tien_do(thanh_tien_do, 90, 100)
        messagebox.showinfo("Thành công", f"Tệp âm thanh đã được lưu tại:\n{tep_am_thanh}")
    except Exception as e:
        thanh_tien_do["value"] = 0
        thanh_tien_do.update_idletasks()
        logging.error(f"Lỗi khi xử lý tệp: {e}")
        messagebox.showerror("Lỗi", str(e))

def chon_tep(thanh_tien_do, ngon_ngu, toc_do):
    """
    Hiển thị hộp thoại để người dùng chọn tệp và xử lý chuyển đổi văn bản thành giọng nói.
    """
    try:
        mapping_ngon_ngu = {
            "Tiếng Việt": "vi",
            "Tiếng Anh": "en",
            "Tiếng Pháp": "fr",
            "Tiếng Đức": "de",
            "Tiếng Tây Ban Nha": "es",
            "Tiếng Nhật": "ja",
            "Tiếng Trung": "zh",
            "Tiếng Hàn": "ko",
            "Tiếng Ý": "it",
            "Tiếng Nga": "ru",
        }
        ma_ngon_ngu = mapping_ngon_ngu.get(ngon_ngu.get())
        if not ma_ngon_ngu:
            messagebox.showerror("Lỗi", f"Ngôn ngữ không được hỗ trợ: {ngon_ngu.get()}")
            return

        duong_dan_tep = filedialog.askopenfilename(filetypes=[("Các tệp được hỗ trợ", "*.txt *.docx *.pdf")])
        if not duong_dan_tep:
            return

        duong_dan_luu = filedialog.askdirectory(title="Chọn nơi lưu tệp âm thanh")
        if not duong_dan_luu:
            return

        threading.Thread(
            target=xu_ly_tep_van_ban,
            args=(thanh_tien_do, duong_dan_tep, duong_dan_luu, ma_ngon_ngu, toc_do.get()),
            daemon=True
        ).start()

    except Exception as e:
        logging.error(f"Đã xảy ra lỗi: {e}")
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")

def main():
    """
    Cài đặt và chạy giao diện người dùng chính của ứng dụng.
    """
    root = tk.Tk()
    root.title("Ứng dụng Chuyển Văn Bản Thành Giọng Nói")
    root.geometry("500x400")
    root.configure(bg="#f0f8ff")

    tieu_de = tk.Label(
        root, text="ỨNG DỤNG CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI", font=("Arial", 15, "bold"), bg="#f0f8ff", fg="#333"
    )
    tieu_de.pack(pady=20)

    mo_ta = tk.Label(
        root, text="Chọn tệp văn bản và cài đặt tùy chọn:", font=("Arial", 12), bg="#f0f8ff", fg="#555"
    )
    mo_ta.pack(pady=10)

    thanh_tien_do = Progressbar(root, length=400, mode="determinate")
    thanh_tien_do.pack(pady=10)

    khung_tuy_chon = tk.Frame(root, bg="#f0f8ff")
    khung_tuy_chon.pack(pady=10)

    tk.Label(khung_tuy_chon, text="Ngôn ngữ:", bg="#f0f8ff").grid(row=0, column=0, padx=5, sticky="w")
    ngon_ngu = Combobox(khung_tuy_chon, values=["Tiếng Việt", "Tiếng Anh", "Tiếng Pháp", "Tiếng Đức", "Tiếng Tây Ban Nha", "Tiếng Nhật", "Tiếng Trung", "Tiếng Hàn", "Tiếng Ý", "Tiếng Nga"])
    ngon_ngu.set("Tiếng Việt")
    ngon_ngu.grid(row=0, column=1, padx=5)

    tk.Label(khung_tuy_chon, text="Tốc độ đọc chậm:", bg="#f0f8ff").grid(row=1, column=0, padx=5, sticky="w")
    toc_do = tk.BooleanVar()
    tk.Checkbutton(khung_tuy_chon, variable=toc_do, bg="#f0f8ff").grid(row=1, column=1, padx=5)

    nut_chon_tep = tk.Button(
        root,
        text="Chọn Tệp",
        command=lambda: chon_tep(thanh_tien_do, ngon_ngu, toc_do),
        font=("Arial", 14),
        bg="#4682b4",
        fg="white",
        activebackground="#5a9bd4",
        activeforeground="white",
    )
    nut_chon_tep.pack(pady=30)

    chan_trang = tk.Label(root, text="© 2025 - Ứng Dụng Python", font=("Arial", 10, "italic"), bg="#f0f8ff", fg="#999")
    chan_trang.pack(side=tk.BOTTOM, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()

