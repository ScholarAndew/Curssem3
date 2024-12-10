import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

def get_folder_size(folder_path):
    total_size = 0
    try:
        for root_dir, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
    except (FileNotFoundError, PermissionError):
        pass
    return total_size

def get_folder_info(folder_path):
    total_size = 0
    file_types = defaultdict(int)
    files_info = []

    try:
        for root_dir, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_extension = os.path.splitext(file)[1].lower()
                    file_types[file_extension] += 1
                    files_info.append({"name": file, "size": file_size})
    except (FileNotFoundError, PermissionError) as e:
        messagebox.showerror("Error", f"Failed to access {folder_path}: {e}")

    return total_size, dict(file_types), files_info

def populate_folder(tree, parent, folder_path):
    try:
        entries = os.listdir(folder_path)
        folders = [entry for entry in entries if os.path.isdir(os.path.join(folder_path, entry))]
        files = [entry for entry in entries if os.path.isfile(os.path.join(folder_path, entry))]
        for folder in folders:
            folder_path_full = os.path.join(folder_path, folder)
            folder_size_total = get_folder_size(folder_path_full)
            node = tree.insert(
                parent,
                "end",
                text=folder,
                values=("", f"{folder_size_total / (1024 * 1024):.2f} MB"),
            )
            tree_data[node] = folder_path_full
            populate_folder(tree, node, folder_path_full)
        for file in files:
            file_path_full = os.path.join(folder_path, file)
            file_size_mb = os.path.getsize(file_path_full) / (1024 * 1024)
            tree.insert(parent, "end", text=file, values=(f"{file_size_mb:.2f} MB", "N/A"))
    except (FileNotFoundError, PermissionError) as e:
        messagebox.showerror("Error", f"Failed to scan {folder_path}: {e}")

def start_scan():
    base_folder = filedialog.askdirectory(title="Select a folder to scan")
    if not base_folder:
        return

    for item in tree.get_children():
        tree.delete(item)
    tree_data.clear()

    total_size, file_types, files_info = get_folder_info(base_folder)

    root_node = tree.insert("", "end", text=base_folder, values=("Root Folder",))
    tree_data[root_node] = base_folder
    populate_folder(tree, root_node, base_folder)

    total_size_mb = total_size / (1024 * 1024)
    summary_text.set(f"Total size (with subfolders): {total_size_mb:.2f} MB\nFile types: {file_types}")

root = tk.Tk()
root.title("User Folder Scanner")
root.geometry("800x600")

top_frame = ttk.Frame(root)
top_frame.pack(fill="x", pady=10, padx=10)

scan_button = ttk.Button(top_frame, text="Scan Folders", command=start_scan)
scan_button.pack(side="left", padx=5)

summary_text = tk.StringVar(value="Overall Total Size: 0 MB\nFile types: {}")
summary_label = ttk.Label(root, textvariable=summary_text, anchor="w", justify="left")
summary_label.pack(fill="x", padx=10, pady=5)

tree_frame = ttk.Frame(root)
tree_frame.pack(fill="both", expand=True, pady=10, padx=10)

tree = ttk.Treeview(tree_frame, columns=("Direct Size", "Total Size"), show="tree headings", height=20)
tree.heading("#0", text="Folder/File Name")
tree.heading("#1", text="Direct Size")
tree.heading("#2", text="Total Size")
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree_data = {}
root.mainloop()
