import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json

class ParagraphEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Paragraph Editor - Dreszcz")
        self.data = {}
        self.current_id = None

        # --- GUI Layout ---
        tk.Label(master, text="Paragraph ID:").grid(row=0, column=0, sticky="e")
        self.id_entry = tk.Entry(master)
        self.id_entry.grid(row=0, column=1, sticky="we")

        tk.Button(master, text="Load", command=self.load_paragraph).grid(row=0, column=2)
        tk.Button(master, text="New", command=self.new_paragraph).grid(row=0, column=3)

        tk.Label(master, text="Text:").grid(row=1, column=0, sticky="nw")
        self.text_field = tk.Text(master, height=6)
        self.text_field.grid(row=1, column=1, columnspan=3, sticky="we")

        tk.Label(master, text="Combat (JSON):").grid(row=2, column=0, sticky="nw")
        self.combat_field = tk.Text(master, height=4)
        self.combat_field.grid(row=2, column=1, columnspan=3, sticky="we")

        tk.Label(master, text="Effects (JSON):").grid(row=3, column=0, sticky="nw")
        self.effects_field = tk.Text(master, height=4)
        self.effects_field.grid(row=3, column=1, columnspan=3, sticky="we")

        tk.Label(master, text="Edges (JSON):").grid(row=4, column=0, sticky="nw")
        self.edges_field = tk.Text(master, height=4)
        self.edges_field.grid(row=4, column=1, columnspan=3, sticky="we")

        tk.Button(master, text="Save", command=self.save_paragraph).grid(row=5, column=1)
        tk.Button(master, text="Load JSON File", command=self.load_json_file).grid(row=5, column=2)
        tk.Button(master, text="Save JSON File", command=self.save_json_file).grid(row=5, column=3)

        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_columnconfigure(3, weight=1)

    def load_json_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            messagebox.showinfo("Success", "JSON loaded successfully.")

    def save_json_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success", "JSON saved successfully.")

    def load_paragraph(self):
        pid = self.id_entry.get()
        if pid in self.data:
            self.current_id = pid
            para = self.data[pid]
            self.text_field.delete("1.0", tk.END)
            self.text_field.insert(tk.END, para.get("text", ""))
            self.combat_field.delete("1.0", tk.END)
            self.combat_field.insert(tk.END, json.dumps(para.get("combat", []), indent=2))
            self.effects_field.delete("1.0", tk.END)
            self.effects_field.insert(tk.END, json.dumps(para.get("effects", []), indent=2))
            self.edges_field.delete("1.0", tk.END)
            self.edges_field.insert(tk.END, json.dumps(para.get("edges", []), indent=2))
        else:
            messagebox.showwarning("Not found", f"No paragraph with ID {pid}.")

    def new_paragraph(self):
        pid = simpledialog.askstring("New Paragraph", "Enter new paragraph ID:")
        if pid:
            if pid in self.data:
                messagebox.showerror("Error", f"Paragraph {pid} already exists.")
            else:
                self.id_entry.delete(0, tk.END)
                self.id_entry.insert(0, pid)
                self.text_field.delete("1.0", tk.END)
                self.combat_field.delete("1.0", tk.END)
                self.effects_field.delete("1.0", tk.END)
                self.edges_field.delete("1.0", tk.END)
                self.current_id = pid

    def save_paragraph(self):
        pid = self.id_entry.get()
        if not pid:
            messagebox.showerror("Error", "ID is required.")
            return
        try:
            self.data[pid] = {
                "text": self.text_field.get("1.0", tk.END).strip(),
                "combat": json.loads(self.combat_field.get("1.0", tk.END)),
                "effects": json.loads(self.effects_field.get("1.0", tk.END)),
                "edges": json.loads(self.edges_field.get("1.0", tk.END))
            }
            messagebox.showinfo("Saved", f"Paragraph {pid} saved.")
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ParagraphEditor(root)
    root.mainloop()