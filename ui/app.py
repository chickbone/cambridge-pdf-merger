import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from merge_pdfs import (
    process_zip,
    merge_pdfs_in_dir,
    generate_default_output_name,
    get_pdf_metadata_summary
)
from ui.preview_pane import StructurePreviewPane
from ui.settings_dialog import SettingsWindow


class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Cambridge Core PDF Merger")
        self.geometry("1140x720")
        self.minsize(680, 620)

        # Set default appearance
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Variables & Settings
        self.input_mode = tk.StringVar(value="ZIP Archive")
        self.input_path_var = tk.StringVar(value="")
        self.output_path_var = tk.StringVar(value="")
        self.show_preview_var = tk.BooleanVar(value=True)
        self.is_processing = False
        self.last_output_file = None
        self.settings_window = None

        # Build UI
        self._create_widgets()
        self.apply_preview_visibility(initial=True)

    def _create_widgets(self):
        # Configure main window grid weights (2-column layout) — 60:40 ratio
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)

        # -------------------------------------------------------------
        # Left Panel (Main Control Pane)
        # -------------------------------------------------------------
        self.main_pane = ctk.CTkFrame(self, fg_color="transparent")
        self.main_pane.grid(row=0, column=0, sticky="nsew", padx=(15, 8), pady=15)
        self.main_pane.grid_columnconfigure(0, weight=1)
        self.main_pane.grid_rowconfigure(3, weight=1)

        # 1. Header Frame
        header_frame = ctk.CTkFrame(self.main_pane, corner_radius=10)
        header_frame.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 Cambridge Core PDF Merger",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")

        desc_label = ctk.CTkLabel(
            header_frame,
            text="Merge chapter PDFs into a structured book with hierarchical bookmarks.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="w")

        header_btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_btn_frame.grid(row=0, column=1, rowspan=2, padx=15, pady=10, sticky="e")

        self.toggle_preview_btn = ctk.CTkButton(
            header_btn_frame,
            text="👁 Preview Pane",
            width=110,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#4f46e5",
            hover_color="#4338ca",
            command=self.toggle_preview_pane
        )
        self.toggle_preview_btn.pack(side="left", padx=(0, 8))

        settings_btn = ctk.CTkButton(
            header_btn_frame,
            text="⚙ Settings",
            width=90,
            height=32,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_settings_window
        )
        settings_btn.pack(side="left")

        # 2. Input & Output Configuration Card
        config_frame = ctk.CTkFrame(self.main_pane, corner_radius=10)
        config_frame.grid(row=1, column=0, padx=0, pady=10, sticky="ew")
        config_frame.grid_columnconfigure(1, weight=1)

        # Input Mode Selector
        mode_label = ctk.CTkLabel(config_frame, text="Input Source:", font=ctk.CTkFont(weight="bold"))
        mode_label.grid(row=0, column=0, padx=(15, 10), pady=(15, 8), sticky="w")

        self.mode_selector = ctk.CTkSegmentedButton(
            config_frame,
            values=["ZIP Archive", "PDF Folder"],
            variable=self.input_mode,
            command=self._on_mode_change
        )
        self.mode_selector.grid(row=0, column=1, columnspan=2, padx=15, pady=(15, 8), sticky="ew")

        # Input Path Selector
        input_label = ctk.CTkLabel(config_frame, text="Source Path:", font=ctk.CTkFont(weight="bold"))
        input_label.grid(row=1, column=0, padx=(15, 10), pady=8, sticky="w")

        self.input_entry = ctk.CTkEntry(
            config_frame,
            textvariable=self.input_path_var,
            placeholder_text="Select a .zip archive or PDF folder..."
        )
        self.input_entry.grid(row=1, column=1, padx=(0, 10), pady=8, sticky="ew")

        self.browse_input_btn = ctk.CTkButton(
            config_frame,
            text="Browse...",
            width=90,
            command=self._browse_input
        )
        self.browse_input_btn.grid(row=1, column=2, padx=(0, 15), pady=8)

        # Output Path Selector
        output_label = ctk.CTkLabel(config_frame, text="Output File:", font=ctk.CTkFont(weight="bold"))
        output_label.grid(row=2, column=0, padx=(15, 10), pady=(8, 15), sticky="w")

        self.output_entry = ctk.CTkEntry(
            config_frame,
            textvariable=self.output_path_var,
            placeholder_text="Destination .pdf file path..."
        )
        self.output_entry.grid(row=2, column=1, padx=(0, 10), pady=(8, 15), sticky="ew")

        self.browse_output_btn = ctk.CTkButton(
            config_frame,
            text="Save As...",
            width=90,
            command=self._browse_output
        )
        self.browse_output_btn.grid(row=2, column=2, padx=(0, 15), pady=(8, 15))

        # 3. Action Buttons & Status Frame
        action_frame = ctk.CTkFrame(self.main_pane, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=0, pady=(5, 5), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)

        self.merge_btn = ctk.CTkButton(
            action_frame,
            text="⚡ Merge PDFs",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self._start_merge
        )
        self.merge_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.open_output_btn = ctk.CTkButton(
            action_frame,
            text="📂 Open Merged File",
            height=40,
            width=150,
            state="disabled",
            fg_color="#2b8a3e",
            hover_color="#237032",
            command=self._open_output_file
        )
        self.open_output_btn.grid(row=0, column=1, sticky="e")

        self.progress_bar = ctk.CTkProgressBar(self.main_pane, height=8)
        self.progress_bar.grid(row=2, column=0, padx=0, pady=(50, 5), sticky="ew")
        self.progress_bar.set(0)

        # 4. Switchable Tabview (Process Log & Metadata Tab)
        self.status_tabview = ctk.CTkTabview(self.main_pane, corner_radius=10)
        self.status_tabview.grid(row=3, column=0, padx=0, pady=(10, 0), sticky="nsew")

        # Tab 1: Execution & Process Log
        self.tab_log = self.status_tabview.add("📜 Process Log")
        self.tab_log.grid_columnconfigure(0, weight=1)
        self.tab_log.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(self.tab_log, fg_color="transparent")
        log_header.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="ew")
        log_header.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            log_header,
            text="Status: Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        clear_btn = ctk.CTkButton(
            log_header,
            text="Clear Log",
            width=70,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="gray",
            hover_color="#555",
            command=self._clear_log
        )
        clear_btn.grid(row=0, column=1, sticky="e")

        self.log_textbox = ctk.CTkTextbox(
            self.tab_log,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            corner_radius=6
        )
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Tab 2: Metadata Preview
        self.tab_metadata = self.status_tabview.add("📊  Metadata")
        self.tab_metadata.grid_columnconfigure(0, weight=1)
        self.tab_metadata.grid_rowconfigure(0, weight=1)

        self.metadata_scroll = ctk.CTkScrollableFrame(self.tab_metadata, corner_radius=6, fg_color="transparent")
        self.metadata_scroll.grid(row=0, column=0, padx=8, pady=(4, 8), sticky="nsew")
        self.metadata_scroll.grid_columnconfigure(0, weight=1)

        self._render_metadata_view()

        # -------------------------------------------------------------
        # Right Panel (Graphical Document Structure Preview Pane)
        # -------------------------------------------------------------
        self.preview_pane = StructurePreviewPane(self)

    def _render_metadata_view(self, summary=None):
        for w in self.metadata_scroll.winfo_children():
            w.destroy()

        if summary is None:
            input_path = self.input_path_var.get().strip()
            output_path = self.output_path_var.get().strip()
            summary = get_pdf_metadata_summary(input_path, output_path)

        # Header with Refresh action
        header_bar = ctk.CTkFrame(self.metadata_scroll, fg_color="transparent")
        header_bar.pack(fill="x", pady=(0, 8))
        header_bar.grid_columnconfigure(0, weight=1)

        meta_title = ctk.CTkLabel(
            header_bar,
            text="📄 PDF Properties & Document Metadata",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        meta_title.grid(row=0, column=0, sticky="w")

        refresh_meta_btn = ctk.CTkButton(
            header_bar,
            text="🔄 Refresh",
            width=75,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("black", "white"),
            command=lambda: self._render_metadata_view()
        )
        refresh_meta_btn.grid(row=0, column=1, sticky="e")

        # Stats Cards Grid
        stats_grid = ctk.CTkFrame(self.metadata_scroll, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 10))
        stats_grid.grid_columnconfigure((0, 1, 2), weight=1)

        file_count_chip = ctk.CTkLabel(
            stats_grid,
            text=f"📁 Files: {summary['file_count']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray85", "gray25"),
            corner_radius=6,
            height=28
        )
        file_count_chip.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        pages_chip = ctk.CTkLabel(
            stats_grid,
            text=f"📑 Pages: {summary['total_pages']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray85", "gray25"),
            corner_radius=6,
            height=28
        )
        pages_chip.grid(row=0, column=1, padx=2, sticky="ew")

        out_status_str = f"💾 {summary['output_size_mb']} MB" if summary["output_exists"] else "💾 Not Merged"
        out_chip = ctk.CTkLabel(
            stats_grid,
            text=out_status_str,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#059669" if summary["output_exists"] else ("gray85", "gray25"),
            text_color="white" if summary["output_exists"] else ("black", "white"),
            corner_radius=6,
            height=28
        )
        out_chip.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # Detailed Table Card
        table_card = ctk.CTkFrame(
            self.metadata_scroll,
            corner_radius=8,
            fg_color=("gray92", "gray20"),
            border_width=1,
            border_color=("gray80", "gray28")
        )
        table_card.pack(fill="x", pady=(0, 5))
        table_card.grid_columnconfigure(1, weight=1)

        rows = [
            ("Document Title:", summary.get("title", "Not Specified")),
            ("Author / Creator:", summary.get("author", "Not Specified")),
            ("Subject / Topic:", summary.get("subject", "Not Specified")),
            ("PDF Producer:", summary.get("producer", "Not Specified")),
            ("Creation Date:", summary.get("creation_date", "Not Specified")),
            ("Source Name:", summary.get("source_name", "None")),
            ("Output Status:", f"Created ({summary['output_pages']} pages, {summary['output_size_mb']} MB)" if summary["output_exists"] else "Pending execution"),
        ]

        for idx, (label_text, val_text) in enumerate(rows):
            lbl = ctk.CTkLabel(
                table_card,
                text=label_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="gray",
                anchor="w"
            )
            lbl.grid(row=idx, column=0, padx=(12, 8), pady=5, sticky="w")

            val = ctk.CTkLabel(
                table_card,
                text=str(val_text),
                font=ctk.CTkFont(size=12),
                anchor="w",
                wraplength=380,
                justify="left"
            )
            val.grid(row=idx, column=1, padx=(0, 12), pady=5, sticky="w")

    def apply_preview_visibility(self, initial=False):
        is_visible = self.show_preview_var.get()
        if is_visible:
            self.preview_pane.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
            # 60:40 — main pane weight=3, preview pane weight=2
            self.grid_columnconfigure(0, weight=3)
            self.grid_columnconfigure(1, weight=2)
            self.toggle_preview_btn.configure(fg_color="#4f46e5", text="👁 Hide Preview")
            if not initial:
                current_w = self.winfo_width()
                if current_w < 950:
                    self.geometry("1140x720")
            self.preview_pane.refresh()
        else:
            self.preview_pane.grid_forget()
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
            self.toggle_preview_btn.configure(fg_color=("gray75", "gray30"), text="👁 Show Preview")
            if not initial:
                current_w = self.winfo_width()
                if current_w > 900:
                    self.geometry("700x720")

    def toggle_preview_pane(self):
        new_state = not self.show_preview_var.get()
        self.show_preview_var.set(new_state)
        self.apply_preview_visibility()

    def _open_settings_window(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.lift()
            self.settings_window.focus_force()

    def _on_mode_change(self, value: str):
        self.input_path_var.set("")
        self.output_path_var.set("")
        if value == "ZIP Archive":
            self.input_entry.configure(placeholder_text="Select a .zip archive...")
        else:
            self.input_entry.configure(placeholder_text="Select a directory containing PDFs...")
        self.preview_pane.show_empty_state()
        self._render_metadata_view()

    def _browse_input(self):
        if self.input_mode.get() == "ZIP Archive":
            file_selected = filedialog.askopenfilename(
                title="Select Cambridge Core ZIP Archive",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
            )
            if file_selected:
                self.input_path_var.set(file_selected)
                dir_name = os.path.dirname(file_selected)
                default_filename = generate_default_output_name(file_selected)
                self.output_path_var.set(os.path.join(dir_name, default_filename))
                self.preview_pane.update_preview(file_selected)
                self._render_metadata_view()
        else:
            folder_selected = filedialog.askdirectory(title="Select Folder Containing PDFs")
            if folder_selected:
                self.input_path_var.set(folder_selected)
                parent_dir = os.path.dirname(folder_selected)
                default_filename = generate_default_output_name(folder_selected)
                self.output_path_var.set(os.path.join(parent_dir, default_filename))
                self.preview_pane.update_preview(folder_selected)
                self._render_metadata_view()

    def _browse_output(self):
        current_val = self.output_path_var.get().strip()
        initial_dir = os.path.dirname(current_val) if current_val else os.getcwd()
        initial_file = os.path.basename(current_val) if current_val else "Merged_Document.pdf"

        file_selected = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_selected:
            self.output_path_var.set(file_selected)
            self._render_metadata_view()

    def _log(self, message: str):
        def append():
            self.log_textbox.insert("end", message + "\n")
            self.log_textbox.see("end")
        self.after(0, append)

    def _set_status(self, text: str, color: str = "gray"):
        def update():
            self.status_label.configure(text=f"Status: {text}", text_color=color)
        self.after(0, update)

    def _clear_log(self):
        self.log_textbox.delete("1.0", "end")

    def _start_merge(self):
        if self.is_processing:
            return

        input_path = self.input_path_var.get().strip()
        output_path = self.output_path_var.get().strip()

        if not input_path:
            messagebox.showwarning("Missing Input", "Please select an input ZIP archive or PDF directory.")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Invalid Path", f"Input path does not exist:\n{input_path}")
            return

        if not output_path:
            output_path = generate_default_output_name(input_path)
            self.output_path_var.set(output_path)

        # Update UI state
        self.is_processing = True
        self.merge_btn.configure(state="disabled", text="⏳ Merging...")
        self.browse_input_btn.configure(state="disabled")
        self.browse_output_btn.configure(state="disabled")
        self.mode_selector.configure(state="disabled")
        self.open_output_btn.configure(state="disabled")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self._set_status("Processing...", color="#3b82f6")
        self._log(f"--- Starting merge job at {os.path.basename(output_path)} ---")

        # Run merge in background thread
        thread = threading.Thread(
            target=self._run_merge_worker,
            args=(input_path, output_path),
            daemon=True
        )
        thread.start()

    def _run_merge_worker(self, input_path: str, output_path: str):
        success = False
        try:
            if zipfile_is_valid := input_path.lower().endswith(".zip"):
                success = process_zip(input_path, output_path, status_callback=self._log)
            elif os.path.isdir(input_path):
                success = merge_pdfs_in_dir(input_path, output_path, status_callback=self._log)
            else:
                self._log("Error: Input is neither a valid ZIP file nor a directory.")
                success = False
        except Exception as e:
            self._log(f"\n[Exception occurred]: {str(e)}")
            success = False

        self.after(0, self._on_merge_complete, success, output_path)

    def _on_merge_complete(self, success: bool, output_path: str):
        self.is_processing = False
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        
        self.merge_btn.configure(state="normal", text="⚡ Merge PDFs")
        self.browse_input_btn.configure(state="normal")
        self.browse_output_btn.configure(state="normal")
        self.mode_selector.configure(state="normal")

        # Refresh metadata view to show created file size and status
        self._render_metadata_view()

        if success:
            self.progress_bar.set(1.0)
            self.last_output_file = output_path
            self.open_output_btn.configure(state="normal")
            self._set_status("Merged successfully!", color="#22c55e")
            self._log("Job completed successfully.\n")
            messagebox.showinfo("Success", f"PDF successfully created:\n{output_path}")
        else:
            self.progress_bar.set(0)
            self._set_status("Merge failed. Check log for details.", color="#ef4444")
            self._log("Job failed.\n")
            messagebox.showerror("Merge Failed", "An error occurred while merging PDFs. Please check the log for details.")

    def _open_output_file(self):
        if self.last_output_file and os.path.exists(self.last_output_file):
            try:
                if sys.platform == "win32":
                    os.startfile(self.last_output_file)
                elif sys.platform == "darwin":
                    subprocess.run(["open", self.last_output_file], check=True)
                else:
                    subprocess.run(["xdg-open", self.last_output_file], check=True)
            except Exception as e:
                messagebox.showerror("Error Opening File", f"Could not open file: {e}")
        else:
            messagebox.showwarning("File Not Found", "Output PDF could not be found.")


def launch_gui():
    app = PDFMergerApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
