# ĐỀ TÀI: ỨNG DỤNG CHUYỂN ĐỔI VĂN BẢN THÀNH ÂM THANH

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Combobox

import threading
import time
import os
import logging
import re

from docx import Document
import fitz  # PyMuPDF
from gtts import gTTS
from langdetect import detect

# =========================
# Cấu hình log
# =========================
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# Module: Xử lý tệp và văn bản
# =========================
def doc_tep(duong_dan_tep):
    """
    Đọc và trả về nội dung văn bản từ tệp.
    Hỗ trợ định dạng .txt, .docx, và .pdf.
    """
    try:
        if os.path.getsize(duong_dan_tep) > 10 * 1024 * 1024:  # Giới hạn 10 MB
            raise ValueError("Tệp quá lớn, không thể xử lý!")

        if duong_dan_tep.endswith(".txt"):
            with open(duong_dan_tep, "r", encoding="utf-8") as tep:
                van_ban = tep.read()

        elif duong_dan_tep.endswith(".docx"):
            doc = Document(duong_dan_tep)
            van_ban = "\n".join(doan.text.strip() for doan in doc.paragraphs)

        elif duong_dan_tep.endswith(".pdf"):
            pdf = fitz.open(duong_dan_tep)
            van_ban = "".join(trang.get_text() for trang in pdf.pages())
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
    Làm sạch và chuẩn hóa văn bản:
    - Thu gọn khoảng trắng
    - Xóa ký tự điều khiển
    - Loại bỏ ký tự không mong muốn (giữ chữ/số, khoảng trắng và một số dấu câu)
    """
    try:
        van_ban = re.sub(r"\s+", " ", van_ban)
        van_ban = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", van_ban)
        van_ban = re.sub(r"[^\w\s,.!?-]", "", van_ban)
        return van_ban.strip()
    except Exception as e:
        logging.error(f"Lỗi khi làm sạch văn bản: {e}")
        raise ValueError(f"Lỗi khi làm sạch văn bản: {e}")

# =========================
# Module: Chuyển văn bản thành giọng nói
# =========================
def van_ban_thanh_am_thanh(duong_dan_tep, duong_dan_luu, ngon_ngu="vi", toc_do_doc=False):
    """
    Chuyển văn bản từ tệp đầu vào thành giọng nói và lưu thành tệp âm thanh.
    Lưu ý: Ứng dụng chỉ hỗ trợ 2 ngôn ngữ (vi/en), nên KHÔNG tự đổi theo detect.
    """
    try:
        van_ban = doc_tep(duong_dan_tep)

        # Ghi log để tham khảo (không tự đổi ngôn ngữ)
        try:
            detected_lang = detect(van_ban)
            logging.info(f"Ngôn ngữ phát hiện (tham khảo): {detected_lang}")
        except Exception as e:
            logging.warning(f"Không phát hiện được ngôn ngữ: {e}")

        toc_do = True if toc_do_doc else False  # True => đọc chậm
        tts = gTTS(text=van_ban, lang=ngon_ngu, slow=toc_do)

        ten_tep = os.path.splitext(os.path.basename(duong_dan_tep))[0]
        tep_am_thanh = os.path.join(duong_dan_luu, f"{ten_tep}.mp3")
        tts.save(tep_am_thanh)

        return tep_am_thanh

    except Exception as e:
        logging.error(f"Lỗi khi chuyển văn bản thành giọng nói: {e}")
        raise RuntimeError(f"Lỗi khi chuyển văn bản thành giọng nói: {e}")

# =========================
# Module: Giao diện người dùng
# =========================
def xu_ly_thanh_tien_do(thanh_tien_do, buoc_bat_dau, buoc_ket_thuc):
    """Cập nhật thanh tiến trình từ từ dựa trên trạng thái xử lý cụ thể."""
    for i in range(buoc_bat_dau, buoc_ket_thuc + 1):
        thanh_tien_do["value"] = i
        thanh_tien_do.update_idletasks()
        time.sleep(0.01)


def xu_ly_tep_van_ban(thanh_tien_do, duong_dan_tep, duong_dan_luu, ma_ngon_ngu, toc_do):
    """Xử lý chuyển văn bản thành giọng nói và cập nhật giao diện."""
    try:
        logging.info(f"Bắt đầu xử lý tệp: {duong_dan_tep}")

        # Đọc tệp
        xu_ly_thanh_tien_do(thanh_tien_do, 0, 20)
        van_ban = doc_tep(duong_dan_tep)

        # Làm sạch văn bản (doc_tep đã làm rồi, nhưng giữ lại để tương thích)
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
    """Hiển thị hộp thoại chọn tệp và chạy xử lý chuyển đổi."""
    try:
        mapping_ngon_ngu = {
            "Tiếng Việt": "vi",
            "Tiếng Anh": "en",
        }

        ma_ngon_ngu = mapping_ngon_ngu.get(ngon_ngu.get())
        if not ma_ngon_ngu:
            messagebox.showerror("Lỗi", f"Ngôn ngữ không được hỗ trợ: {ngon_ngu.get()}")
            return

        duong_dan_tep = filedialog.askopenfilename(
            filetypes=[("Các tệp được hỗ trợ", "*.txt *.docx *.pdf")]
        )
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
    root = tk.Tk()
    root.title("Text to Speech - TTS")
    root.geometry("720x420")
    root.minsize(680, 400)
    root.configure(bg="#0f172a")  # nền tối

    # ===== Header =====
    header = tk.Frame(root, bg="#0f172a")
    header.pack(fill="x", padx=18, pady=(16, 10))

    tk.Label(
        header,
        text="CHUYỂN VĂN BẢN THÀNH GIỌNG NÓI",
        font=("Segoe UI", 16, "bold"),
        bg="#0f172a",
        fg="#e2e8f0"
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Hỗ trợ TXT / DOCX / PDF • Xuất MP3 • Chọn ngôn ngữ và tốc độ đọc",
        font=("Segoe UI", 10),
        bg="#0f172a",
        fg="#94a3b8"
    ).pack(anchor="w", pady=(6, 0))

    # ===== Main content =====
    body = tk.Frame(root, bg="#0f172a")
    body.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    # Card
    card = tk.Frame(body, bg="#111827", bd=0, highlightthickness=1, highlightbackground="#1f2937")
    card.pack(fill="both", expand=True)

    content = tk.Frame(card, bg="#111827")
    content.pack(fill="both", expand=True, padx=18, pady=18)

    # Left panel
    left = tk.Frame(content, bg="#111827")
    left.pack(side="left", fill="both", expand=True, padx=(0, 12))

    tk.Label(
        left,
        text="Tùy chọn",
        font=("Segoe UI", 12, "bold"),
        bg="#111827",
        fg="#e5e7eb"
    ).pack(anchor="w")

    form = tk.Frame(left, bg="#111827")
    form.pack(fill="x", pady=(12, 0))

    tk.Label(form, text="Ngôn ngữ", font=("Segoe UI", 10), bg="#111827", fg="#cbd5e1") \
        .grid(row=0, column=0, sticky="w", pady=6)

    ngon_ngu = Combobox(form, values=["Tiếng Việt", "Tiếng Anh"], state="readonly")
    ngon_ngu.set("Tiếng Việt")
    ngon_ngu.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=6)

    tk.Label(form, text="Tốc độ chậm", font=("Segoe UI", 10), bg="#111827", fg="#cbd5e1") \
        .grid(row=1, column=0, sticky="w", pady=6)

    toc_do = tk.BooleanVar(value=False)
    tk.Checkbutton(
        form,
        variable=toc_do,
        bg="#111827",
        activebackground="#111827",
        highlightthickness=0
    ).grid(row=1, column=1, sticky="w", padx=(10, 0), pady=6)

    form.grid_columnconfigure(1, weight=1)

    status_var = tk.StringVar(value="Sẵn sàng. Nhấn “Chọn tệp & chuyển đổi”.")
    tk.Label(left, textvariable=status_var, font=("Segoe UI", 10), bg="#111827", fg="#94a3b8") \
        .pack(anchor="w", pady=(14, 6))

    thanh_tien_do = Progressbar(left, mode="determinate")
    thanh_tien_do.pack(fill="x", pady=(0, 6))

    # Right panel
    right = tk.Frame(content, bg="#111827")
    right.pack(side="right", fill="y")

    def _start():
        status_var.set("Đang mở hộp thoại chọn tệp...")
        chon_tep(thanh_tien_do, ngon_ngu, toc_do)
        status_var.set("Đang xử lý... (theo dõi thanh tiến trình)")

    tk.Button(
        right,
        text="Chọn tệp\n& chuyển đổi",
        command=_start,
        font=("Segoe UI", 12, "bold"),
        bg="#2563eb",
        fg="white",
        activebackground="#1d4ed8",
        activeforeground="white",
        bd=0,
        padx=18,
        pady=14,
        width=14
    ).pack(pady=(0, 10))

    tk.Button(
        right,
        text="Thoát",
        command=root.destroy,
        font=("Segoe UI", 11),
        bg="#334155",
        fg="white",
        activebackground="#475569",
        activeforeground="white",
        bd=0,
        padx=18,
        pady=10,
        width=14
    ).pack()

    footer = tk.Frame(root, bg="#0f172a")
    footer.pack(fill="x", padx=18, pady=(0, 10))
    tk.Label(
        footer,
        text="© 2025 - Ứng dụng Python",
        font=("Segoe UI", 9),
        bg="#0f172a",
        fg="#64748b"
    ).pack(anchor="w")

    root.mainloop()


if __name__ == "__main__":
    main()
