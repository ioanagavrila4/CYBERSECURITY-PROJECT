import tkinter as tk
from tkinter import messagebox, ttk

def create_email_interface():
    def save_email():
        email = email_entry.get()
        if email:
            messagebox.showinfo("Email Saved", f"Email saved: {email}")
        else:
            messagebox.showwarning("Warning", "Please enter an email address")

    def save_priority():
        priority = priority_var.get()
        messagebox.showinfo("Priority Saved", f"Priority saved: {priority}")

    def genereaza_rapoarte():
        messagebox.showinfo("Report", "Generating reports...")

    root = tk.Tk()
    root.title("Your CyberPolice!!")
    root.geometry("800x600")
    root.configure(bg='white')

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

    tk.Label(priority_input_frame, text="Priority (0-6):", font=('Arial', 14), bg='white', fg='black').pack(side='left', padx=(0, 10))

    priority_var = tk.StringVar(value="0")
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