import os
import customtkinter as ctk
from merge_pdfs import get_input_structure
from ui.tooltip import ToolTip


class StructurePreviewPane(ctk.CTkFrame):
    """Graphical in-window preview pane displaying hierarchical chapters and sections."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        self.parent = parent
        self.current_path = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        # 1. Header with Title and Action Controls
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=15, pady=(15, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text="📋 Document Structure",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            width=32,
            height=28,
            font=ctk.CTkFont(size=13),
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("black", "white"),
            command=self.refresh
        )
        refresh_btn.grid(row=0, column=1, padx=(0, 6), sticky="e")
        ToolTip(refresh_btn, "Refresh outline structure")

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=32,
            height=28,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("gray80", "gray30"),
            hover_color=("gray70", "gray40"),
            text_color=("black", "white"),
            command=self._on_close_pane
        )
        close_btn.grid(row=0, column=2, sticky="e")
        ToolTip(close_btn, "Hide preview pane")

        # 2. Stats summary bar
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.total_chip = ctk.CTkLabel(
            self.stats_frame,
            text="Files: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray85", "gray25"),
            corner_radius=6,
            height=26
        )
        self.total_chip.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        self.chapters_chip = ctk.CTkLabel(
            self.stats_frame,
            text="Chapters: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray85", "gray25"),
            corner_radius=6,
            height=26
        )
        self.chapters_chip.grid(row=0, column=1, padx=2, sticky="ew")

        self.sections_chip = ctk.CTkLabel(
            self.stats_frame,
            text="Sections: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray85", "gray25"),
            corner_radius=6,
            height=26
        )
        self.sections_chip.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # 3. Graphical Scrollable Tree View
        self.scroll_tree = ctk.CTkScrollableFrame(self, corner_radius=8, fg_color=("gray92", "gray17"))
        self.scroll_tree.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.scroll_tree.grid_columnconfigure(0, weight=1)

        self.show_empty_state()

    def _on_close_pane(self):
        self.parent.show_preview_var.set(False)
        self.parent.apply_preview_visibility()

    def show_empty_state(self, message="Select a ZIP archive or PDF folder on the left to view the bookmark hierarchy."):
        for widget in self.scroll_tree.winfo_children():
            widget.destroy()

        self.total_chip.configure(text="Files: 0")
        self.chapters_chip.configure(text="Chapters: 0")
        self.sections_chip.configure(text="Sections: 0")

        empty_frame = ctk.CTkFrame(self.scroll_tree, fg_color="transparent")
        empty_frame.pack(expand=True, fill="both", pady=70, padx=15)

        icon_label = ctk.CTkLabel(
            empty_frame,
            text="📂",
            font=ctk.CTkFont(size=36)
        )
        icon_label.pack(pady=(0, 8))

        title_label = ctk.CTkLabel(
            empty_frame,
            text="No Document Loaded",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        title_label.pack(pady=(0, 4))

        desc_label = ctk.CTkLabel(
            empty_frame,
            text=message,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=260
        )
        desc_label.pack()

    def update_preview(self, input_path: str):
        self.current_path = input_path
        if not input_path or not os.path.exists(input_path):
            self.show_empty_state()
            return

        items = get_input_structure(input_path)
        if not items:
            self.show_empty_state(message="No valid PDF files found in the selected source.")
            return

        for widget in self.scroll_tree.winfo_children():
            widget.destroy()

        parent_count = sum(1 for item in items if item["type"] == "parent")
        child_count = sum(1 for item in items if item["type"] == "child")

        self.total_chip.configure(text=f"Files: {len(items)}")
        self.chapters_chip.configure(text=f"Chapters: {parent_count}")
        self.sections_chip.configure(text=f"Sections: {child_count}")

        # Render Graphical Tree Cards with hover tooltips for filenames and trailing page numbers
        for item in items:
            t = item["type"]
            title = item["title"]
            fn = item["filename"]
            major = item["major"]
            minor = item["minor"]
            page_str = item.get("page")
            tooltip_text = f"File: {fn}"

            if t == "parent":
                card = ctk.CTkFrame(
                    self.scroll_tree,
                    corner_radius=4,
                    fg_color=("gray85", "gray23"),
                    border_width=1,
                    border_color=("gray75", "gray30")
                )
                card.pack(fill="x", pady=(8, 4), padx=2)
                card.grid_columnconfigure(1, weight=1)

                badge = ctk.CTkLabel(
                    card,
                    text=f"{major:02d}.0" if major is not None else "00.0",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color="#2563eb",
                    text_color="white",
                    corner_radius=4,
                    width=48,
                    height=23
                )
                badge.grid(row=0, column=0, padx=(12, 10), pady=10)

                title_lbl = ctk.CTkLabel(
                    card,
                    text=f"{title}",
                    font=ctk.CTkFont(size=15, weight="bold"),
                    anchor="w",
                    wraplength=280,
                    justify="left"
                )
                title_lbl.grid(row=0, column=1, sticky="w", pady=10, padx=(0, 10))

                ToolTip(card, tooltip_text)
                ToolTip(badge, tooltip_text)
                ToolTip(title_lbl, tooltip_text)

                if page_str:
                    page_lbl = ctk.CTkLabel(
                        card,
                        text=page_str,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=("gray45", "gray65"),
                        anchor="e"
                    )
                    page_lbl.grid(row=0, column=2, padx=(8, 12), pady=10, sticky="e")
                    ToolTip(page_lbl, tooltip_text)

            elif t == "child":
                row = ctk.CTkFrame(
                    self.scroll_tree,
                    corner_radius=4,
                    fg_color=("gray95", "gray20")
                )
                row.pack(fill="x", pady=2, padx=(20, 2))
                row.grid_columnconfigure(1, weight=1)

                prefix_str = f"{major:02d}.{minor}" if major is not None else "--.-"
                prefix_lbl = ctk.CTkLabel(
                    row,
                    text=prefix_str,
                    font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                    text_color=("gray40", "gray65"),
                    anchor="w"
                )
                prefix_lbl.grid(row=0, column=0, padx=(12, 8), pady=7, sticky="w")

                title_lbl = ctk.CTkLabel(
                    row,
                    text=f"{title}",
                    font=ctk.CTkFont(size=13),
                    anchor="w",
                    wraplength=270,
                    justify="left"
                )
                title_lbl.grid(row=0, column=1, sticky="w", pady=7, padx=(0, 10))

                ToolTip(row, tooltip_text)
                ToolTip(prefix_lbl, tooltip_text)
                ToolTip(title_lbl, tooltip_text)

                if page_str:
                    page_lbl = ctk.CTkLabel(
                        row,
                        text=page_str,
                        font=ctk.CTkFont(size=11),
                        text_color=("gray45", "gray65"),
                        anchor="e"
                    )
                    page_lbl.grid(row=0, column=2, padx=(8, 12), pady=7, sticky="e")
                    ToolTip(page_lbl, tooltip_text)

            else:
                top_row = ctk.CTkFrame(
                    self.scroll_tree,
                    corner_radius=6,
                    fg_color=("gray90", "gray22")
                )
                top_row.pack(fill="x", pady=4, padx=2)
                top_row.grid_columnconfigure(1, weight=1)

                badge = ctk.CTkLabel(
                    top_row,
                    text="Top",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color="#64748b",
                    text_color="white",
                    corner_radius=4,
                    width=42,
                    height=20
                )
                badge.grid(row=0, column=0, padx=(10, 8), pady=8)

                title_lbl = ctk.CTkLabel(
                    top_row,
                    text=f"{title}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w",
                    wraplength=280,
                    justify="left"
                )
                title_lbl.grid(row=0, column=1, sticky="w", pady=8, padx=(0, 10))

                ToolTip(top_row, tooltip_text)
                ToolTip(badge, tooltip_text)
                ToolTip(title_lbl, tooltip_text)

                if page_str:
                    page_lbl = ctk.CTkLabel(
                        top_row,
                        text=page_str,
                        font=ctk.CTkFont(size=11),
                        text_color=("gray45", "gray65"),
                        anchor="e"
                    )
                    page_lbl.grid(row=0, column=2, padx=(8, 12), pady=8, sticky="e")
                    ToolTip(page_lbl, tooltip_text)

    def refresh(self):
        input_path = self.parent.input_path_var.get().strip()
        self.update_preview(input_path)
