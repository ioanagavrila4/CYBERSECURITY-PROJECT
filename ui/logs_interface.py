import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LogsInterface:
    def __init__(self, db_path="data/Sqlite3.db"):
        self.db_path = db_path
        self.root = None
        self.tree = None

    def get_severity_color(self, severity):
        """Return color based on severity level"""
        severity_colors = {
            '0': '#ff4444',    # Emergency - Red
            '1': '#ff6600',    # Alert - Orange-Red
            '2': '#ff8800',    # Critical - Orange
            '3': '#ffaa00',    # Error - Yellow-Orange
            '4': '#ffcc00',    # Warning - Yellow
            '5': '#88cc00',    # Notice - Yellow-Green
            '6': '#00cc00',    # Info - Green
            '7': '#00cccc',    # Debug - Cyan
        }
        return severity_colors.get(str(severity), '#cccccc')  # Default gray

    def lighten_color(self, color_hex):
        """Lighten a hex color for better readability as background"""
        # Remove the # if present
        color_hex = color_hex.lstrip('#')

        # Convert hex to RGB
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)

        # Lighten by mixing with white (increase each component towards 255)
        r = min(255, r + (255 - r) * 0.7)
        g = min(255, g + (255 - g) * 0.7)
        b = min(255, b + (255 - b) * 0.7)

        # Convert back to hex
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

    def get_severity_label(self, severity):
        """Return severity label"""
        severity_labels = {
            '0': 'Emergency',
            '1': 'Alert',
            '2': 'Critical',
            '3': 'Error',
            '4': 'Warning',
            '5': 'Notice',
            '6': 'Info',
            '7': 'Debug'
        }
        return severity_labels.get(str(severity), 'Unknown')

    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp

    def load_logs_from_db(self):
        """Load logs from SQLite database"""
        logs = []
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, raw_format, time_stamp, severity, description, hostname, updated
                FROM logs
                ORDER BY time_stamp DESC
            """)

            rows = cursor.fetchall()

            for row in rows:
                try:
                    raw_data = json.loads(row[1])
                    message = raw_data.get("MESSAGE", "N/A")
                    priority = raw_data.get("PRIORITY", row[3])  # fallback to stored severity
                    identifier = raw_data.get("SYSLOG_IDENTIFIER", "N/A")
                    realtime_timestamp = raw_data.get("__REALTIME_TIMESTAMP", None)

                    # Format timestamp
                    if realtime_timestamp:
                        try:
                            dt = datetime.fromtimestamp(int(realtime_timestamp) / 1_000_000)
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Include microseconds
                        except:
                            formatted_time = self.format_timestamp(row[2])
                    else:
                        formatted_time = self.format_timestamp(row[2])

                    logs.append({
                        'id': row[0],
                        'datetime': formatted_time,
                        'message': message[:100] + "..." if len(message) > 100 else message,
                        'full_message': message,
                        'severity': str(priority),
                        'identifier': identifier,
                        'hostname': row[5] or "N/A",
                        'raw_format': row[1]
                    })

                except json.JSONDecodeError:
                    # Fallback for non-JSON entries
                    logs.append({
                        'id': row[0],
                        'datetime': self.format_timestamp(row[2]),
                        'message': row[4] or "N/A",
                        'full_message': row[4] or "N/A",
                        'severity': str(row[3]),
                        'identifier': "N/A",
                        'hostname': row[5] or "N/A",
                        'raw_format': row[1]
                    })

            connection.close()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error loading logs: {e}")

        return logs

    def create_logs_interface(self):
        """Create the main logs interface"""
        self.root = tk.Tk()
        self.root.title("CyberPolice - Security Logs Viewer")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')

        # Header frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(
            header_frame,
            text="Security Logs Viewer",
            font=('Helvetica', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(expand=True)

        # Control frame
        control_frame = tk.Frame(self.root, bg='#ecf0f1', height=60)
        control_frame.pack(fill='x', padx=10, pady=5)
        control_frame.pack_propagate(False)

        # Refresh button
        refresh_btn = tk.Button(
            control_frame,
            text="Refresh Logs",
            command=self.refresh_logs,
            bg='#3498db',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=15
        )
        refresh_btn.pack(side='left', padx=10, pady=10)

        # Back to Email Interface button
        back_btn = tk.Button(
            control_frame,
            text="Back to Email Interface",
            command=self.go_to_email_interface,
            bg='#95a5a6',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=15
        )
        back_btn.pack(side='right', padx=10, pady=10)

        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Loading logs...",
            font=('Helvetica', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.status_label.pack(expand=True)

        # Main frame for treeview and scrollbars
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Create treeview with columns matching the image
        columns = ('datetime', 'message', 'severity', 'identifier', 'hostname')

        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=25)

        # Define column headings and widths
        self.tree.heading('datetime', text='Date/Time (UTC)')
        self.tree.heading('message', text='Message')
        self.tree.heading('severity', text='Severity')
        self.tree.heading('identifier', text='Identifier')
        self.tree.heading('hostname', text='Hostname')

        # Configure column widths
        self.tree.column('datetime', width=180, minwidth=150)
        self.tree.column('message', width=500, minwidth=300)
        self.tree.column('severity', width=100, minwidth=80)
        self.tree.column('identifier', width=200, minwidth=150)
        self.tree.column('hostname', width=200, minwidth=150)

        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Bind double-click to show details
        self.tree.bind('<Double-1>', self.show_log_details)

        # Load logs
        self.refresh_logs()

        self.root.mainloop()

    def refresh_logs(self):
        """Refresh the logs display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load new logs
        logs = self.load_logs_from_db()

        # Configure severity colors for each severity level
        for i in range(8):
            color = self.get_severity_color(str(i))
            self.tree.tag_configure(f'severity_{i}', background='white', foreground=color)

        # Insert logs into treeview
        for log in logs:
            severity_tag = f'severity_{log["severity"]}'
            severity_display = f"{log['severity']} - {self.get_severity_label(log['severity'])}"

            # Add small colored circle to datetime
            colored_datetime = f"● {log['datetime']}"

            self.tree.insert('', 'end',
                           values=(
                               colored_datetime,
                               log['message'],
                               severity_display,
                               log['identifier'],
                               log['hostname']
                           ),
                           tags=(severity_tag,))

        # Update status
        log_count = len(logs)
        self.status_label.config(text=f"Loaded {log_count} log entries")

    def show_log_details(self, event=None):
        """Show detailed log information in a popup"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        # Get the full log data
        logs = self.load_logs_from_db()
        selected_log = None
        for log in logs:
            if log['datetime'] == values[0] and log['message'] == values[1]:
                selected_log = log
                break

        if not selected_log:
            return

        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Log Entry Details")
        detail_window.geometry("800x600")
        detail_window.configure(bg='#f0f0f0')

        # Header
        header_frame = tk.Frame(detail_window, bg='#34495e', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        header_label = tk.Label(
            header_frame,
            text="Log Entry Details",
            font=('Helvetica', 16, 'bold'),
            bg='#34495e',
            fg='white'
        )
        header_label.pack(expand=True)

        # Scrollable text area
        text_frame = tk.Frame(detail_window, bg='#f0f0f0')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)

        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 10))
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)

        text_widget.pack(side='left', fill='both', expand=True)
        text_scrollbar.pack(side='right', fill='y')

        # Format and insert details
        details = f"""
LOG ENTRY DETAILS
================

Date/Time: {selected_log['datetime']}
Hostname: {selected_log['hostname']}
Severity: {selected_log['severity']} - {self.get_severity_label(selected_log['severity'])}
Identifier: {selected_log['identifier']}

Full Message:
{selected_log['full_message']}

Raw Log Format:
{json.dumps(json.loads(selected_log['raw_format']), indent=2)}
"""

        text_widget.insert('1.0', details)
        text_widget.config(state='disabled')  # Make read-only

        # Close button
        close_btn = tk.Button(
            detail_window,
            text="Close",
            command=detail_window.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=20
        )
        close_btn.pack(pady=10)

    def go_to_email_interface(self):
        """Navigate back to email interface"""
        self.root.destroy()
        # Import and start email interface
        try:
            from ui.email_interface import create_email_interface
        except ImportError:
            # Fallback for direct script execution
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from ui.email_interface import create_email_interface
        create_email_interface()

def create_logs_interface():
    """Function to create and run the logs interface"""
    app = LogsInterface()
    app.create_logs_interface()

if __name__ == '__main__':
    create_logs_interface()