import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import re

def get_email_config():
    """Get the current email configuration for use by other modules"""
    config_file = "email_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return {
                    'alert_email': config.get('alert_email', ''),
                    'alert_priority': config.get('alert_priority', 0)
                }
        except (json.JSONDecodeError, IOError):
            pass
    return {'alert_email': '', 'alert_priority': 0}

def create_email_interface():
    config_file = "email_config.json"

    def load_config():
        """Load email configuration from file"""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_config(config):
        """Save email configuration to file"""
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError:
            return False

    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def save_email():
        email = email_entry.get().strip()
        if not email:
            messagebox.showwarning("Warning", "Please enter an email address")
            return

        if not validate_email(email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address")
            return

        config = load_config()
        config['alert_email'] = email

        if save_config(config):
            messagebox.showinfo("Email Saved", f"Alert email saved: {email}")
        else:
            messagebox.showerror("Error", "Failed to save email configuration")

    def save_priority():
        priority = priority_var.get()
        config = load_config()
        config['alert_priority'] = int(priority)

        if save_config(config):
            messagebox.showinfo("Priority Saved", f"Alert priority threshold saved: {priority}\nWill alert for priorities 0-{priority}")
        else:
            messagebox.showerror("Error", "Failed to save priority configuration")

    def genereaza_rapoarte():
        messagebox.showinfo("Report", "Generating reports...")

    root = tk.Tk()
    root.title("Your CyberPolice!!")
    root.geometry("800x600")
    root.configure(bg='white')

    # Load existing configuration
    config = load_config()

    # Main container
    main_frame = tk.Frame(root, bg='white', padx=50, pady=50)
    main_frame.pack(fill='both', expand=True)

    # Title
    title_label = tk.Label(
        main_frame,
        text="Your CyberPolice!!",
        font=('Arial', 20, 'bold'),
        bg='white',
        fg='#4B0082'
    )
    title_label.pack(pady=30)

    # Email section with purple border
    email_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=3, highlightbackground='#8A2BE2', highlightthickness=2)
    email_frame.pack(fill='x', pady=20, padx=20)

    # Email input row
    email_input_frame = tk.Frame(email_frame, bg='white')
    email_input_frame.pack(fill='x', padx=20, pady=20)

    tk.Label(email_input_frame, text="Email:", font=('Arial', 14), bg='white', fg='black').pack(side='left', padx=(0, 10))
    email_entry = tk.Entry(email_input_frame, width=40, font=('Arial', 12), bd=2, relief='solid')
    email_entry.pack(side='left', padx=(0, 20))

    # Load existing email if available
    if 'alert_email' in config:
        email_entry.insert(0, config['alert_email'])

    save_email_btn = tk.Button(
        email_input_frame,
        text="Save Email",
        command=save_email,
        bg='white',
        fg='gray',
        font=('Arial', 12),
        width=12,
        height=1,
        bd=2,
        relief='solid',
        highlightbackground='#8A2BE2'
    )
    save_email_btn.pack(side='left')

    # Priority section with blue border
    priority_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=3, highlightbackground='#4169E1', highlightthickness=2)
    priority_frame.pack(fill='x', pady=20, padx=20)

    # Priority input row
    priority_input_frame = tk.Frame(priority_frame, bg='white')
    priority_input_frame.pack(fill='x', padx=20, pady=20)

    tk.Label(priority_input_frame, text="Alert Priority Threshold (0=Emergency, 6=Info):", font=('Arial', 14), bg='white', fg='black').pack(side='left', padx=(0, 10))

    # Set initial priority value from config or default to "0"
    initial_priority = str(config.get('alert_priority', 0))
    priority_var = tk.StringVar(value=initial_priority)
    priority_combo = ttk.Combobox(
        priority_input_frame,
        textvariable=priority_var,
        values=['0', '1', '2', '3', '4', '5', '6'],
        state="readonly",
        width=15,
        font=('Arial', 12)
    )
    priority_combo.pack(side='left', padx=(0, 20))

    save_priority_btn = tk.Button(
        priority_input_frame,
        text="Save Priority",
        command=save_priority,
        bg='white',
        fg='gray',
        font=('Arial', 12),
        width=12,
        height=1,
        bd=2,
        relief='solid',
        highlightbackground='#4169E1'
    )
    save_priority_btn.pack(side='left')

    # Generate Reports section
    reports_frame = tk.Frame(main_frame, bg='white')
    reports_frame.pack(fill='x', pady=40, padx=20)

    genereaza_btn = tk.Button(
        reports_frame,
        text="Generate Reports",
        command=genereaza_rapoarte,
        bg='white',
        fg='gray',
        font=('Arial', 14, 'bold'),
        width=20,
        height=2,
        bd=3,
        relief='solid',
        highlightbackground='#8A2BE2'
    )
    genereaza_btn.pack()

    root.mainloop()

if __name__ == '__main__':
    create_email_interface()