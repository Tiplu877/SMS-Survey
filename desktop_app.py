import tkinter as tk
from tkinter import simpledialog, filedialog
import sqlite3, csv, re, subprocess, sys, os, smtplib
from email.message import EmailMessage

#Helper for PyInstaller paths
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)

#Database setup
DB_NAME = resource_path("customers.db")
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE NOT NULL
)
""")
conn.commit()

#Logging setup
LOG_FILE = resource_path("app_logs.txt")
def log_message(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")
    print(message)

#Email setup
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.environ.get("EMAIL_USER", "your_email@gmail.com")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "YOUR_APP_PASSWORD")
COMPANY_EMAIL = "company@email.com"

def send_feedback_email(phone, rating, feedback):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Customer Feedback - Rating {rating}"
        msg['From'] = EMAIL_USER
        msg['To'] = COMPANY_EMAIL
        msg.set_content(f"Phone: {phone}\nRating: {rating}\nFeedback: {feedback}")
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        log_message(f"Sent feedback email for {phone}")
    except Exception as e:
        log_message(f"Failed to send feedback email: {e}")

# Helpers
def format_us_number(phone):
    digits = re.sub(r"\D", "", phone) 
    if digits.startswith("1") and len(digits) == 11:
        digits = "+" + digits
    elif len(digits) == 10:
        digits = "+1" + digits
    else:
        return None
    return digits

def show_popup(title, message, success=True):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("420x220")
    popup.configure(bg="#1E1E2F")
    popup.resizable(False, False)

    bar_color = "#2ECC71" if success else "#E74C3C"
    tk.Frame(popup, bg=bar_color, height=10).pack(fill="x")

    tk.Label(
        popup,
        text=message,
        font=("Helvetica", 14),
        fg="#FFFFFF",
        bg="#1E1E2F",
        wraplength=380,
        justify="center"
    ).pack(expand=True, pady=20)

    tk.Button(
        popup,
        text="OK",
        font=("Helvetica", 12, "bold"),
        bg="#3498DB",
        fg="#FFFFFF",
        width=12,
        relief="flat",
        activebackground="#2980B9",
        command=popup.destroy
    ).pack(pady=10)

    popup.transient(root)
    popup.grab_set()
    root.wait_window(popup)

#GUI Actions
def add_number():
    phone = simpledialog.askstring("Add Phone", "Enter phone number:")
    if phone:
        formatted = format_us_number(phone)
        if not formatted:
            show_popup("Error", "Invalid phone number ❌", False)
            return
        try:
            cursor.execute("INSERT INTO customers (phone) VALUES (?)", (formatted,))
            conn.commit()
            show_popup("Added", f"{formatted} added successfully ✅", True)
        except sqlite3.IntegrityError:
            show_popup("Duplicate", "Phone number already exists ⚠️", False)

def remove_number():
    phone = simpledialog.askstring("Remove Phone", "Enter phone number:")
    if phone:
        clean = clean_phone(phone)
        if not clean:
            show_popup("Error", "Invalid phone number ❌", False)
            log_message(f"Failed to remove invalid number: {phone}")
            return
        cursor.execute("DELETE FROM customers WHERE phone=?", (clean,))
        conn.commit()
        show_popup("Removed", f"{clean} removed ✅", True)
        log_message(f"Removed phone number: {clean}")

def view_numbers():
    cursor.execute("SELECT phone FROM customers ORDER BY phone")
    rows = cursor.fetchall()

    popup = tk.Toplevel(root)
    popup.title("Phone Numbers")
    popup.geometry("420x450")
    popup.configure(bg="#1E1E2F")

    tk.Label(
        popup, text="Saved Phone Numbers",
        font=("Helvetica", 18, "bold"),
        fg="#FFFFFF", bg="#1E1E2F"
    ).pack(pady=15)

    frame = tk.Frame(popup, bg="#1E1E2F")
    frame.pack(fill="both", expand=True, padx=20)

    canvas = tk.Canvas(frame, bg="#1E1E2F", highlightthickness=0)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#1E1E2F")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if rows:
        for r in rows:
            tk.Label(
                scroll_frame, text=r[0],
                font=("Helvetica", 14),
                fg="#FFFFFF", bg="#1E1E2F"
            ).pack(pady=3)
    else:
        tk.Label(
            scroll_frame, text="No phone numbers found",
            font=("Helvetica", 14),
            fg="#B0B0B0", bg="#1E1E2F"
        ).pack(pady=10)

    tk.Button(
        popup, text="Close",
        font=("Helvetica", 12, "bold"),
        bg="#3498DB", fg="#FFFFFF",
        width=12, relief="flat",
        command=popup.destroy
    ).pack(pady=15)

def import_csv():
    file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file:
        count = 0
        with open(file, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    formatted = format_us_number(row[0])
                    if formatted:
                        try:
                            cursor.execute("INSERT INTO customers (phone) VALUES (?)", (formatted,))
                            count += 1
                        except sqlite3.IntegrityError:
                            pass
        conn.commit()
        show_popup("Imported", f"{count} numbers imported ✅", True)

def export_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        cursor.execute("SELECT phone FROM customers")
        rows = cursor.fetchall()
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            for r in rows:
                writer.writerow(r)
        show_popup("Exported", f"{len(rows)} numbers exported ✅", True)
        log_message(f"Exported {len(rows)} numbers to CSV")

def start_flask():
    folder = os.path.dirname(sys.executable)
    flask_path = os.path.join(folder, "app.exe")

    if not os.path.exists(flask_path):
        show_popup(
            "Error",
            f"app.exe not found.\nExpected location:\n{flask_path}",
            False
        )
        log_message("Flask server not found")
        return

    subprocess.Popen([flask_path], cwd=folder)
    show_popup("Server Started", "Flask server started 🚀", True)
    log_message("Flask server started")

def view_logs():
    if not os.path.exists(LOG_FILE):
        show_popup("Logs", "No logs available yet.", False)
        return

    with open(LOG_FILE, "r") as f:
        logs = f.read()

    popup = tk.Toplevel(root)
    popup.title("Application Logs")
    popup.geometry("600x500")
    popup.configure(bg="#1E1E2F")

    tk.Label(popup, text="Application Logs", font=("Helvetica", 16, "bold"), fg="#FFFFFF", bg="#1E1E2F").pack(pady=10)

    frame = tk.Frame(popup, bg="#1E1E2F")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    text_area = tk.Text(frame, bg="#1E1E2F", fg="#FFFFFF", wrap="word")
    text_area.insert("1.0", logs)
    text_area.config(state="disabled")
    text_area.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(frame, command=text_area.yview)
    scrollbar.pack(side="right", fill="y")
    text_area['yscrollcommand'] = scrollbar.set

    tk.Button(popup, text="Close", font=("Helvetica", 12, "bold"), bg="#3498DB", fg="#FFFFFF", width=10, relief="flat", command=popup.destroy).pack(pady=10)

# Send Survey & collect feedback
def send_survey():
    try:
        from app import send_survey_sms 
        send_survey_sms() 
        show_popup("Survey Sent", "Survey sent to all numbers ✅", True)
    except Exception as e:
        show_popup("Error", f"Failed to send survey ❌\n{e}", False)


#GUI Setup
root = tk.Tk()
root.title("SMS Survey Manager")
root.state("zoomed")
root.configure(bg="#1E1E2F")

def on_exit():
    conn.close()
    root.destroy()
root.protocol("WM_DELETE_WINDOW", on_exit)

title_frame = tk.Frame(root, bg="#1E1E2F")
title_frame.pack(pady=40)
tk.Label(title_frame, text="SMS Survey Manager", font=("Helvetica", 34, "bold"), fg="#FFFFFF", bg="#1E1E2F").pack()
tk.Label(title_frame, text="Manage customers, send surveys & collect feedback", font=("Helvetica", 16), fg="#B0B0B0", bg="#1E1E2F").pack(pady=10)

btn_frame = tk.Frame(root, bg="#1E1E2F")
btn_frame.pack(pady=30)

def on_enter(e): e.widget["background"] = "#2980B9"
def on_leave(e): e.widget["background"] = "#3498DB"

button_style = {
    "width": 30, "height": 2, "font": ("Helvetica", 16, "bold"),
    "bg": "#3498DB", "fg": "#FFFFFF", "bd": 0, "relief": "flat",
    "activebackground": "#2980B9", "activeforeground": "#FFFFFF"
}

buttons = [
    ("🚀 Start Server", start_flask),
    ("➕ Add Phone Number", add_number),
    ("❌ Remove Phone Number", remove_number),
    ("📋 View Numbers", view_numbers),
    ("📥 Import CSV", import_csv),
    ("📤 Export CSV", export_csv),
    ("📨 Send Survey", send_survey),
    ("📝 View Logs", view_logs),
    ("🚪 Exit", on_exit)
]

for text, cmd in buttons:
    btn = tk.Button(btn_frame, text=text, command=cmd, **button_style)
    btn.pack(pady=10)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

root.mainloop()
