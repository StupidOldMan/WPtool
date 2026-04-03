import tkinter as tk


class NumbersTab(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg="#f6f8fb", padx=22, pady=22)
        self.left_value_var = tk.StringVar(value="10")
        self.right_value_var = tk.StringVar(value="32")
        self.result_var = tk.StringVar(value="42")

        self.columnconfigure(0, weight=1)

        card = tk.Frame(self, bg="white", bd=0, highlightthickness=1, highlightbackground="#d5deea")
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(1, weight=1)

        tk.Label(
            card,
            text="Numbers Tab",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 6))

        tk.Label(
            card,
            text="This calculator keeps its own independent numeric state.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#537188",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=18)

        tk.Label(card, text="Value A", font=("Segoe UI", 10, "bold"), bg="white", fg="#204660").grid(
            row=2, column=0, sticky="w", padx=18, pady=(18, 8)
        )
        tk.Entry(
            card,
            textvariable=self.left_value_var,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=2, column=1, sticky="ew", padx=(0, 18), pady=(18, 8))

        tk.Label(card, text="Value B", font=("Segoe UI", 10, "bold"), bg="white", fg="#204660").grid(
            row=3, column=0, sticky="w", padx=18, pady=8
        )
        tk.Entry(
            card,
            textvariable=self.right_value_var,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=3, column=1, sticky="ew", padx=(0, 18), pady=8)

        tk.Button(
            card,
            text="Add Values",
            command=self._update_sum,
            bg="#2d936c",
            fg="white",
            activebackground="#236f52",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=8,
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=18, pady=(12, 10))

        tk.Label(
            card,
            textvariable=self.result_var,
            font=("Consolas", 18, "bold"),
            bg="#eef4f8",
            fg="#173245",
            padx=14,
            pady=12,
        ).grid(row=5, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 18))

    def _update_sum(self) -> None:
        try:
            total = float(self.left_value_var.get()) + float(self.right_value_var.get())
        except ValueError:
            self.result_var.set("Enter valid numbers only.")
            return

        self.result_var.set(f"Result: {total:g}")
