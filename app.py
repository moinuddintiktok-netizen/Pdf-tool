
import os
import threading
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core.pdf_tools import (
    word_to_pdf,
    pdf_to_word,
    images_to_pdf,
    merge_pdfs,
    split_pdf,
    protect_pdf,
    unlock_pdf,
)
from core.file_tools import (
    scan_temp_files,
    clean_paths,
    organize_folder,
    find_duplicates,
    disk_overview,
)

APP_NAME = "SMART PDF STUDIO"
VERSION = "1.0.0"

BG = "#070A12"
PANEL = "#101522"
PANEL_2 = "#151B2B"
CYAN = "#35E8FF"
PURPLE = "#A855F7"
GREEN = "#35F59A"
TEXT = "#F4F7FB"
MUTED = "#8D99AE"
RED = "#FF5C7A"


class NeonCard(ctk.CTkFrame):
    def __init__(self, master, title, value, subtitle, accent=CYAN, **kwargs):
        super().__init__(master, fg_color=PANEL, corner_radius=18, border_width=1,
                         border_color="#202A40", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text=title, text_color=MUTED,
                     font=ctk.CTkFont(size=12, weight="bold")).grid(
                         row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        ctk.CTkLabel(self, text=value, text_color=accent,
                     font=ctk.CTkFont(size=28, weight="bold")).grid(
                         row=1, column=0, padx=18, pady=0, sticky="w")
        ctk.CTkLabel(self, text=subtitle, text_color=MUTED,
                     font=ctk.CTkFont(size=11)).grid(
                         row=2, column=0, padx=18, pady=(2, 16), sticky="w")


class SmartPDFStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(f"{APP_NAME} • {VERSION}")
        self.geometry("1280x820")
        self.minsize(1040, 700)
        self.configure(fg_color=BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready • Offline mode")
        self._build_sidebar()
        self._build_main()

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#090D17")
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)

        ctk.CTkLabel(
            side, text="✦", text_color=CYAN,
            font=ctk.CTkFont(size=42, weight="bold")
        ).pack(pady=(28, 0))
        ctk.CTkLabel(
            side, text="SMART PDF", text_color=TEXT,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 0))
        ctk.CTkLabel(
            side, text="STUDIO • VIP EDITION", text_color=PURPLE,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(pady=(0, 30))

        self.nav_buttons = []
        for text, command in [
            ("◈  Dashboard", self.show_dashboard),
            ("▣  PDF Toolkit", self.show_pdf),
            ("◫  PC Cleaner", self.show_cleaner),
            ("⌘  File Organizer", self.show_organizer),
        ]:
            btn = ctk.CTkButton(
                side, text=text, command=command, anchor="w",
                height=44, corner_radius=12, fg_color="transparent",
                hover_color="#18223A", text_color=TEXT,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            btn.pack(fill="x", padx=18, pady=4)
            self.nav_buttons.append(btn)

        ctk.CTkLabel(side, text="", height=1).pack(expand=True)
        ctk.CTkLabel(
            side, text="100% LOCAL PROCESSING",
            text_color=GREEN, font=ctk.CTkFont(size=10, weight="bold")
        ).pack(pady=(0, 6))
        ctk.CTkLabel(
            side, text="No upload • No cloud required",
            text_color=MUTED, font=ctk.CTkFont(size=10)
        ).pack(pady=(0, 20))

    def _build_main(self):
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(self.main, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text="SMART PDF STUDIO",
            text_color=TEXT, font=ctk.CTkFont(size=30, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            top, text="Offline productivity suite • PDF + PC utilities",
            text_color=MUTED, font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w")

        ctk.CTkButton(
            top, text="☾  Dark", width=90, height=32,
            command=self.toggle_mode, fg_color=PANEL_2, hover_color="#222B42"
        ).grid(row=0, column=1, rowspan=2, padx=(10, 0))

        self.content = ctk.CTkScrollableFrame(
            self.main, fg_color="transparent", corner_radius=0
        )
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)

        self.show_dashboard()

        footer = ctk.CTkFrame(self.main, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        footer.grid_columnconfigure(0, weight=1)

        status = ctk.CTkLabel(
            footer, textvariable=self.status_var,
            text_color=MUTED, anchor="w",
            font=ctk.CTkFont(size=11)
        )
        status.grid(row=0, column=0, sticky="w")

        created = ctk.CTkLabel(
            footer,
            text="Created by Chishti Bro Computers and Developers",
            text_color=CYAN, anchor="e",
            font=ctk.CTkFont(size=10, weight="bold")
        )
        created.grid(row=0, column=1, sticky="e")

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def toggle_mode(self):
        mode = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if mode == "Dark" else "dark")

    def set_status(self, text):
        self.status_var.set(text)

    def show_dashboard(self):
        self.clear_content()
        ctk.CTkLabel(
            self.content, text="Your offline command center",
            text_color=TEXT, font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(4, 14))

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew")
        for i in range(4):
            cards.grid_columnconfigure(i, weight=1)

        for i, data in enumerate([
            ("PDF ENGINE", "8+", "Core PDF operations", CYAN),
            ("CONVERTERS", "3", "Word / PDF / Images", PURPLE),
            ("CLEANER", "SAFE", "Preview before delete", GREEN),
            ("ORGANIZER", "SMART", "Extension-based filing", "#FFB84D"),
        ]):
            NeonCard(cards, *data).grid(row=0, column=i, padx=5, sticky="ew")

        hero = ctk.CTkFrame(
            self.content, fg_color=PANEL, corner_radius=22,
            border_width=1, border_color="#202A40"
        )
        hero.grid(row=2, column=0, sticky="ew", pady=16)
        hero.grid_columnconfigure(0, weight=1)
        hero.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hero, text="⚡ OFFLINE-FIRST • FAST • PRIVATE",
            text_color=CYAN, font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=24, pady=(24, 8), sticky="w")
        ctk.CTkLabel(
            hero, text="Professional PDF tools without sending your files to a server.",
            text_color=TEXT, justify="left",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=1, column=0, padx=24, pady=(0, 8), sticky="w")
        ctk.CTkLabel(
            hero, text="Merge • Split • Convert • Protect • Unlock • Organize • Clean",
            text_color=MUTED, justify="left",
            font=ctk.CTkFont(size=13)
        ).grid(row=2, column=0, padx=24, pady=(0, 22), sticky="w")

        ctk.CTkButton(
            hero, text="OPEN PDF TOOLKIT →", height=46, corner_radius=14,
            fg_color=CYAN, hover_color="#22BFD2", text_color="#041016",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.show_pdf
        ).grid(row=1, column=1, rowspan=2, padx=24, pady=20, sticky="e")

    def section_title(self, title, subtitle):
        ctk.CTkLabel(
            self.content, text=title, text_color=TEXT,
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(4, 2))
        ctk.CTkLabel(
            self.content, text=subtitle, text_color=MUTED,
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, sticky="w", pady=(0, 16))

    def action_card(self, row, title, description, command, accent=CYAN):
        card = ctk.CTkFrame(
            self.content, fg_color=PANEL, corner_radius=18,
            border_width=1, border_color="#202A40"
        )
        card.grid(row=row, column=0, sticky="ew", pady=7)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=title, text_color=accent,
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(16, 3), sticky="w")
        ctk.CTkLabel(
            card, text=description, text_color=MUTED,
            font=ctk.CTkFont(size=11), wraplength=700, justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 16), sticky="w")
        ctk.CTkButton(
            card, text="RUN", width=120, height=38, corner_radius=11,
            fg_color=accent, hover_color=accent, text_color="#061018",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=command
        ).grid(row=0, column=1, rowspan=2, padx=20)

    def show_pdf(self):
        self.clear_content()
        self.section_title(
            "Smart PDF Toolkit",
            "Offline PDF operations • local files stay on your computer"
        )
        self.action_card(2, "PDF → Word", "Extract PDF text into an editable DOCX file.",
                         self.pdf_to_word_ui, PURPLE)
        self.action_card(3, "Word → PDF", "Convert DOCX to PDF. Uses LibreOffice when available; otherwise creates a clean text PDF.",
                         self.word_to_pdf_ui, CYAN)
        self.action_card(4, "Images → PDF", "Combine JPG, JPEG, PNG and WEBP images into one PDF.",
                         self.images_to_pdf_ui, GREEN)
        self.action_card(5, "Merge PDFs", "Join multiple PDF files into one document.",
                         self.merge_ui, "#FFB84D")
        self.action_card(6, "Split PDF", "Export selected page ranges such as 1-3, 5, 8-10.",
                         self.split_ui, "#FF6EA8")
        self.action_card(7, "Password Protect", "Encrypt a PDF with AES-256 when the cryptography provider is available.",
                         self.protect_ui, CYAN)
        self.action_card(8, "Unlock PDF", "Remove PDF encryption when you know the document password.",
                         self.unlock_ui, RED)

    def ask_save(self, title, default_ext):
        return filedialog.asksaveasfilename(
            title=title, defaultextension=default_ext,
            filetypes=[("Files", f"*{default_ext}"), ("All files", "*.*")]
        )

    def run_threaded(self, fn, success="Done"):
        def worker():
            try:
                result = fn()
                self.after(0, lambda: self.set_status(f"✓ {success}"))
                self.after(0, lambda: messagebox.showinfo("Smart PDF Studio", str(result or success)))
            except Exception as e:
                self.after(0, lambda: self.set_status("Operation failed"))
                self.after(0, lambda: messagebox.showerror("Operation failed", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def pdf_to_word_ui(self):
        src = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not src: return
        out = self.ask_save("Save Word document", ".docx")
        if not out: return
        self.set_status("Converting PDF → Word…")
        self.run_threaded(lambda: pdf_to_word(src, out), "PDF converted to Word")

    def word_to_pdf_ui(self):
        src = filedialog.askopenfilename(filetypes=[("Word documents", "*.docx")])
        if not src: return
        out = self.ask_save("Save PDF", ".pdf")
        if not out: return
        self.set_status("Converting Word → PDF…")
        self.run_threaded(lambda: word_to_pdf(src, out), "Word converted to PDF")

    def images_to_pdf_ui(self):
        srcs = filedialog.askopenfilenames(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp")]
        )
        if not srcs: return
        out = self.ask_save("Save image PDF", ".pdf")
        if not out: return
        self.set_status("Building image PDF…")
        self.run_threaded(lambda: images_to_pdf(srcs, out), "Images converted to PDF")

    def merge_ui(self):
        srcs = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if not srcs: return
        out = self.ask_save("Save merged PDF", ".pdf")
        if not out: return
        self.set_status("Merging PDFs…")
        self.run_threaded(lambda: merge_pdfs(srcs, out), "PDFs merged")

    def split_ui(self):
        src = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not src: return
        pages = ctk.CTkInputDialog(
            text="Enter pages/ranges (example: 1-3,5,8-10):",
            title="Split PDF"
        ).get_input()
        if not pages: return
        out = self.ask_save("Save split PDF", ".pdf")
        if not out: return
        self.set_status("Splitting PDF…")
        self.run_threaded(lambda: split_pdf(src, pages, out), "PDF split complete")

    def protect_ui(self):
        src = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not src: return
        password = ctk.CTkInputDialog(text="Enter a strong password:", title="Password Protect").get_input()
        if not password: return
        out = self.ask_save("Save protected PDF", ".pdf")
        if not out: return
        self.set_status("Encrypting PDF…")
        self.run_threaded(lambda: protect_pdf(src, out, password), "PDF protected")

    def unlock_ui(self):
        src = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not src: return
        password = ctk.CTkInputDialog(text="Enter PDF password:", title="Unlock PDF").get_input()
        if not password: return
        out = self.ask_save("Save unlocked PDF", ".pdf")
        if not out: return
        self.set_status("Unlocking PDF…")
        self.run_threaded(lambda: unlock_pdf(src, out, password), "PDF unlocked")

    def show_cleaner(self):
        self.clear_content()
        self.section_title(
            "PC Cleaner",
            "Preview-first cleanup. Nothing is deleted automatically."
        )
        self.action_card(2, "Scan Temporary Files",
                         "Find common temporary/cache files in the current user's temp folders.",
                         self.clean_scan_ui, GREEN)
        self.action_card(3, "Disk Overview",
                         "Show free/used space for the main filesystem.",
                         self.disk_ui, CYAN)
        self.action_card(4, "Duplicate Finder",
                         "Find duplicate files by size + SHA-256 hash. Review before deletion.",
                         self.duplicate_ui, PURPLE)

    def clean_scan_ui(self):
        self.set_status("Scanning temporary files…")
        self.run_threaded(self.clean_scan, "Scan complete")

    def clean_scan(self):
        items, total = scan_temp_files()
        if not items:
            return "No removable temporary files found."
        answer = messagebox.askyesno(
            "Cleanup preview",
            f"Found {len(items)} files ({total/1024/1024:.1f} MB).\n\nDelete these files now?"
        )
        if answer:
            deleted, freed = clean_paths(items)
            return f"Deleted {deleted} files and freed {freed/1024/1024:.1f} MB."
        return "Cleanup cancelled. No files were deleted."

    def disk_ui(self):
        total, used, free = disk_overview()
        messagebox.showinfo(
            "Disk Overview",
            f"Total: {total/1024**3:.1f} GB\n"
            f"Used:  {used/1024**3:.1f} GB\n"
            f"Free:  {free/1024**3:.1f} GB"
        )

    def duplicate_ui(self):
        folder = filedialog.askdirectory(title="Choose folder to scan")
        if not folder: return
        self.set_status("Finding duplicates…")
        self.run_threaded(lambda: self.duplicate_scan(folder), "Duplicate scan complete")

    def duplicate_scan(self, folder):
        groups = find_duplicates(folder)
        count = sum(len(v) - 1 for v in groups.values() if len(v) > 1)
        if count == 0:
            return "No duplicates found."
        report = ["Duplicate groups:"]
        for key, paths in list(groups.items())[:30]:
            report.append(f"\n{key}:")
            report.extend(f"  • {p}" for p in paths)
        messagebox.showinfo("Duplicate Finder", "\n".join(report))
        return f"Found {count} duplicate copies."

    def show_organizer(self):
        self.clear_content()
        self.section_title(
            "File Organizer",
            "Create clean extension-based folders without touching system files."
        )
        self.action_card(
            2, "Organize Folder",
            "Move files into folders such as Images, Documents, Videos, Archives and Others.",
            self.organize_ui, CYAN
        )

    def organize_ui(self):
        folder = filedialog.askdirectory(title="Choose folder to organize")
        if not folder: return
        answer = messagebox.askyesno(
            "Confirm organization",
            "Files will be moved into categorized subfolders. Continue?"
        )
        if not answer: return
        self.set_status("Organizing files…")
        self.run_threaded(lambda: organize_folder(folder), "Folder organized")


if __name__ == "__main__":
    app = SmartPDFStudio()
    app.mainloop()
