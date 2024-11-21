import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv

class ContactManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Management System")
        self.root.geometry("800x600")
        
        self.conn = sqlite3.connect("contacts.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )""")
        self.conn.commit()

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.search_var = tk.StringVar()

        tk.Label(root, text="Name").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(root, text="Phone").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.phone_var).grid(row=1, column=1, padx=10, pady=10)
        tk.Label(root, text="Email").grid(row=2, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=10)
        tk.Label(root, text="Address").grid(row=3, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.address_var).grid(row=3, column=1, padx=10, pady=10)

        tk.Button(root, text="Add Contact", command=self.add_contact).grid(row=4, column=0, pady=10)
        tk.Button(root, text="Update Contact", command=self.update_contact).grid(row=4, column=1, pady=10)
        tk.Button(root, text="Delete Contact", command=self.delete_contact).grid(row=5, column=0, pady=10)
        tk.Button(root, text="Export Contacts", command=self.export_contacts).grid(row=5, column=1, pady=10)
        tk.Button(root, text="Import Contacts", command=self.import_contacts).grid(row=6, column=0, pady=10)

        tk.Label(root, text="Search").grid(row=7, column=0, padx=10, pady=10)
        tk.Entry(root, textvariable=self.search_var).grid(row=7, column=1, padx=10, pady=10)
        tk.Button(root, text="Search", command=self.search_contacts).grid(row=7, column=2, padx=10, pady=10)

        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Phone", "Email", "Address"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Address", text="Address")
        self.tree.column("ID", width=30)
        self.tree.bind("<Double-1>", self.select_contact)
        self.tree.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.display_contacts()

    def add_contact(self):
        name, phone, email, address = self.name_var.get(), self.phone_var.get(), self.email_var.get(), self.address_var.get()
        if name and phone and email and address:
            self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)", (name, phone, email, address))
            self.conn.commit()
            self.display_contacts()
            self.clear_fields()
        else:
            messagebox.showerror("Error", "All fields are required.")

    def update_contact(self):
        selected_item = self.tree.focus()
        if selected_item:
            contact_id = self.tree.item(selected_item)["values"][0]
            name, phone, email, address = self.name_var.get(), self.phone_var.get(), self.email_var.get(), self.address_var.get()
            if name and phone and email and address:
                self.cursor.execute("UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?", (name, phone, email, address, contact_id))
                self.conn.commit()
                self.display_contacts()
                self.clear_fields()
            else:
                messagebox.showerror("Error", "All fields are required.")
        else:
            messagebox.showerror("Error", "No contact selected.")

    def delete_contact(self):
        selected_item = self.tree.focus()
        if selected_item:
            contact_id = self.tree.item(selected_item)["values"][0]
            self.cursor.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
            self.conn.commit()
            self.display_contacts()
        else:
            messagebox.showerror("Error", "No contact selected.")

    def search_contacts(self):
        search_term = self.search_var.get()
        self.cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?", (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        rows = self.cursor.fetchall()
        self.display_in_tree(rows)

    def export_contacts(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file:
            self.cursor.execute("SELECT * FROM contacts")
            rows = self.cursor.fetchall()
            with open(file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Phone", "Email", "Address"])
                writer.writerows(rows)

    def import_contacts(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file:
            with open(file, "r") as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    self.cursor.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)", (row[1], row[2], row[3], row[4]))
                self.conn.commit()
            self.display_contacts()

    def display_contacts(self):
        self.cursor.execute("SELECT * FROM contacts")
        rows = self.cursor.fetchall()
        self.display_in_tree(rows)

    def display_in_tree(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", "end", values=row)

    def select_contact(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item)["values"]
            self.name_var.set(values[1])
            self.phone_var.set(values[2])
            self.email_var.set(values[3])
            self.address_var.set(values[4])

    def clear_fields(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.search_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactManagementSystem(root)
    root.mainloop()
