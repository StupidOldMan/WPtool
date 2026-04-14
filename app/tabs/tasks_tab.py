import json
import threading
import tkinter as tk
import re
from pathlib import Path
from tkinter import ttk
from tksheet import Sheet


class TasksTab(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, bg="#f6f8fb", padx=22, pady=22)
        self.settings_path = Path(__file__).resolve().parents[2] / "oracle_settings.json"
        self.instant_client_dir = (
            Path(__file__).resolve().parents[2] / "vendor" / "oracle" / "instantclient_19_26"
        )
        self.name_var = tk.StringVar()
        self.host_var = tk.StringVar()
        self.port_var = tk.StringVar(value="1521")
        self.service_name_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.connection_display_var = tk.StringVar()
        self.status_var = tk.StringVar(
            value="Save Oracle connection settings, then run a query to view results."
        )
        self.info_value_vars: dict[str, tk.StringVar] = {}
        self.saved_connections: list[dict[str, str]] = []
        self.selected_connection_index: int = -1
        self.connection = None
        self.run_query_button: tk.Button | None = None
        self.results_sheet: Sheet | None = None
        self.query_input: tk.Text | None = None
        self.connection_combo: ttk.Combobox | None = None
        self._oracle_client_initialized = False

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._load_settings()

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
            text="Oracle Database Query",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 6))

        tk.Label(
            card,
            text="Connect to Oracle DB, send a SQL query, and view the result grid below.",
            font=("Segoe UI", 10),
            bg="white",
            fg="#537188",
        ).grid(row=1, column=0, sticky="w", padx=18)

        selector_frame = tk.Frame(card, bg="white")
        selector_frame.grid(row=2, column=0, sticky="ew", padx=18, pady=(14, 6))
        selector_frame.columnconfigure(1, weight=1)

        tk.Label(
            selector_frame,
            text="Saved Connection",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.connection_combo = ttk.Combobox(
            selector_frame,
            textvariable=self.connection_display_var,
            state="readonly",
            font=("Segoe UI", 10),
        )
        self.connection_combo.grid(row=0, column=1, sticky="ew")
        self.connection_combo.bind("<<ComboboxSelected>>", self._handle_connection_combo_select)

        settings_frame = tk.Frame(card, bg="white")
        settings_frame.grid(row=3, column=0, sticky="ew", padx=18, pady=(8, 10))
        for column in range(5):
            settings_frame.columnconfigure(column, weight=1)

        self._create_info_card(settings_frame, 0, "Name", self.name_var, key="name")
        self._create_info_card(settings_frame, 1, "Host", self.host_var, key="host")
        self._create_info_card(settings_frame, 2, "Port", self.port_var, key="port")
        self._create_info_card(settings_frame, 3, "Service Name", self.service_name_var, key="service_name")
        self._create_info_card(settings_frame, 4, "Username", self.username_var, key="username")

        query_frame = tk.Frame(card, bg="white")
        query_frame.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 8))
        query_frame.columnconfigure(0, weight=1)
        query_frame.rowconfigure(1, weight=1)

        header_row = tk.Frame(query_frame, bg="white")
        header_row.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_row.columnconfigure(0, weight=1)

        tk.Label(
            header_row,
            text="SQL Query",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w")

        tk.Button(
            header_row,
            text="Save Settings",
            command=self._open_settings_window,
            bg="#d7e4ec",
            fg="#173245",
            activebackground="#c5d7e2",
            activeforeground="#173245",
            relief="flat",
            padx=16,
            pady=8,
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        self.run_query_button = tk.Button(
            header_row,
            text="Run Query",
            command=self._start_run_query,
            bg="#2d936c",
            fg="white",
            activebackground="#236f52",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=8,
        )
        self.run_query_button.grid(row=0, column=2, sticky="e", padx=(8, 0))

        self.query_input = tk.Text(
            query_frame,
            height=4,
            wrap="word",
            font=("Consolas", 10),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
            bg="#fbfcfe",
            fg="#173245",
            padx=12,
            pady=10,
        )
        self.query_input.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.query_input.insert("1.0", "select sysdate as CURRENT_TIME from dual")

        results_frame = tk.Frame(
            card,
            bg="white",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
        )
        results_frame.grid(row=5, column=0, sticky="nsew", padx=18, pady=(0, 8))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)

        tk.Label(
            results_frame,
            text="Query Results",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        self.results_sheet = Sheet(
            results_frame,
            height=320,
            headers=["Result"],
            data=[["Oracle results will appear here."]],
            show_row_index=False,
            theme="light blue",
            font=("Segoe UI", 9, "normal"),
            header_font=("Segoe UI", 9, "bold"),
            popup_menu_font=("Segoe UI", 9, "normal"),
            table_wrap="",
            header_wrap="",
            table_bg="#ffffff",
            header_bg="#ffffff",
            frame_bg="#ffffff",
        )
        self.results_sheet.grid(row=1, column=0, sticky="nsew", padx=(12, 12), pady=(0, 10))
        self.results_sheet.enable_bindings()

        tk.Label(
            card,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg="white",
            fg="#204660",
        ).grid(row=6, column=0, sticky="w", padx=18, pady=(0, 18))

        self._refresh_connection_combo()
        self._refresh_info_cards()
        self._set_result_message("Oracle results will appear here.")

    def _normalize_connection(self, payload: dict[str, str]) -> dict[str, str]:
        return {
            "name": str(payload.get("name", "")).strip(),
            "host": str(payload.get("host", "")).strip(),
            "port": str(payload.get("port", "1521")).strip() or "1521",
            "service_name": str(payload.get("service_name", "")).strip(),
            "username": str(payload.get("username", "")).strip(),
            "password": str(payload.get("password", "")).strip(),
        }

    def _default_connection_name(self, index: int, connection: dict[str, str]) -> str:
        service_name = connection.get("service_name", "").strip()
        host = connection.get("host", "").strip()
        if service_name:
            return service_name
        if host:
            return f"{host}-{index + 1}"
        return f"Connection {index + 1}"

    def _load_settings(self) -> None:
        self.saved_connections = []
        self.selected_connection_index = -1

        if not self.settings_path.exists():
            return

        try:
            raw_data = json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        selected_index = -1
        connections: list[dict[str, str]] = []

        if isinstance(raw_data, dict) and "connections" in raw_data:
            raw_connections = raw_data.get("connections", [])
            if isinstance(raw_connections, list):
                connections = [
                    self._normalize_connection(item)
                    for item in raw_connections
                    if isinstance(item, dict)
                ]
            selected_index = int(raw_data.get("selected_index", -1)) if str(raw_data.get("selected_index", "")).strip("-").isdigit() else -1
        elif isinstance(raw_data, dict):
            legacy_connection = self._normalize_connection(raw_data)
            if any(legacy_connection.values()):
                connections = [legacy_connection]
                selected_index = 0

        self.saved_connections = connections
        for index, item in enumerate(self.saved_connections):
            if not item.get("name", "").strip():
                item["name"] = self._default_connection_name(index, item)

        if self.saved_connections:
            if not 0 <= selected_index < len(self.saved_connections):
                selected_index = len(self.saved_connections) - 1
            self.selected_connection_index = selected_index
            self._apply_connection(self.saved_connections[selected_index])

    def _apply_connection(self, connection: dict[str, str]) -> None:
        self.name_var.set(connection.get("name", ""))
        self.host_var.set(connection.get("host", ""))
        self.port_var.set(connection.get("port", "1521") or "1521")
        self.service_name_var.set(connection.get("service_name", ""))
        self.username_var.set(connection.get("username", ""))
        self.password_var.set(connection.get("password", ""))

    def _connection_label(self, connection: dict[str, str]) -> str:
        return connection.get("name", "").strip() or "(unnamed)"

    def _current_connection_payload(self) -> dict[str, str]:
        return self._normalize_connection(
            {
                "name": self.name_var.get(),
                "host": self.host_var.get(),
                "port": self.port_var.get(),
                "service_name": self.service_name_var.get(),
                "username": self.username_var.get(),
                "password": self.password_var.get(),
            }
        )

    def _save_settings(self) -> None:
        payload = self._current_connection_payload()
        has_connection_value = any(
            payload[key]
            for key in ("host", "port", "service_name", "username", "password")
        )
        if not has_connection_value:
            self.status_var.set("Enter at least one Oracle setting before saving.")
            return

        if not payload["name"]:
            payload["name"] = self._default_connection_name(len(self.saved_connections), payload)

        existing_index = next(
            (index for index, item in enumerate(self.saved_connections) if item == payload),
            None,
        )

        if existing_index is None:
            self.saved_connections.append(payload)
            self.selected_connection_index = len(self.saved_connections) - 1
            message = f"Saved Oracle settings #{self.selected_connection_index + 1}."
        else:
            self.selected_connection_index = existing_index
            message = f"Selected existing Oracle settings #{existing_index + 1}."

        self._write_settings_file()
        self.status_var.set(message)
        self._refresh_connection_combo()
        self._refresh_info_cards()
        self.connection = None

    def _write_settings_file(self) -> None:
        storage_payload = {
            "selected_index": self.selected_connection_index,
            "connections": self.saved_connections,
        }
        self.settings_path.write_text(
            json.dumps(storage_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _create_info_card(
        self,
        parent: tk.Misc,
        column: int,
        label: str,
        variable: tk.StringVar,
        key: str | None = None,
    ) -> None:
        frame = tk.Frame(
            parent,
            bg="#f8fbfd",
            highlightthickness=1,
            highlightbackground="#d5deea",
            padx=10,
            pady=8,
        )
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0), pady=(0, 8))
        frame.columnconfigure(1, weight=1)

        tk.Label(
            frame,
            text=f"{label}:",
            font=("Segoe UI", 9, "bold"),
            bg="#f8fbfd",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w", padx=(0, 6))

        value_var = tk.StringVar(value=variable.get().strip() or "(not set)")
        if key is not None:
            self.info_value_vars[key] = value_var

        tk.Label(
            frame,
            textvariable=value_var,
            font=("Segoe UI", 10),
            bg="#f8fbfd",
            fg="#173245",
            anchor="w",
        ).grid(row=0, column=1, sticky="ew")

    def _refresh_info_cards(self) -> None:
        for key, variable in (
            ("name", self.name_var),
            ("host", self.host_var),
            ("port", self.port_var),
            ("service_name", self.service_name_var),
            ("username", self.username_var),
        ):
            info_var = self.info_value_vars.get(key)
            if info_var is not None:
                info_var.set(variable.get().strip() or "(not set)")

    def _refresh_connection_combo(self) -> None:
        if self.connection_combo is None:
            return

        values = [self._connection_label(item) for item in self.saved_connections]
        self.connection_combo["values"] = values

        if values and 0 <= self.selected_connection_index < len(values):
            self.connection_display_var.set(values[self.selected_connection_index])
        elif values:
            self.selected_connection_index = 0
            self.connection_display_var.set(values[0])
        else:
            self.connection_display_var.set("")

    def _handle_connection_combo_select(self, _event: tk.Event | None = None) -> None:
        selected_label = self.connection_display_var.get().strip()
        if not selected_label:
            return

        for index, item in enumerate(self.saved_connections):
            if self._connection_label(item) == selected_label:
                self.selected_connection_index = index
                self._apply_connection(item)
                self._refresh_info_cards()
                self.connection = None
                self.status_var.set(f"Loaded Oracle settings #{index + 1}.")
                return

    def _open_settings_window(self) -> None:
        window = tk.Toplevel(self)
        window.title("Oracle Settings")
        window.geometry("980x620")
        window.minsize(900, 560)
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
            text="Oracle Connection Settings",
            font=("Segoe UI Semibold", 16),
            bg="white",
            fg="#16354a",
        ).grid(row=0, column=0, sticky="w")

        entry_grid = tk.Frame(frame, bg="white")
        entry_grid.grid(row=1, column=0, sticky="ew", pady=(16, 16))
        for column in range(6):
            entry_grid.columnconfigure(column, weight=1)

        self._create_settings_entry(entry_grid, 0, "Name", self.name_var)
        self._create_settings_entry(entry_grid, 1, "Host", self.host_var)
        self._create_settings_entry(entry_grid, 2, "Port", self.port_var)
        self._create_settings_entry(entry_grid, 3, "Service Name", self.service_name_var)
        self._create_settings_entry(entry_grid, 4, "Username", self.username_var)
        self._create_settings_entry(entry_grid, 5, "Password", self.password_var)

        saved_frame = tk.Frame(
            frame,
            bg="#f8fbfd",
            padx=16,
            pady=14,
            highlightthickness=1,
            highlightbackground="#d5deea",
        )
        saved_frame.grid(row=2, column=0, sticky="nsew")
        saved_frame.columnconfigure(0, weight=1)
        saved_frame.rowconfigure(1, weight=1)

        tk.Label(
            saved_frame,
            text="Saved Connections",
            font=("Segoe UI", 10, "bold"),
            bg="#f8fbfd",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        saved_tree = ttk.Treeview(
            saved_frame,
            columns=("name", "host", "port", "service_name", "username", "password"),
            show="headings",
            style="Oracle.Treeview",
        )
        for column, title, width in (
            ("name", "NAME", 140),
            ("host", "HOST", 180),
            ("port", "PORT", 90),
            ("service_name", "ServiceName", 180),
            ("username", "Username", 150),
            ("password", "Password", 150),
        ):
            saved_tree.heading(column, text=title)
            saved_tree.column(column, width=width, anchor="w", stretch=True)
        saved_tree.grid(row=1, column=0, sticky="nsew")

        saved_y_scroll = ttk.Scrollbar(saved_frame, orient="vertical", command=saved_tree.yview)
        saved_y_scroll.grid(row=1, column=1, sticky="ns")
        saved_x_scroll = ttk.Scrollbar(saved_frame, orient="horizontal", command=saved_tree.xview)
        saved_x_scroll.grid(row=2, column=0, sticky="ew")
        saved_tree.configure(yscrollcommand=saved_y_scroll.set, xscrollcommand=saved_x_scroll.set)

        self._populate_saved_connections_tree(saved_tree)
        saved_tree.bind(
            "<<TreeviewSelect>>",
            lambda _event: self._handle_saved_connection_select(saved_tree),
        )

        hint_text = "Select a saved row to load it into the input boxes above."
        if not self.saved_connections:
            hint_text = "No saved Oracle connections yet. Enter values above and press Save."
        tk.Label(
            saved_frame,
            text=hint_text,
            font=("Segoe UI", 9),
            bg="#f8fbfd",
            fg="#537188",
        ).grid(row=3, column=0, sticky="w", pady=(10, 0))

        button_row = tk.Frame(frame, bg="white")
        button_row.grid(row=3, column=0, sticky="e", pady=(18, 0))

        tk.Button(
            button_row,
            text="Delete",
            command=lambda: self._delete_settings_from_window(saved_tree),
            bg="#d66c5f",
            fg="white",
            activebackground="#b65347",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=10,
        ).grid(row=0, column=0, padx=(0, 8))

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
        ).grid(row=0, column=1)

    def _create_settings_entry(
        self,
        parent: tk.Misc,
        column: int,
        label: str,
        variable: tk.StringVar,
    ) -> None:
        entry_frame = tk.Frame(parent, bg="white")
        entry_frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 8, 0))
        entry_frame.columnconfigure(0, weight=1)

        tk.Label(
            entry_frame,
            text=label,
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#204660",
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        tk.Entry(
            entry_frame,
            textvariable=variable,
            font=("Segoe UI", 11),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#b7c7d8",
            highlightcolor="#2d6a91",
        ).grid(row=1, column=0, sticky="ew")

    def _populate_saved_connections_tree(self, tree: ttk.Treeview) -> None:
        tree.delete(*tree.get_children())
        for index, item in enumerate(self.saved_connections):
            tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    item.get("name", ""),
                    item.get("host", ""),
                    item.get("port", ""),
                    item.get("service_name", ""),
                    item.get("username", ""),
                    item.get("password", ""),
                ),
            )

        if 0 <= self.selected_connection_index < len(self.saved_connections):
            selected_iid = str(self.selected_connection_index)
            tree.selection_set(selected_iid)
            tree.focus(selected_iid)

    def _handle_saved_connection_select(self, tree: ttk.Treeview) -> None:
        selected_items = tree.selection()
        if not selected_items:
            return

        selected_index = int(selected_items[0])
        if not 0 <= selected_index < len(self.saved_connections):
            return

        self.selected_connection_index = selected_index
        self._apply_connection(self.saved_connections[selected_index])
        self._refresh_connection_combo()
        self._refresh_info_cards()
        self.connection = None
        self.status_var.set(f"Loaded Oracle settings #{selected_index + 1}.")

    def _save_settings_from_window(self, window: tk.Toplevel) -> None:
        self._save_settings()
        for child in window.winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Frame):
                        for widget in grandchild.winfo_children():
                            if isinstance(widget, ttk.Treeview):
                                self._populate_saved_connections_tree(widget)

    def _delete_settings_from_window(self, tree: ttk.Treeview) -> None:
        selected_items = tree.selection()
        if not selected_items:
            self.status_var.set("Select a saved Oracle connection to delete.")
            return

        selected_index = int(selected_items[0])
        if not 0 <= selected_index < len(self.saved_connections):
            self.status_var.set("The selected Oracle connection is no longer available.")
            return

        deleted_name = self.saved_connections[selected_index].get("name", "").strip() or f"#{selected_index + 1}"
        del self.saved_connections[selected_index]

        if not self.saved_connections:
            self.selected_connection_index = -1
            self.name_var.set("")
            self.host_var.set("")
            self.port_var.set("1521")
            self.service_name_var.set("")
            self.username_var.set("")
            self.password_var.set("")
        else:
            if selected_index < self.selected_connection_index:
                self.selected_connection_index -= 1
            if self.selected_connection_index >= len(self.saved_connections):
                self.selected_connection_index = len(self.saved_connections) - 1
            self._apply_connection(self.saved_connections[self.selected_connection_index])

        self._write_settings_file()
        self._populate_saved_connections_tree(tree)
        self._refresh_connection_combo()
        self._refresh_info_cards()
        self.connection = None
        self.status_var.set(f"Deleted Oracle settings {deleted_name}.")

    def _set_result_message(self, message: str) -> None:
        self._set_result_rows(["Result"], [(message,)])

    def _set_result_rows(self, columns: list[str], rows: list[tuple[str, ...]]) -> None:
        if self.results_sheet is None:
            return

        data = [list(row) for row in rows] if rows else [["" for _ in columns]]
        total_columns = max(len(columns), 1)
        total_rows = max(len(data), 1)
        self.results_sheet.headers(columns, redraw=False)
        self.results_sheet.set_sheet_data_and_display_dimensions(
            total_rows=total_rows,
            total_columns=total_columns,
        )
        self.results_sheet.set_sheet_data(
            data,
            redraw=False,
            reset_col_positions=True,
            reset_row_positions=True,
        )
        self.results_sheet.set_all_column_widths(width=160, redraw=True)

    def _start_run_query(self) -> None:
        worker = threading.Thread(target=self._run_query_worker, daemon=True)
        worker.start()
        self.status_var.set("Running Oracle query...")

    def _run_query_worker(self) -> None:
        try:
            rows, columns = self.run_query()
        except Exception as exc:
            message = str(exc)
            self.after(0, lambda msg=message: self._handle_query_error(msg))
            return

        self.after(0, lambda cols=columns, result_rows=rows: self._handle_query_success(cols, result_rows))

    def _handle_query_success(self, columns: list[str], rows: list[tuple[str, ...]]) -> None:
        self.status_var.set(f"Oracle query completed. {len(rows)} row(s) returned.")
        self._set_result_rows(columns, rows or [tuple("" for _ in columns)])

    def _handle_query_error(self, message: str) -> None:
        self.status_var.set("Oracle query failed.")
        self._set_result_message(message)

    def create_oracle_connection(self):
        try:
            import oracledb
        except ImportError as exc:
            raise RuntimeError(
                "python-oracledb is not installed. Install it with: python -m pip install oracledb --upgrade"
            ) from exc

        if not self._oracle_client_initialized:
            if not self.instant_client_dir.exists():
                raise RuntimeError(
                    f"Oracle Instant Client was not found at {self.instant_client_dir}."
                )
            try:
                oracledb.init_oracle_client(lib_dir=str(self.instant_client_dir))
            except oracledb.ProgrammingError:
                pass
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to initialize Oracle Instant Client from {self.instant_client_dir}: {exc}"
                ) from exc
            self._oracle_client_initialized = True

        host = self.host_var.get().strip()
        port = self.port_var.get().strip() or "1521"
        service_name = self.service_name_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        missing = [
            name
            for name, value in (
                ("host", host),
                ("service_name", service_name),
                ("username", username),
                ("password", password),
            )
            if not value
        ]
        if missing:
            raise RuntimeError("Missing Oracle connection settings: " + ", ".join(missing))

        dsn = f"{host}:{port}/{service_name}"
        return oracledb.connect(user=username, password=password, dsn=dsn)

    def run_query(self) -> tuple[list[tuple[str, ...]], list[str]]:
        if self.connection is None:
            self.connection = self.create_oracle_connection()

        if self.query_input is None:
            raise RuntimeError("Query input is not available.")

        sql = self.query_input.get("1.0", tk.END).strip()
        sql = sql.rstrip()
        if sql.endswith(";"):
            sql = sql[:-1].rstrip()
        if not sql:
            raise RuntimeError("Enter a SQL query before running.")

        normalized_sql = re.sub(r"^\s+", "", sql)
        normalized_sql = re.sub(r"^/\*.*?\*/\s*", "", normalized_sql, flags=re.DOTALL)
        normalized_sql = re.sub(r"^(--[^\n]*\n\s*)+", "", normalized_sql)
        lowered_sql = normalized_sql.lower()
        if not (lowered_sql.startswith("select") or lowered_sql.startswith("with")):
            raise RuntimeError("Only SELECT queries are allowed in this tab.")

        cursor = self.connection.cursor()
        try:
            cursor.execute(sql)
            description = cursor.description
            if description is None:
                self.connection.commit()
                return [("Statement executed successfully.",)], ["Result"]

            columns = [item[0] for item in description]
            fetched_rows = cursor.fetchmany(200)
            rows = [tuple("" if value is None else str(value) for value in row) for row in fetched_rows]
            return rows, columns
        finally:
            cursor.close()
