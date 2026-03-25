#!/usr/bin/env python3

from __future__ import annotations

import queue
import threading
import traceback
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from conversion_pipeline import build_output_layout, convert_benji2_inputs_to_outputs


class ConversionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SDM26 Converter")
        self.geometry("900x680")
        self.minsize(820, 600)

        self.input_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.output_preview_var = tk.StringVar(value="Select an input path and output directory.")
        self.status_var = tk.StringVar(value="Idle")

        self._queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self._worker: threading.Thread | None = None

        self._build_ui()
        self.after(100, self._process_queue)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        input_frame = ttk.LabelFrame(self, text="Input")
        input_frame.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="nsew")
        input_frame.columnconfigure(0, weight=1)

        ttk.Entry(input_frame, textvariable=self.input_path_var).grid(
            row=0, column=0, padx=8, pady=8, sticky="ew"
        )
        ttk.Button(input_frame, text="Select File", command=self._select_file).grid(
            row=0, column=1, padx=(0, 8), pady=8
        )
        ttk.Button(input_frame, text="Select Folder", command=self._select_folder).grid(
            row=0, column=2, padx=(0, 8), pady=8
        )

        output_frame = ttk.LabelFrame(self, text="Output")
        output_frame.grid(row=1, column=0, padx=12, pady=6, sticky="nsew")
        output_frame.columnconfigure(0, weight=1)

        ttk.Entry(output_frame, textvariable=self.output_dir_var).grid(
            row=0, column=0, padx=8, pady=8, sticky="ew"
        )
        ttk.Button(output_frame, text="Select Output", command=self._select_output_dir).grid(
            row=0, column=1, padx=(0, 8), pady=8
        )
        ttk.Label(
            output_frame,
            textvariable=self.output_preview_var,
            justify="left",
            wraplength=820,
        ).grid(row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="w")

        action_frame = ttk.Frame(self)
        action_frame.grid(row=2, column=0, padx=12, pady=6, sticky="ew")
        action_frame.columnconfigure(1, weight=1)

        self.start_button = ttk.Button(action_frame, text="Start Conversion", command=self._start_conversion)
        self.start_button.grid(row=0, column=0, padx=(0, 8))
        ttk.Button(action_frame, text="Clear Log", command=self._clear_log).grid(row=0, column=1, sticky="w")

        progress_frame = ttk.LabelFrame(self, text="Progress")
        progress_frame.grid(row=3, column=0, padx=12, pady=6, sticky="nsew")
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(2, weight=1)

        ttk.Label(progress_frame, textvariable=self.status_var).grid(
            row=0, column=0, padx=8, pady=(8, 4), sticky="w"
        )
        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress_bar.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")

        self.log_output = ScrolledText(progress_frame, wrap="word", height=20, state="disabled")
        self.log_output.grid(row=2, column=0, padx=8, pady=(0, 8), sticky="nsew")

    def _select_file(self):
        selected = filedialog.askopenfilename(
            title="Select a BENJI2 file",
            filetypes=[("BENJI2 files", "*.benji2"), ("All files", "*.*")],
        )
        if selected:
            self.input_path_var.set(selected)
            self._update_output_preview()

    def _select_folder(self):
        selected = filedialog.askdirectory(title="Select a folder containing BENJI2 files")
        if selected:
            self.input_path_var.set(selected)
            self._update_output_preview()

    def _select_output_dir(self):
        selected = filedialog.askdirectory(title="Select the base output directory")
        if selected:
            self.output_dir_var.set(selected)
            self._update_output_preview()

    def _update_output_preview(self):
        input_path = self.input_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        if not input_path or not output_dir:
            self.output_preview_var.set("Select an input path and output directory.")
            return

        layout = build_output_layout(output_dir, input_path)
        self.output_preview_var.set(
            f"CSV files: {layout.csv_dir}\n"
            f"MoTeC files: {layout.ld_dir}"
        )

    def _set_running(self, is_running: bool):
        state = "disabled" if is_running else "normal"
        self.start_button.configure(state=state)

    def _clear_log(self):
        self.log_output.configure(state="normal")
        self.log_output.delete("1.0", tk.END)
        self.log_output.configure(state="disabled")

    def _append_log(self, message: str):
        self.log_output.configure(state="normal")
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)
        self.log_output.configure(state="disabled")

    def _start_conversion(self):
        input_path = self.input_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()

        if not input_path:
            messagebox.showerror("Missing Input", "Select a BENJI2 file or folder first.")
            return

        if not output_dir:
            messagebox.showerror("Missing Output", "Select an output directory first.")
            return

        if self._worker and self._worker.is_alive():
            return

        self._clear_log()
        self._append_log(f"Input: {input_path}")
        self._append_log(f"Output base: {output_dir}")
        self._update_output_preview()
        self.progress_bar.configure(value=0, maximum=1)
        self.status_var.set("Starting conversion...")
        self._set_running(True)

        self._worker = threading.Thread(
            target=self._run_conversion_worker,
            args=(input_path, output_dir),
            daemon=True,
        )
        self._worker.start()

    def _run_conversion_worker(self, input_path: str, output_dir: str):
        def log(message: str):
            self._queue.put(("log", message))

        def progress(completed: int, total: int, message: str):
            self._queue.put(("progress", (completed, total, message)))

        try:
            layout, results = convert_benji2_inputs_to_outputs(
                input_path,
                output_dir,
                logger=log,
                progress_callback=progress,
            )
            self._queue.put(("done", (layout, results)))
        except Exception as exc:
            self._queue.put(("log", traceback.format_exc()))
            self._queue.put(("error", str(exc)))

    def _process_queue(self):
        try:
            while True:
                kind, payload = self._queue.get_nowait()

                if kind == "log":
                    self._append_log(str(payload))
                elif kind == "progress":
                    completed, total, message = payload  # type: ignore[misc]
                    self.progress_bar.configure(maximum=max(total, 1), value=completed)
                    self.status_var.set(f"{message} ({completed}/{total})")
                elif kind == "done":
                    layout, results = payload  # type: ignore[misc]
                    self._set_running(False)
                    self.progress_bar.configure(value=self.progress_bar.cget("maximum"))
                    self.status_var.set(f"Complete ({len(results)} file(s))")
                    self._append_log(f"Done. Output root: {layout.root_dir}")
                    messagebox.showinfo(
                        "Conversion Complete",
                        f"Converted {len(results)} file(s).\n\nOutput root:\n{layout.root_dir}",
                    )
                elif kind == "error":
                    self._set_running(False)
                    self.status_var.set("Failed")
                    messagebox.showerror("Conversion Failed", str(payload))
        except queue.Empty:
            pass
        finally:
            self.after(100, self._process_queue)


def main():
    app = ConversionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
