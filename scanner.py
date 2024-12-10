import tkinter as tk
from tkinter import messagebox, simpledialog
from ttkbootstrap import Style, ttk
import sqlite3
from datetime import datetime

# --- Database Setup ---
conn = sqlite3.connect("SYMUN_attendance.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    barcode TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT,
    name TEXT,
    role TEXT,
    date_time TEXT
)
""")
conn.commit()

# --- Functions ---
def add_member():
    """Add a new member to the database."""
    barcode = simpledialog.askstring("Scan Barcode", "Please scan or enter the barcode:")
    if not barcode:
        return

    name = simpledialog.askstring("Member Name", "Enter the member's name:")
    if not name:
        return

    role = simpledialog.askstring("Member Role", "Enter the member's role:")
    if not role:
        return

    try:
        cursor.execute("INSERT INTO members (barcode, name, role) VALUES (?, ?, ?)", (barcode, name, role))
        conn.commit()
        messagebox.showinfo("Success", f"Member '{name}' added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Barcode already exists in the system.")

def scan_barcode_entry(event):
    """Mark attendance using barcode scanner input."""
    barcode = barcode_entry.get().strip()
    barcode_entry.delete(0, tk.END)  # Clear the entry field

    if not barcode:
        return

    # Check if the barcode exists in the database
    cursor.execute("SELECT name, role FROM members WHERE barcode = ?", (barcode,))
    member = cursor.fetchone()

    if member:
        name, role = member
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO attendance (barcode, name, role, date_time) VALUES (?, ?, ?, ?)",
                       (barcode, name, role, now))
        conn.commit()
        messagebox.showinfo("Attendance Marked", f"{name} ({role}) marked present at {now}")
    else:
        messagebox.showerror("Unknown Barcode", "The scanned barcode is not registered.")

def view_attendance_log():
    """Display attendance records."""
    cursor.execute("SELECT name, role, date_time FROM attendance ORDER BY date_time DESC")
    records = cursor.fetchall()

    log_window = tk.Toplevel(root)
    log_window.title("Attendance Log")

    text = tk.Text(log_window, wrap=tk.WORD)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    if records:
        for record in records:
            text.insert(tk.END, f"{record[2]} - {record[0]} ({record[1]})\n")
    else:
        text.insert(tk.END, "No attendance records found.")

def reset_logs():
    """Reset all attendance logs after login verification."""
    username = simpledialog.askstring("Login", "Enter your username:")
    password = simpledialog.askstring("Login", "Enter your password:", show="*")

    if username == "ashik" and password == "3487":
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all attendance logs?"):
            cursor.execute("DELETE FROM attendance")  # Clear the attendance table
            conn.commit()
            messagebox.showinfo("Success", "Attendance logs have been reset.")
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def member_list():
    """Display the list of members and allow removing a member."""
    cursor.execute("SELECT barcode, name, role FROM members")
    members = cursor.fetchall()

    list_window = tk.Toplevel(root)
    list_window.title("Member List")

    text = tk.Text(list_window, wrap=tk.WORD, height=15)
    text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    if members:
        for member in members:
            text.insert(tk.END, f"Barcode: {member[0]} | Name: {member[1]} | Role: {member[2]}\n")

        def remove_member():
            """Remove the selected member based on barcode."""
            barcode_to_remove = simpledialog.askstring("Remove Member", "Enter the barcode of the member to remove:")
            if barcode_to_remove:
                cursor.execute("DELETE FROM members WHERE barcode = ?", (barcode_to_remove,))
                conn.commit()
                messagebox.showinfo("Success", "Member removed successfully!")
                list_window.destroy()  # Close the list window
                member_list()  # Refresh the member list window
    else:
        text.insert(tk.END, "No members found.")
        
    ttk.Button(list_window, text="Remove Member", command=remove_member, width=25, bootstyle="danger").pack(pady=10)

# --- GUI Setup ---
style = Style("superhero")
root = style.master
root.title("SYMUN Attendance System")
root.geometry("500x500")

# App Title
title_label = ttk.Label(root, text="SYMUN Attendance System", font=("Helvetica", 18, "bold"), anchor="center")
title_label.pack(pady=10)

# Barcode Entry
barcode_label = ttk.Label(root, text="Scan Barcode Below:", font=("Helvetica", 14))
barcode_label.pack(pady=5)

barcode_entry = ttk.Entry(root, font=("Helvetica", 14), bootstyle="primary")
barcode_entry.pack(pady=10, padx=20, fill=tk.X)

# Bind the "Enter" key to mark attendance
barcode_entry.bind("<Return>", scan_barcode_entry)

# Buttons
ttk.Button(root, text="Add Member", command=add_member, width=25, bootstyle="primary").pack(pady=10)
ttk.Button(root, text="View Attendance Log", command=view_attendance_log, width=25, bootstyle="info").pack(pady=10)
ttk.Button(root, text="Reset Logs", command=reset_logs, width=25, bootstyle="danger").pack(pady=10)
ttk.Button(root, text="Member List", command=member_list, width=25, bootstyle="info").pack(pady=10)

# Footer
footer_label = ttk.Label(root, text="Savar Youth Model United Nations", font=("Helvetica", 10), anchor="center")
footer_label.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
