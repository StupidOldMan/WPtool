import tkinter as tk
from tkinter import ttk

from app.tabs.notes_tab import NotesTab
from app.tabs.numbers_tab import NumbersTab
from app.tabs.tasks_tab import TasksTab


class WPtoolApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("WPtool")
        self.geometry("980x720")
        self.minsize(860, 620)
        self.configure(bg="#e8edf3")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#e8edf3", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=(18, 10),
            font=("Segoe UI", 10, "bold"),
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#10324a", padx=24, pady=20)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title = tk.Label(
            header,
            text="WPtool Workspace",
            font=("Segoe UI Semibold", 20),
            bg="#10324a",
            fg="#f4f7fb",
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = tk.Label(
            header,
            text="Three isolated tabs, each with its own state and source file.",
            font=("Segoe UI", 10),
            bg="#10324a",
            fg="#c7d7e5",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 0))

        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, sticky="nsew", padx=18, pady=18)

        self.notes_tab = NotesTab(notebook)
        self.tasks_tab = TasksTab(notebook)
        self.numbers_tab = NumbersTab(notebook)

        notebook.add(self.notes_tab, text="Splunk")
        notebook.add(self.tasks_tab, text="Tasks")
        notebook.add(self.numbers_tab, text="Numbers")


def run() -> None:
    app = WPtoolApp()
    app.mainloop()
