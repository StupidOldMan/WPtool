import base64
from datetime import datetime
import json
import os
import ssl
import threading
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
import xml.etree.ElementTree as ET
from tkinter import ttk


class NotesTab(tk.Frame):
    AUTH_LOGIN_URL = "http://smiot.samsungds.net:8089/services/auth/login"

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg="#f6f8fb", padx=22, pady=22)
        self.settings_path = Path(__file__).resolve().parents[2] / "splunk_settings.json"
        self.index_settings_path = Path(__file__).resolve().parents[2] / "index_settings.txt"
        self.index_var = tk.StringVar(value="main")
        self.text_var = tk.StringVar(value="error OR failed")
        self.start_time_var = tk.StringVar(value="20260401 000000")
        self.end_time_var = tk.StringVar(value="20260401 235959")
        self.splunk_username_var = tk.StringVar()
        self.splunk_password_var = tk.StringVar()
        self.index_settings_content = ""
        self.status_var = tk.StringVar(
            value="Set your Splunk connection in Settings, then click Run Search."
        )
        self.index_options: list[str] = []
        self.index_combo: ttk.Combobox | None = None
        self.query_text: tk.Text | None = None
        self.results_tree: ttk.Treeview | None = None
        self.run_button: tk.Button | None = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        tree_style = ttk.Style(self)
        tree_style.configure("Results.Treeview", rowheight=24, font=("Segoe UI", 9))
        tree_style.configure("Results.Treeview.Heading", font=("Segoe UI", 9, "bold"))

        card = tk.Frame(
            self,
            bg="white",
            bd=0,
            highlightthickness=1,
            highlightbackground="#d5deea",
        )
        card.grid(row=0, column=0, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.rowconfigure(6, weight=1)

        tk.Label(
            card,
            text="Splunk Message Search",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        tk.Label(
            card,
            text="Enter the Splunk index on the left and the message text on the right.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#537188",
        ).grid(row=1, column=0, sticky="w", padx=18)

        input_row = tk.Frame(card, bg="white")
        input_row.grid(row=2, column=0, sticky="ew", padx=18, pady=(14, 10))
        input_row.columnconfigure(0, weight=1)
        input_row.columnconfigure(1, weight=1)

        left_box = tk.Frame(
            input_row,
            bg="#f8fbfd",
            highlightthickness=1,
            highlightbackground="#d5deea",
            padx=14,
            pady=12,
        )
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left_box.columnconfigure(0, weight=1)

        right_box = tk.Frame(
            input_row,
            bg="#f8fbfd",
            highlightthickness=1,
            highlightbackground="#d5deea",
            padx=14,
            pady=12,
        )
        right_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right_box.columnconfigure(0, weight=1)

        tk.Label(
            left_box,
            text="Index",
            font=("Segoe UI", 10, "bold"),
            bg="#f8fbfd",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w")
        self.index_combo = ttk.Combobox(
            left_box,
            textvariable=self.index_var,
            font=("Segoe UI", 11),
            state="readonly",
        )
        self.index_combo.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        tk.Label(
            right_box,
            text="Text (literal)",
            font=("Segoe UI", 10, "bold"),
            bg="#f8fbfd",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w")
        tk.Entry(
            right_box,
            textvariable=self.text_var,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=1, column=0, sticky="ew", pady=(8, 0))

        time_row = tk.Frame(right_box, bg="#f8fbfd")
        time_row.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        time_row.columnconfigure(0, weight=1)
        time_row.columnconfigure(1, weight=1)

        start_box = tk.Frame(time_row, bg="#f8fbfd")
        start_box.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        start_box.columnconfigure(0, weight=1)

        end_box = tk.Frame(time_row, bg="#f8fbfd")
        end_box.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        end_box.columnconfigure(0, weight=1)

        tk.Label(
            start_box,
            text="Start",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fbfd",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w")
        tk.Entry(
            start_box,
            textvariable=self.start_time_var,
            font=("Segoe UI", 10),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0))

        tk.Label(
            end_box,
            text="End",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fbfd",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w")
        tk.Entry(
            end_box,
            textvariable=self.end_time_var,
            font=("Segoe UI", 10),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0))

        toolbar = tk.Frame(card, bg="white")
        toolbar.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 6))
        toolbar.columnconfigure(0, weight=1)

        tk.Label(
            toolbar,
            text="Generated Query",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w")

        self.run_button = tk.Button(
            toolbar,
            text="Run Search",
            command=self._start_search,
            bg="#1f6f8b",
            fg="white",
            activebackground="#15576e",
            activeforeground="white",
            relief="flat",
            padx=14,
            pady=8,
        )
        self.run_button.grid(row=0, column=1, sticky="e")

        settings_button = tk.Button(
            toolbar,
            text="Splunk Setting",
            command=self._open_settings_window,
            bg="#d7e4ec",
            fg="#173245",
            activebackground="#c5d7e2",
            activeforeground="#173245",
            relief="flat",
            padx=14,
            pady=8,
        )
        settings_button.grid(row=0, column=2, sticky="e", padx=(8, 0))

        index_settings_button = tk.Button(
            toolbar,
            text="Index Setting",
            command=self._open_index_settings_window,
            bg="#d7e4ec",
            fg="#173245",
            activebackground="#c5d7e2",
            activeforeground="#173245",
            relief="flat",
            padx=14,
            pady=8,
        )
        index_settings_button.grid(row=0, column=3, sticky="e", padx=(8, 0))

        self.query_text = tk.Text(
            card,
            height=1,
            wrap="none",
            font=("Consolas", 9),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
            bg="#eef4f8",
            fg="#173245",
            padx=14,
            pady=12,
        )
        self.query_text.grid(row=4, column=0, sticky="ew", padx=18, pady=(4, 8))

        tk.Label(
            card,
            text="Splunk Results",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=5, column=0, sticky="w", padx=18)

        results_frame = tk.Frame(
            card,
            bg="white",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
        )
        results_frame.grid(row=6, column=0, sticky="nsew", padx=18, pady=(6, 8))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        columns = ("time", "host", "source", "sourcetype", "raw")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Results.Treeview",
        )
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        headings = {
            "time": "_time",
            "host": "host",
            "source": "source",
            "sourcetype": "sourcetype",
            "raw": "_raw",
        }
        widths = {
            "time": 150,
            "host": 120,
            "source": 140,
            "sourcetype": 120,
            "raw": 320,
        }
        for key in columns:
            self.results_tree.heading(key, text=headings[key])
            self.results_tree.column(key, width=widths[key], anchor="w", stretch=True)

        y_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.results_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        tk.Label(
            card,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg="white",
            fg="#537188",
        ).grid(row=7, column=0, sticky="w", padx=18, pady=(0, 18))

        self.index_var.trace_add("write", lambda *_: self._refresh_query())
        self.text_var.trace_add("write", lambda *_: self._refresh_query())
        self.start_time_var.trace_add("write", lambda *_: self._refresh_query())
        self.end_time_var.trace_add("write", lambda *_: self._refresh_query())
        self._load_settings()
        self._load_index_settings()
        self._refresh_index_options()
        self._refresh_query()
        self._set_results_rows([])

    def _build_query(self) -> str:
        index_value = self.index_var.get().strip() or "<index>"
        text_value = self.text_var.get().strip() or "<text>"
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()

        try:
            earliest = self._format_splunk_absolute_time(start_time) if start_time else "<start_time>"
            latest = self._format_splunk_absolute_time(end_time) if end_time else "<end_time>"
        except ValueError:
            earliest = "<invalid_start_time>"
            latest = "<invalid_end_time>"

        return (
            f'search index="{self._escape_literal(index_value)}" '
            f'"{self._escape_literal(text_value)}" '
            f'earliest="{earliest}" latest="{latest}" '
            "| table _time host source sourcetype _raw"
        )

    def _refresh_query(self) -> None:
        if self.query_text is None:
            return

        self.query_text.config(state="normal")
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert("1.0", self._build_query())
        self.query_text.config(state="disabled")

    def _set_results_rows(self, rows: list[dict[str, str]]) -> None:
        if self.results_tree is None:
            return

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for row in rows:
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    row.get("_time", ""),
                    row.get("host", ""),
                    row.get("source", ""),
                    row.get("sourcetype", ""),
                    row.get("_raw", ""),
                ),
            )

    def _load_settings(self) -> None:
        settings = {
            "username": os.getenv("SPLUNK_USERNAME", "").strip(),
            "password": os.getenv("SPLUNK_PASSWORD", "").strip(),
        }

        if self.settings_path.exists():
            try:
                data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = {}

            if isinstance(data, dict):
                settings["username"] = str(data.get("username", settings["username"])).strip()
                settings["password"] = str(data.get("password", settings["password"])).strip()

        self.splunk_username_var.set(settings["username"])
        self.splunk_password_var.set(settings["password"])

    def _save_settings(self) -> None:
        payload = {
            "username": self.splunk_username_var.get().strip(),
            "password": self.splunk_password_var.get().strip(),
        }
        self.settings_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _load_index_settings(self) -> None:
        if not self.index_settings_path.exists():
            self.index_settings_content = ""
            self.index_options = []
            return

        try:
            self.index_settings_content = self.index_settings_path.read_text(encoding="utf-8")
        except OSError:
            self.index_settings_content = ""
            self.index_options = []
            return

        self.index_options = [
            line.strip()
            for line in self.index_settings_content.splitlines()
            if line.strip()
        ]

    def _save_index_settings(self, content: str) -> None:
        self.index_settings_path.write_text(content, encoding="utf-8")
        self.index_settings_content = content
        self.index_options = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]
        self._refresh_index_options()

    def _refresh_index_options(self) -> None:
        if self.index_combo is None:
            return

        self.index_combo["values"] = self.index_options
        if self.index_options:
            if self.index_var.get().strip() not in self.index_options:
                self.index_var.set(self.index_options[0])
        else:
            self.index_var.set("")

    def _open_settings_window(self) -> None:
        window = tk.Toplevel(self)
        window.title("Splunk Settings")
        window.geometry("560x420")
        window.minsize(520, 380)
        window.resizable(True, True)
        window.transient(self.winfo_toplevel())
        window.grab_set()
        window.configure(bg="#f6f8fb")

        frame = tk.Frame(
            window,
            bg="white",
            padx=24,
            pady=24,
            highlightthickness=1,
            highlightbackground="#d5deea",
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.columnconfigure(0, weight=1)

        tk.Label(
            frame,
            text="Splunk Connection Settings",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, sticky="w")

        self._create_settings_entry(frame, 1, "SPLUNK_USERNAME", self.splunk_username_var, False)
        self._create_settings_entry(frame, 3, "SPLUNK_PASSWORD", self.splunk_password_var, True)

        button_row = tk.Frame(frame, bg="white")
        button_row.grid(row=5, column=0, sticky="e", pady=(18, 0))

        tk.Button(
            button_row,
            text="Save",
            command=lambda: self._save_settings_from_window(window),
            bg="#1f6f8b",
            fg="white",
            activebackground="#15576e",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
        ).grid(row=0, column=0)

    def _open_index_settings_window(self) -> None:
        window = tk.Toplevel(self)
        window.title("Index Settings")
        window.geometry("620x460")
        window.minsize(560, 400)
        window.resizable(True, True)
        window.transient(self.winfo_toplevel())
        window.grab_set()
        window.configure(bg="#f6f8fb")

        frame = tk.Frame(
            window,
            bg="white",
            padx=24,
            pady=24,
            highlightthickness=1,
            highlightbackground="#d5deea",
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        tk.Label(
            frame,
            text="Index Settings",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            frame,
            text="Enter one or more lines. Saved content will be loaded automatically next time.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#537188",
        ).grid(row=1, column=0, sticky="w", pady=(8, 12))

        text_area = tk.Text(
            frame,
            wrap="word",
            font=("Consolas", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
            bg="#fbfcfe",
            fg="#173245",
            padx=14,
            pady=12,
        )
        text_area.grid(row=2, column=0, sticky="nsew")
        text_area.insert("1.0", self.index_settings_content)

        button_row = tk.Frame(frame, bg="white")
        button_row.grid(row=3, column=0, sticky="e", pady=(18, 0))

        tk.Button(
            button_row,
            text="Save",
            command=lambda: self._save_index_settings_from_window(window, text_area),
            bg="#1f6f8b",
            fg="white",
            activebackground="#15576e",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
        ).grid(row=0, column=0)

    def _create_settings_entry(
        self,
        parent: tk.Misc,
        row: int,
        label: str,
        variable: tk.StringVar,
        masked: bool,
    ) -> None:
        tk.Label(
            parent,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=row, column=0, sticky="w", pady=(18, 8))
        tk.Entry(
            parent,
            textvariable=variable,
            font=("Segoe UI", 12),
            show="*" if masked else "",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=row + 1, column=0, sticky="ew", ipady=4)

    def _save_settings_from_window(self, window: tk.Toplevel) -> None:
        self._save_settings()
        self.status_var.set(f"Saved Splunk settings to {self.settings_path.name}.")
        window.destroy()

    def _save_index_settings_from_window(self, window: tk.Toplevel, text_area: tk.Text) -> None:
        content = text_area.get("1.0", tk.END).rstrip()
        self._save_index_settings(content)
        self.status_var.set(f"Saved index settings to {self.index_settings_path.name}.")
        window.destroy()

    def _start_search(self) -> None:
        try:
            self._validate_time_range()
        except ValueError as exc:
            self.status_var.set("Splunk search failed.")
            self._set_results_rows(
                [{"_time": "", "host": "error", "source": "", "sourcetype": "", "_raw": str(exc)}]
            )
            return

        if self.run_button is not None:
            self.run_button.config(state="disabled")

        self.status_var.set("Searching Splunk...")
        self._set_results_rows(
            [{"_time": "", "host": "info", "source": "", "sourcetype": "", "_raw": "Searching Splunk..."}]
        )
        worker = threading.Thread(target=self._run_search, daemon=True)
        worker.start()

    def _run_search(self) -> None:
        try:
            results = self._fetch_splunk_results()
        except Exception as exc:
            self.after(0, lambda: self._finish_search_error(str(exc)))
            return

        self.after(0, lambda: self._finish_search_success(results))

    def _fetch_splunk_results(self) -> str:
        username = self.splunk_username_var.get().strip()
        password = self.splunk_password_var.get().strip()
        verify_ssl = os.getenv("SPLUNK_VERIFY_SSL", "true").strip().lower()

        missing = [
            name
            for name, value in (
                ("SPLUNK_USERNAME", username),
                ("SPLUNK_PASSWORD", password),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Missing Splunk connection settings: "
                + ", ".join(missing)
                + ". Open Settings, save them, and run again."
            )

        earliest_time, latest_time = self._validate_time_range()
        session_key = self._get_session_key(username, password, verify_ssl)

        payload = urllib.parse.urlencode(
            {
                "search": self._build_search_expression(),
                "earliest_time": str(int(earliest_time.timestamp())),
                "latest_time": str(int(latest_time.timestamp())),
                "output_mode": "json",
                "exec_mode": "oneshot",
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            url=self._build_search_export_url(),
            data=payload,
            method="POST",
        )
        request.add_header(
            "Authorization",
            f"Splunk {session_key}",
        )
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        context = None
        if verify_ssl not in {"1", "true", "yes"}:
            context = ssl._create_unverified_context()

        try:
            with urllib.request.urlopen(request, context=context, timeout=30) as response:
                raw_body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Splunk HTTP {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Unable to reach Splunk: {exc.reason}") from exc

        return self._format_results(raw_body)

    def _get_session_key(self, username: str, password: str, verify_ssl: str) -> str:
        payload = urllib.parse.urlencode(
            {
                "username": username,
                "password": password,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            url=self.AUTH_LOGIN_URL,
            data=payload,
            method="POST",
        )
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        request.add_header(
            "Authorization",
            "Basic " + base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii"),
        )

        context = None
        if verify_ssl not in {"1", "true", "yes"}:
            context = ssl._create_unverified_context()

        try:
            with urllib.request.urlopen(request, context=context, timeout=30) as response:
                raw_body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Splunk login HTTP {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Unable to reach Splunk login endpoint: {exc.reason}") from exc

        try:
            xml_root = ET.fromstring(raw_body)
        except ET.ParseError as exc:
            raise RuntimeError(f"Unable to parse Splunk login response: {raw_body}") from exc

        session_key = xml_root.findtext(".//sessionKey")
        if not session_key:
            raise RuntimeError(f"Splunk login succeeded but no sessionKey was returned: {raw_body}")

        return session_key.strip()

    def _build_search_export_url(self) -> str:
        parsed = urllib.parse.urlparse(self.AUTH_LOGIN_URL)
        if not parsed.scheme or not parsed.netloc:
            raise RuntimeError("AUTH_LOGIN_URL is invalid.")

        return f"{parsed.scheme}://{parsed.netloc}/services/search/jobs/export"

    def _build_search_expression(self) -> str:
        index_value = self.index_var.get().strip()
        text_value = self.text_var.get().strip()

        parts = ["search"]
        if index_value:
            parts.append(f'index="{self._escape_literal(index_value)}"')
        if text_value:
            parts.append(f'"{self._escape_literal(text_value)}"')
        parts.append("| table _time host source sourcetype _raw")
        return " ".join(parts)

    def _validate_time_range(self) -> tuple[datetime, datetime]:
        try:
            start_time = self._parse_user_time(self.start_time_var.get().strip())
        except ValueError as exc:
            raise ValueError("Start time must use YYYYMMDD HH24MISS.") from exc

        try:
            end_time = self._parse_user_time(self.end_time_var.get().strip())
        except ValueError as exc:
            raise ValueError("End time must use YYYYMMDD HH24MISS.") from exc

        if start_time > end_time:
            raise ValueError("Start time must be earlier than or equal to End time.")

        return start_time, end_time

    def _parse_user_time(self, value: str) -> datetime:
        return datetime.strptime(value, "%Y%m%d %H%M%S")

    def _format_splunk_absolute_time(self, value: str) -> str:
        parsed = self._parse_user_time(value)
        return f"{parsed.month}/{parsed.day}/{parsed.year}:{parsed:%H:%M:%S}"

    def _escape_literal(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    def _format_results(self, raw_body: str) -> list[dict[str, str]]:
        lines = [line for line in raw_body.splitlines() if line.strip()]
        if not lines:
            return [{"_time": "", "host": "info", "source": "", "sourcetype": "", "_raw": "No results returned from Splunk."}]

        formatted: list[dict[str, str]] = []
        for line in lines:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                formatted.append(
                    {"_time": "", "host": "", "source": "", "sourcetype": "", "_raw": line}
                )
                continue

            result = item.get("result")
            if isinstance(result, dict):
                formatted.append(
                    {
                        "_time": str(result.get("_time", "")),
                        "host": str(result.get("host", "")),
                        "source": str(result.get("source", "")),
                        "sourcetype": str(result.get("sourcetype", "")),
                        "_raw": str(result.get("_raw", "")),
                    }
                )
            elif "messages" in item:
                formatted.append(
                    {
                        "_time": "",
                        "host": "message",
                        "source": "",
                        "sourcetype": "",
                        "_raw": json.dumps(item["messages"], ensure_ascii=False),
                    }
                )
            else:
                formatted.append(
                    {
                        "_time": "",
                        "host": "",
                        "source": "",
                        "sourcetype": "",
                        "_raw": json.dumps(item, ensure_ascii=False),
                    }
                )

        return formatted

    def _finish_search_success(self, results: list[dict[str, str]]) -> None:
        if self.run_button is not None:
            self.run_button.config(state="normal")

        self.status_var.set("Splunk search completed.")
        self._set_results_rows(results)

    def _finish_search_error(self, message: str) -> None:
        if self.run_button is not None:
            self.run_button.config(state="normal")

        self.status_var.set("Splunk search failed.")
        self._set_results_rows(
            [{"_time": "", "host": "error", "source": "", "sourcetype": "", "_raw": message}]
        )
