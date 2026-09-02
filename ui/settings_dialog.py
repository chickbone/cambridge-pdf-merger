import customtkinter as ctk

class SettingsWindow(ctk.CTkToplevel):
    """Settings dialog window for appearance and preferences."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Settings")
        self.geometry("420x330")
        self.minsize(390, 300)
        self.resizable(False, False)

        self.after(100, self.lift)
        self.after(100, self.focus_force)

        self.grid_columnconfigure(0, weight=1)
        self._create_widgets()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(
            self,
            text="⚙ Application Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        # Appearance Mode
        theme_label = ctk.CTkLabel(
            card,
            text="Appearance Theme:",
            font=ctk.CTkFont(weight="bold")
        )
        theme_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")

        current_mode = ctk.get_appearance_mode()
        self.theme_menu = ctk.CTkOptionMenu(
            card,
            values=["System", "Dark", "Light"],
            command=self._on_theme_change,
            width=130
        )
        self.theme_menu.set(current_mode)
        self.theme_menu.grid(row=0, column=1, padx=15, pady=(15, 10), sticky="e")

        # Preview Pane Toggle Option
        preview_label = ctk.CTkLabel(
            card,
            text="Show Preview Pane:",
            font=ctk.CTkFont(weight="bold")
        )
        preview_label.grid(row=1, column=0, padx=15, pady=(10, 15), sticky="w")

        self.preview_switch = ctk.CTkSwitch(
            card,
            text="Enabled" if self.parent.show_preview_var.get() else "Disabled",
            variable=self.parent.show_preview_var,
            onvalue=True,
            offvalue=False,
            command=self._on_preview_switch_toggle
        )
        self.preview_switch.grid(row=1, column=1, padx=15, pady=(10, 15), sticky="e")

        # About / Info Section
        about_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        about_frame.grid(row=2, column=0, padx=20, pady=(0, 15), sticky="ew")
        about_frame.grid_columnconfigure(0, weight=1)

        about_text = ctk.CTkLabel(
            about_frame,
            text="Cambridge Core PDF Merger\nMerges chapter PDFs with automatic bookmark hierarchy.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        about_text.grid(row=0, column=0, sticky="w")

        # Done Button
        close_btn = ctk.CTkButton(
            self,
            text="Done",
            width=100,
            command=self.destroy
        )
        close_btn.grid(row=3, column=0, padx=20, pady=(0, 15), sticky="e")

    def _on_theme_change(self, mode: str):
        ctk.set_appearance_mode(mode)

    def _on_preview_switch_toggle(self):
        is_enabled = self.parent.show_preview_var.get()
        self.preview_switch.configure(text="Enabled" if is_enabled else "Disabled")
        self.parent.apply_preview_visibility()
