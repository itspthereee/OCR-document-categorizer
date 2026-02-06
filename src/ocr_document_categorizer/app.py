from __future__ import annotations

import threading
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import easyocr
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:  # noqa: BLE001
    TkinterDnD = None
    DND_FILES = None

from PIL import Image, ImageTk
from reportlab.pdfgen import canvas

from .pipeline import run_pipeline


class DesktopApp:
    def __init__(self) -> None:
        if TkinterDnD is not None:
            self.root = TkinterDnD.Tk()
        else:
            self.root = tk.Tk()
        self.root.title("OCR Document Categorizer")
        self.root.geometry("1100x700")

        self.reader: Optional[easyocr.Reader] = None
        self.image_path: Optional[Path] = None
        self.cropped_photo: Optional[ImageTk.PhotoImage] = None
        self.last_text: str = ""

        self._build_ui()

    def _build_ui(self) -> None:
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.select_button = ttk.Button(toolbar, text="Select Image", command=self._select_image)
        self.select_button.pack(side=tk.LEFT)

        self.run_button = ttk.Button(toolbar, text="Run OCR", command=self._run_ocr, state=tk.DISABLED)
        self.run_button.pack(side=tk.LEFT, padx=8)

        self.copy_button = ttk.Button(toolbar, text="Copy Text", command=self._copy_text, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=8)

        self.export_button = ttk.Button(toolbar, text="Export PDF", command=self._export_pdf, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Select an image to begin.")
        status_label = ttk.Label(toolbar, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=8)

        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(content, padding=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = ttk.Frame(content, padding=8)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(left, text="Cropped Document Preview").pack(anchor=tk.W)
        self.image_label = ttk.Label(left)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        if TkinterDnD is not None:
            self.image_label.drop_target_register(DND_FILES)
            self.image_label.dnd_bind("<<Drop>>", self._handle_drop)
        else:
            self.status_var.set("Drag-and-drop disabled (install tkinterdnd2).")

        ttk.Label(right, text="Categorized Text").pack(anchor=tk.W)
        self.text = tk.Text(right, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True)

    def _select_image(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tiff")],
        )
        if not file_path:
            return
        self._set_image_path(Path(file_path))

    def _set_image_path(self, path: Path) -> None:
        self.image_path = path
        self.run_button.configure(state=tk.NORMAL)
        self.status_var.set(f"Selected: {self.image_path.name}")

    def _handle_drop(self, event) -> None:
        if not event.data:
            return
        raw = event.data.strip()
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        path = Path(raw)
        if path.exists():
            self._set_image_path(path)

    def _run_ocr(self) -> None:
        if not self.image_path:
            return

        self.run_button.configure(state=tk.DISABLED)
        self.status_var.set("Running OCR...")
        self.text.delete("1.0", tk.END)

        thread = threading.Thread(target=self._process_image, daemon=True)
        thread.start()

    def _process_image(self) -> None:
        try:
            if self.reader is None:
                self.reader = easyocr.Reader(["en"])

            result = run_pipeline(self.image_path, self.reader)
            self._update_ui_with_result(result)
        except Exception as exc:  # noqa: BLE001
            self.root.after(0, lambda: self._show_error(str(exc)))
        finally:
            self.root.after(0, lambda: self.run_button.configure(state=tk.NORMAL))

    def _update_ui_with_result(self, result) -> None:
        def update() -> None:
            image = Image.fromarray(result.crop.cropped[:, :, ::-1])
            image.thumbnail((500, 600))
            self.cropped_photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=self.cropped_photo)

            self.text.delete("1.0", tk.END)
            for section in result.sections:
                self.text.insert(tk.END, f"{section.heading}\n")
                self.text.insert(tk.END, f"{section.text}\n\n")

            self.last_text = self.text.get("1.0", tk.END).strip()
            self.copy_button.configure(state=tk.NORMAL)
            self.export_button.configure(state=tk.NORMAL)

            payload = {
                "sections": [asdict(section) for section in result.sections],
                "source_image": str(self.image_path),
            }
            self.status_var.set(f"Done. Sections: {len(payload['sections'])}")

        self.root.after(0, update)

    def _show_error(self, message: str) -> None:
        messagebox.showerror("Error", message)
        self.status_var.set("Error encountered.")

    def _copy_text(self) -> None:
        if not self.last_text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.last_text)
        self.status_var.set("Text copied to clipboard.")

    def _export_pdf(self) -> None:
        if not self.last_text:
            return
        output = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Save PDF",
        )
        if not output:
            return
        self._write_pdf(Path(output), self.last_text)
        self.status_var.set("PDF exported.")

    def _write_pdf(self, path: Path, text: str) -> None:
        pdf = canvas.Canvas(str(path))
        width, height = pdf._pagesize
        margin = 72
        y = height - margin
        for line in text.splitlines():
            if y <= margin:
                pdf.showPage()
                y = height - margin
            pdf.drawString(margin, y, line)
            y -= 14
        pdf.save()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = DesktopApp()
    app.run()


if __name__ == "__main__":
    main()
