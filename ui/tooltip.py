import tkinter as tk
import customtkinter as ctk

class ToolTip:
    """Lightweight tooltip for displaying hover text on GUI elements."""
    def __init__(self, widget, text: str, delay_ms: int = 250):
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self.tip_window = None
        self.schedule_id = None
        self.last_event = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")
        self.widget.bind("<Motion>", self._on_motion, add="+")

    def _on_enter(self, event):
        self.last_event = event
        self._cancel_schedule()
        self.schedule_id = self.widget.after(self.delay_ms, self._show_tip)

    def _on_motion(self, event):
        self.last_event = event

    def _on_leave(self, event=None):
        self._cancel_schedule()
        self._hide_tip()

    def _cancel_schedule(self):
        if self.schedule_id:
            try:
                self.widget.after_cancel(self.schedule_id)
            except Exception:
                pass
            self.schedule_id = None

    def _show_tip(self):
        if self.tip_window or not self.text:
            return

        x = (self.last_event.x_root + 12) if self.last_event else (self.widget.winfo_rootx() + 20)
        y = (self.last_event.y_root + 16) if self.last_event else (self.widget.winfo_rooty() + self.widget.winfo_height() + 5)

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#1e293b" if is_dark else "#f8fafc"
        fg_color = "#f1f5f9" if is_dark else "#0f172a"
        border_color = "#475569" if is_dark else "#cbd5e1"

        frame = tk.Frame(tw, background=border_color, padx=1, pady=1)
        frame.pack()

        label = tk.Label(
            frame,
            text=self.text,
            justify="left",
            background=bg_color,
            foreground=fg_color,
            font=("Segoe UI", 9),
            padx=8,
            pady=4
        )
        label.pack()

    def _hide_tip(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None
