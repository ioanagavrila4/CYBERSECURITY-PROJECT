import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import re

# Try to import PIL for advanced graphics, fallback to basic tkinter
try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available - using basic graphics")

def create_gradient_background(width, height, color1, color2):
    """Create a gradient background image if PIL is available"""
    if not PIL_AVAILABLE:
        return None

    try:
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)

        # Create vertical gradient
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        return ImageTk.PhotoImage(image)
    except Exception:
        return None

def create_icon_from_text(text, size, bg_color, text_color):
    """Create a simple icon from text if PIL is available"""
    if not PIL_AVAILABLE:
        return None

    try:
        image = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(image)

        # Try to use a built-in font, fallback to default
        try:
            # Use default font since custom fonts may not be available on all systems
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            draw.text((x, y), text, fill=text_color)
        except:
            # Fallback if there are font issues
            draw.text((size//4, size//4), text, fill=text_color)

        return ImageTk.PhotoImage(image)
    except Exception:
        return None

def setup_custom_styles():
    """Setup custom styles for better cross-platform appearance"""
    try:
        style = ttk.Style()

        # Configure styles to be more consistent across platforms
        style.configure('Custom.TCombobox',
                       fieldbackground='white',
                       background='white',
                       borderwidth=2,
                       relief='solid')

        return style
    except Exception:
        # Return None if style configuration fails
        return None

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

    # Setup custom styles
    setup_custom_styles()

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
        priority_text = priority_var.get()
        # Extract numeric value from the display text
        priority = priority_text.split(' - ')[0] if ' - ' in priority_text else priority_text

        config = load_config()
        config['alert_priority'] = int(priority)

        if save_config(config):
            messagebox.showinfo("Priority Saved", f"Alert priority threshold saved: {priority_text}\nWill alert for priorities 0-{priority}")
        else:
            messagebox.showerror("Error", "Failed to save priority configuration")

    def genereaza_rapoarte():
        messagebox.showinfo("Report", "Generating reports...")

    root = tk.Tk()
    root.title("CyberPolice - Security Alert Configuration")
    root.geometry("900x700")
    root.configure(bg='#f0f0f0')
    root.resizable(True, True)

    # Set minimum size for better usability on different screens
    root.minsize(700, 500)

    # Configure for better cross-platform appearance
    root.option_add('*TCombobox*Listbox.selectBackground', '#4a90e2')

    # Load existing configuration
    config = load_config()

    # Create gradient background if available
    gradient_bg = create_gradient_background(900, 700, (240, 248, 255), (230, 230, 250))
    if gradient_bg:
        try:
            bg_label = tk.Label(root, image=gradient_bg)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            bg_label.image = gradient_bg  # Keep a reference
        except Exception:
            root.configure(bg='#f8f9fa')
    else:
        # Fallback to solid color if gradient not available
        root.configure(bg='#f8f9fa')

    # Main scrollable container
    canvas = tk.Canvas(root, bg='#f8f9fa', highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    scrollbar.pack(side="right", fill="y", pady=20)

    # Main container within scrollable frame
    main_frame = tk.Frame(scrollable_frame, bg='#f8f9fa', padx=30, pady=30)
    main_frame.pack(fill='both', expand=True)

    # Header section with icon and title
    header_frame = tk.Frame(main_frame, bg='#f8f9fa')
    header_frame.pack(fill='x', pady=(0, 30))

    # Create shield icon if possible
    shield_icon = create_icon_from_text("🛡️", 64, (70, 130, 180), (255, 255, 255))
    if shield_icon:
        try:
            icon_label = tk.Label(header_frame, image=shield_icon, bg='#f8f9fa')
            icon_label.image = shield_icon  # Keep a reference
            icon_label.pack()
        except Exception:
            # Fallback text icon
            icon_label = tk.Label(
                header_frame,
                text="🛡️",
                font=('Helvetica', 32),
                bg='#f8f9fa',
                fg='#4682b4'
            )
            icon_label.pack()
    else:
        # Fallback text icon when PIL is not available
        icon_label = tk.Label(
            header_frame,
            text="[SHIELD]",
            font=('Helvetica', 16, 'bold'),
            bg='#4682b4',
            fg='white',
            width=8,
            height=2,
            relief='raised',
            bd=2
        )
        icon_label.pack(pady=5)

    # Title with improved typography
    title_label = tk.Label(
        header_frame,
        text="CyberPolice Security Center",
        font=('Helvetica', 24, 'bold'),
        bg='#f8f9fa',
        fg='#2c3e50'
    )
    title_label.pack(pady=(10, 5))

    # Subtitle
    subtitle_label = tk.Label(
        header_frame,
        text="Configure Alert Settings & Generate Security Reports",
        font=('Helvetica', 12),
        bg='#f8f9fa',
        fg='#7f8c8d'
    )
    subtitle_label.pack()

    # Email section with modern card design
    email_card = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
    email_card.pack(fill='x', pady=15, padx=10)

    # Add shadow effect with multiple frames
    shadow_frame = tk.Frame(main_frame, bg='#d3d3d3', height=2)
    shadow_frame.pack(fill='x', padx=12)

    # Email section header
    email_header = tk.Frame(email_card, bg='#4a90e2', height=50)
    email_header.pack(fill='x')
    email_header.pack_propagate(False)

    email_title = tk.Label(
        email_header,
        text="📧 Email Alert Configuration",
        font=('Helvetica', 14, 'bold'),
        bg='#4a90e2',
        fg='white'
    )
    email_title.pack(expand=True)

    # Email input section
    email_content = tk.Frame(email_card, bg='white')
    email_content.pack(fill='x', padx=25, pady=20)

    # Email label with description
    email_label_frame = tk.Frame(email_content, bg='white')
    email_label_frame.pack(fill='x', pady=(0, 10))

    tk.Label(
        email_label_frame,
        text="Alert Email Address",
        font=('Helvetica', 12, 'bold'),
        bg='white',
        fg='#2c3e50'
    ).pack(anchor='w')

    tk.Label(
        email_label_frame,
        text="Enter the email address where security alerts will be sent",
        font=('Helvetica', 9),
        bg='white',
        fg='#7f8c8d'
    ).pack(anchor='w')

    # Email input with button frame
    email_input_frame = tk.Frame(email_content, bg='white')
    email_input_frame.pack(fill='x', pady=(5, 0))

    email_entry = tk.Entry(
        email_input_frame,
        width=45,
        font=('Helvetica', 11),
        bd=1,
        relief='solid',
        highlightthickness=2,
        highlightcolor='#4a90e2',
        bg='#fafafa'
    )
    email_entry.pack(side='left', padx=(0, 15), ipady=8)

    # Load existing email if available
    if 'alert_email' in config:
        email_entry.insert(0, config['alert_email'])

    save_email_btn = tk.Button(
        email_input_frame,
        text="💾 Save Email",
        command=save_email,
        bg='#4a90e2',
        fg='white',
        font=('Helvetica', 10, 'bold'),
        width=15,
        height=1,
        bd=0,
        relief='flat',
        cursor='hand2',
        activebackground='#357abd',
        activeforeground='white'
    )
    save_email_btn.pack(side='left', ipady=8)

    # Add hover effects
    def on_enter_email(event):
        save_email_btn.configure(bg='#357abd')

    def on_leave_email(event):
        save_email_btn.configure(bg='#4a90e2')

    save_email_btn.bind('<Enter>', on_enter_email)
    save_email_btn.bind('<Leave>', on_leave_email)

    # Priority section with modern card design
    priority_card = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
    priority_card.pack(fill='x', pady=15, padx=10)

    # Add shadow effect
    priority_shadow = tk.Frame(main_frame, bg='#d3d3d3', height=2)
    priority_shadow.pack(fill='x', padx=12)

    # Priority section header
    priority_header = tk.Frame(priority_card, bg='#e74c3c', height=50)
    priority_header.pack(fill='x')
    priority_header.pack_propagate(False)

    priority_title = tk.Label(
        priority_header,
        text="⚠️ Alert Priority Configuration",
        font=('Helvetica', 14, 'bold'),
        bg='#e74c3c',
        fg='white'
    )
    priority_title.pack(expand=True)

    # Priority content section
    priority_content = tk.Frame(priority_card, bg='white')
    priority_content.pack(fill='x', padx=25, pady=20)

    # Priority label with description
    priority_label_frame = tk.Frame(priority_content, bg='white')
    priority_label_frame.pack(fill='x', pady=(0, 10))

    tk.Label(
        priority_label_frame,
        text="Alert Priority Threshold",
        font=('Helvetica', 12, 'bold'),
        bg='white',
        fg='#2c3e50'
    ).pack(anchor='w')

    tk.Label(
        priority_label_frame,
        text="Set minimum alert level: 0=Emergency, 1=High, 2=Medium, 3=Low, 4=Info",
        font=('Helvetica', 9),
        bg='white',
        fg='#7f8c8d'
    ).pack(anchor='w')

    # Priority selection frame
    priority_select_frame = tk.Frame(priority_content, bg='white')
    priority_select_frame.pack(fill='x', pady=(5, 0))

    # Priority selection with labels
    initial_priority = str(config.get('alert_priority', 0))
    priority_var = tk.StringVar(value=initial_priority)

    priority_options = [
        ('0 - Emergency', '0'),
        ('1 - High', '1'),
        ('2 - Medium', '2'),
        ('3 - Low', '3'),
        ('4 - Info', '4')
    ]

    priority_combo = ttk.Combobox(
        priority_select_frame,
        textvariable=priority_var,
        values=[option[0] for option in priority_options],
        state="readonly",
        width=20,
        font=('Helvetica', 11),
        style='Custom.TCombobox'
    )
    priority_combo.pack(side='left', padx=(0, 15), ipady=8)

    # Set the display value based on stored value
    stored_priority = config.get('alert_priority', 0)
    for option in priority_options:
        if option[1] == str(stored_priority):
            priority_combo.set(option[0])
            break

    save_priority_btn = tk.Button(
        priority_select_frame,
        text="🔧 Save Priority",
        command=save_priority,
        bg='#e74c3c',
        fg='white',
        font=('Helvetica', 10, 'bold'),
        width=15,
        height=1,
        bd=0,
        relief='flat',
        cursor='hand2',
        activebackground='#c0392b',
        activeforeground='white'
    )
    save_priority_btn.pack(side='left', ipady=8)

    # Add hover effects for priority button
    def on_enter_priority(event):
        save_priority_btn.configure(bg='#c0392b')

    def on_leave_priority(event):
        save_priority_btn.configure(bg='#e74c3c')

    save_priority_btn.bind('<Enter>', on_enter_priority)
    save_priority_btn.bind('<Leave>', on_leave_priority)

    # Generate Reports section with modern card design
    reports_card = tk.Frame(main_frame, bg='white', relief='flat', bd=0)
    reports_card.pack(fill='x', pady=15, padx=10)

    # Add shadow effect
    reports_shadow = tk.Frame(main_frame, bg='#d3d3d3', height=2)
    reports_shadow.pack(fill='x', padx=12)

    # Reports section header
    reports_header = tk.Frame(reports_card, bg='#27ae60', height=50)
    reports_header.pack(fill='x')
    reports_header.pack_propagate(False)

    reports_title = tk.Label(
        reports_header,
        text="📊 Security Reports",
        font=('Helvetica', 14, 'bold'),
        bg='#27ae60',
        fg='white'
    )
    reports_title.pack(expand=True)

    # Reports content
    reports_content = tk.Frame(reports_card, bg='white')
    reports_content.pack(fill='x', padx=25, pady=20)

    # Reports description
    reports_desc = tk.Label(
        reports_content,
        text="Generate comprehensive security reports and analysis",
        font=('Helvetica', 11),
        bg='white',
        fg='#2c3e50'
    )
    reports_desc.pack(pady=(0, 15))

    genereaza_btn = tk.Button(
        reports_content,
        text="📈 Generate Security Reports",
        command=genereaza_rapoarte,
        bg='#27ae60',
        fg='white',
        font=('Helvetica', 12, 'bold'),
        width=25,
        height=2,
        bd=0,
        relief='flat',
        cursor='hand2',
        activebackground='#229954',
        activeforeground='white'
    )
    genereaza_btn.pack(pady=10, ipady=10)

    # Add hover effects for reports button
    def on_enter_reports(event):
        genereaza_btn.configure(bg='#229954')

    def on_leave_reports(event):
        genereaza_btn.configure(bg='#27ae60')

    genereaza_btn.bind('<Enter>', on_enter_reports)
    genereaza_btn.bind('<Leave>', on_leave_reports)

    # Status bar at bottom
    status_frame = tk.Frame(main_frame, bg='#34495e', height=30)
    status_frame.pack(fill='x', pady=(30, 0))
    status_frame.pack_propagate(False)

    status_label = tk.Label(
        status_frame,
        text="CyberPolice v2.0 - Cross-Platform Security Monitoring",
        font=('Helvetica', 9),
        bg='#34495e',
        fg='white'
    )
    status_label.pack(expand=True)

    # Bind mouse wheel to canvas for scrolling
    def _on_mousewheel(event):
        try:
            # Windows and MacOS
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except AttributeError:
            # Linux and other systems
            if hasattr(event, 'num'):
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")

    canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
    canvas.bind("<Button-4>", _on_mousewheel)    # Linux
    canvas.bind("<Button-5>", _on_mousewheel)    # Linux

    root.mainloop()

if __name__ == '__main__':
    create_email_interface()