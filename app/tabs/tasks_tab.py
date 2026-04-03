import tkinter as tk


class TasksTab(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg="#f6f8fb", padx=22, pady=22)
        self.task_input_var = tk.StringVar()
        self.status_var = tk.StringVar(value="No task added yet.")
        self.tasks: list[str] = []

        self.columnconfigure(0, weight=1)

        card = tk.Frame(self, bg="white", bd=0, highlightthickness=1, highlightbackground="#d5deea")
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)

        tk.Label(
            card,
            text="Tasks Tab",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        tk.Label(
            card,
            text="Task state lives only inside this module.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#537188",
        ).grid(row=1, column=0, sticky="w", padx=18)

        entry_row = tk.Frame(card, bg="white")
        entry_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(18, 10))
        entry_row.columnconfigure(0, weight=1)

        tk.Entry(
            entry_row,
            textvariable=self.task_input_var,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        tk.Button(
            entry_row,
            text="Add Task",
            command=self._add_task,
            bg="#1f6f8b",
            fg="white",
            activebackground="#15576e",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=8,
        ).grid(row=0, column=1)

        self.listbox = tk.Listbox(
            card,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            selectbackground="#c7deea",
            selectforeground="#173245",
            height=10,
        )
        self.listbox.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 10))

        tk.Label(
            card,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg="white",
            fg="#204660",
        ).grid(row=4, column=0, sticky="w", padx=18, pady=(0, 18))

    def _add_task(self) -> None:
        task_name = self.task_input_var.get().strip()
        if not task_name:
            self.status_var.set("Enter a task name before adding.")
            return

        self.tasks.append(task_name)
        self.listbox.insert(tk.END, task_name)
        self.task_input_var.set("")
        self.status_var.set(f"{len(self.tasks)} task(s) stored in this tab.")
