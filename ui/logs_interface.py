import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.reports import Reports
from utils.collector import Collector
from utils.log_report_generator import LogReportGenerator


class LogsInterface:
    """Main interface for viewing and filtering security logs"""

    def __init__(self, db_path=None, log_sources=None):
        # Use absolute paths relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        """
        self.db_path = db_path if db_path else os.path.join(project_root, "data", "Sqlite3.db")
        self.log_sources = log_sources if log_sources else os.path.join(project_root, "data", "log_sources.txt")
        """

        self.db_path = "data/Sqlite3.db"
        self.log_sources = "data/log_sources.txt"
        self.root = None
        self.tree = None
        self.collector = Collector(self.log_sources, self.db_path)
        self.reports = Reports(self.collector)
        self.report_generator = LogReportGenerator()
        self.all_logs = []
        self.filtered_logs = []
        self.current_filter_info = []

        # Filter variables
        self.filter_severity = None
        self.filter_syslog = None
        self.filter_datetime = None
        self.syslog_combo = None
        self.severity_combo = None
        self.datetime_combo = None
        self.status_label = None

    # ==================== HELPER METHODS ====================

    def get_severity_color(self, severity):
        """Return color based on severity level"""
        severity_colors = {
            '0': '#ff4444',  # Emergency - Red
            '1': '#ff6600',  # Alert - Orange-Red
            '2': '#ff8800',  # Critical - Orange
            '3': '#ffaa00',  # Error - Light Orange
            '4': '#ffcc00',  # Warning - Yellow
            '5': '#88cc00',  # Notice - Yellow-Green
            '6': '#00cc00',  # Info - Green
            '7': '#00cccc',  # Debug - Cyan
        }
        return severity_colors.get(str(severity), '#cccccc')

    def get_severity_label(self, severity):
        """Return severity label"""
        severity_labels = {
            '0': 'Emergency', '1': 'Alert', '2': 'Critical', '3': 'Error',
            '4': 'Warning', '5': 'Notice', '6': 'Info', '7': 'Debug'
        }
        return severity_labels.get(str(severity), 'Unknown')

    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return timestamp

    # ==================== DATA LOADING ====================

    def load_logs_from_db(self):
        """Load logs from SQLite database using Reports module"""
        logs = []
        try:
            log_entries = self.reports.get_log_entries()

            for log_entry in log_entries:
                try:
                    formatted_time = log_entry.get_realtime()
                    message = log_entry.get_description() or "N/A"
                    truncated_message = message[:100] + "..." if len(message) > 100 else message

                    severity_val = log_entry.get_severity()
                    if severity_val is None:
                        severity_val = "N/A"
                    
                    identifier_val = log_entry.get_syslog_identifier() or "N/A"

                    logs.append({
                        'datetime': formatted_time,
                        'message': truncated_message,
                        'full_message': message,
                        'severity': str(severity_val),
                        'identifier': str(identifier_val),
                        'hostname': "N/A",
                        'raw_format': log_entry.get_raw_format(),
                        'log_entry': log_entry
                    })

                except Exception as e:
                    print(f"Error processing log entry: {e}")
                    continue

        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading logs: {e}")

        return logs

    def _convert_log_entries_to_display(self, log_entries):
        """Convert LogEntry objects to display format"""
        display_logs = []
        for log_entry in log_entries:
            try:
                formatted_time = log_entry.get_realtime()
                message = log_entry.get_description() or "N/A"
                truncated_message = message[:100] + "..." if len(message) > 100 else message

                severity_val = log_entry.get_severity()
                if severity_val is None:
                    severity_val = "N/A"

                display_logs.append({
                    'datetime': formatted_time,
                    'message': truncated_message,
                    'full_message': message,
                    'severity': str(severity_val),
                    'identifier': str(log_entry.get_syslog_identifier() or "N/A"),
                    'hostname': "N/A",
                    'raw_format': log_entry.get_raw_format(),
                    'log_entry': log_entry
                })
            except Exception as e:
                print(f"Error converting log entry: {e}")
                continue

        return display_logs

    # ==================== UI CREATION ====================

    def create_logs_interface(self):
        """Create the main logs interface"""
        self.root = tk.Tk()
        self.root.title("CyberPolice - Security Logs Interface")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')

        self.filter_severity = tk.StringVar(self.root)
        self.filter_syslog = tk.StringVar(self.root)
        self.filter_datetime = tk.StringVar(self.root)

        self._create_header()
        self._create_control_panel()
        self._create_logs_table()

        # Load logs and populate dropdowns
        self.refresh_logs()
        self.populate_syslog_dropdown()

        self.root.mainloop()

    def _create_header(self):
        """Create header frame"""
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="Security Logs Viewer",
            font=('Helvetica', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(expand=True)

    def _create_control_panel(self):
        """Create control panel with buttons and filters"""
        control_frame = tk.Frame(self.root, bg='#ecf0f1', height=240)
        control_frame.pack(fill='x', padx=10, pady=5)
        control_frame.pack_propagate(False)

        # Action buttons
        self._create_action_buttons(control_frame)

        # Filter section
        self._create_filter_section(control_frame)

        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Loading logs...",
            font=('Helvetica', 10),
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.status_label.pack(pady=5)

    def _create_action_buttons(self, parent):
        """Create action buttons row"""
        button_frame = tk.Frame(parent, bg='#ecf0f1')
        button_frame.pack(fill='x', pady=5)

        # Left buttons
        left_buttons = tk.Frame(button_frame, bg='#ecf0f1')
        left_buttons.pack(side='left', padx=10)

        buttons_config = [
            ("Refresh Logs", self.refresh_logs, '#3498db'),
            ("Clear All Filters", self.clear_filter, '#f39c12'),
            ("Show Available Filter Values", self.show_available_values, '#9b59b6'),
            ("Generate Report", self.generate_logs_report, '#27ae60')
        ]

        for text, command, color in buttons_config:
            tk.Button(
                left_buttons,
                text=text,
                command=command,
                bg=color,
                fg='white',
                font=('Helvetica', 10, 'bold'),
                cursor='hand2',
                relief='flat',
                padx=15,
                pady=8
            ).pack(side='left', padx=5)

        # Center - Apply button
        center_button = tk.Frame(button_frame, bg='#ecf0f1')
        center_button.pack(side='left', expand=True, padx=20)

        tk.Button(
            center_button,
            text="APPLY FILTERS",
            command=self.apply_all_filters,
            bg='#2ecc71',
            fg='black',
            font=('Helvetica', 16, 'bold'),
            cursor='hand2',
            relief='raised',
            bd=5,
            padx=40,
            pady=15
        ).pack()

        # Right button
        right_buttons = tk.Frame(button_frame, bg='#ecf0f1')
        right_buttons.pack(side='right', padx=10)

        tk.Button(
            right_buttons,
            text="Back to Email Interface",
            command=self.go_to_email_interface,
            bg='#95a5a6',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=15,
            pady=8
        ).pack(side='left', padx=5)

    def _create_filter_section(self, parent):
        """Create filter section - FIXED VERSION"""
        filter_card = tk.Frame(parent, bg='white', relief='flat', bd=0)
        filter_card.pack(fill='x', pady=5, padx=10)

        # Filter header
        filter_header = tk.Frame(filter_card, bg='#8e44ad', height=40)
        filter_header.pack(fill='x')
        filter_header.pack_propagate(False)

        tk.Label(
            filter_header,
            text="Log Filtering Options",
            font=('Helvetica', 12, 'bold'),
            bg='#8e44ad',
            fg='white'
        ).pack(expand=True)

        # Filter content - FIXED: Set minimum height and prevent shrinking
        filter_content = tk.Frame(filter_card, bg='white', height=140)
        filter_content.pack(fill='x', padx=20, pady=15)
        filter_content.pack_propagate(False)  # Prevent frame from shrinking

        columns_frame = tk.Frame(filter_content, bg='white')
        columns_frame.pack(fill='both', expand=True)

        # Create filter columns
        self._create_severity_filter(columns_frame)
        self._create_syslog_filter(columns_frame)
        self._create_time_filter(columns_frame)

    def _create_severity_filter(self, parent):
        """Create severity filter column - FIXED VERSION"""
        severity_col = tk.Frame(parent, bg='white')
        severity_col.pack(side='left', fill='both', expand=True, padx=10)

        tk.Label(
            severity_col,
            text="SEVERITY FILTER",
            font=('Helvetica', 11, 'bold'),
            bg='white',
            fg='#e74c3c'
        ).pack(anchor='w', pady=(0, 5))

        tk.Label(
            severity_col,
            text="Select log importance level:",
            font=('Helvetica', 9),
            bg='white',
            fg='#7f8c8d'
        ).pack(anchor='w')

        # self.filter_severity = tk.StringVar()
        severity_values = ["", "0 - Emergency", "1 - Alert", "2 - Critical",
                          "3 - Error", "4 - Warning", "5 - Notice",
                          "6 - Info", "7 - Debug"]

        self.severity_combo = ttk.Combobox(
            severity_col,
            textvariable=self.filter_severity,
            values=severity_values,
            state='readonly',
            width=22
        )
        self.severity_combo.pack(anchor='w', pady=(5, 0), fill='x', padx=(0, 10))
        self.severity_combo.current(0)

    def _create_syslog_filter(self, parent):
        """Create syslog filter column - FIXED VERSION"""
        syslog_col = tk.Frame(parent, bg='white')
        syslog_col.pack(side='left', fill='both', expand=True, padx=10)

        tk.Label(
            syslog_col,
            text="SYSLOG FILTER",
            font=('Helvetica', 11, 'bold'),
            bg='white',
            fg='#3498db'
        ).pack(anchor='w', pady=(0, 5))

        tk.Label(
            syslog_col,
            text="Select service/application:",
            font=('Helvetica', 9),
            bg='white',
            fg='#7f8c8d'
        ).pack(anchor='w')

        # self.filter_syslog = tk.StringVar()
        self.syslog_combo = ttk.Combobox(
            syslog_col,
            textvariable=self.filter_syslog,
            values=[""],
            state='readonly',
            width=22
        )
        self.syslog_combo.pack(anchor='w', pady=(5, 0), fill='x', padx=(0, 10))
        self.syslog_combo.current(0)

    def _create_time_filter(self, parent):
        """Create time filter column with dropdown for last 10 days"""
        time_col = tk.Frame(parent, bg='white')
        time_col.pack(side='left', fill='both', expand=True, padx=10)

        tk.Label(
            time_col,
            text="TIME FILTER",
            font=('Helvetica', 11, 'bold'),
            bg='white',
            fg='#2ecc71'
        ).pack(anchor='w', pady=(0, 5))

        tk.Label(
            time_col,
            text="Show logs BEFORE this time:",
            font=('Helvetica', 9),
            bg='white',
            fg='#7f8c8d'
        ).pack(anchor='w', pady=(0, 5))

        # Create dropdown with last 10 days
        # self.filter_datetime = tk.StringVar()
        
        # Generate last 10 days with timestamp format
        datetime_values = self._generate_last_10_days()
        
        self.datetime_combo = ttk.Combobox(
            time_col,
            textvariable=self.filter_datetime,
            values=datetime_values,
            state='readonly',
            width=25,
            font=('Helvetica', 10)
        )
        self.datetime_combo.pack(anchor='w', pady=(5, 0), fill='x', padx=(0, 10))
        self.datetime_combo.current(0)  # Set to empty/first option

    def _generate_last_10_days(self):
        """Generate list of last 10 days with 00:00:00 timestamp"""
        from datetime import timedelta
        
        today = datetime.now()
        datetime_list = [""]  # Empty option first
        
        for i in range(10):
            day = today - timedelta(days=i)
            # Format: YYYY-MM-DD 00:00:00
            formatted = day.strftime('%Y-%m-%d 00:00:00')
            datetime_list.append(formatted)
        
        return datetime_list

    def _create_logs_table(self):
        """Create logs display table"""
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('datetime', 'message', 'severity', 'identifier')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=25)

        # Define column headings
        self.tree.heading('datetime', text='Date/Time (UTC)')
        self.tree.heading('message', text='Message')
        self.tree.heading('severity', text='Severity')
        self.tree.heading('identifier', text='Syslog Identifier')

        # Configure column widths
        self.tree.column('datetime', width=180, minwidth=150)
        self.tree.column('message', width=600, minwidth=400)
        self.tree.column('severity', width=120, minwidth=100)
        self.tree.column('identifier', width=200, minwidth=150)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)

        h_scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Bind double-click
        self.tree.bind('<Double-1>', self.show_log_details)

    # ==================== DISPLAY METHODS ====================

    def display_logs(self, logs):
        """Display logs in the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Configure severity colors
        for i in range(8):
            color = self.get_severity_color(str(i))
            self.tree.tag_configure(f'severity_{i}', background='white', foreground=color)

        # Insert logs
        for log in logs:
            # Handle "N/A" severity gracefully
            severity_val = log['severity']
            if severity_val == "N/A":
                severity_tag = 'severity_default'
                severity_display = "N/A - Unknown"
                self.tree.tag_configure('severity_default', background='white', foreground='#cccccc')
            else:
                severity_tag = f'severity_{severity_val}'
                severity_display = f"{severity_val} - {self.get_severity_label(severity_val)}"
            
            colored_datetime = f"● {log['datetime']}"

            self.tree.insert('', 'end',
                           values=(
                               colored_datetime,
                               log['message'],
                               severity_display,
                               log['identifier']
                           ),
                           tags=(severity_tag,))

        # Update status
        log_count = len(logs)
        filter_text = " (filtered)" if logs != self.all_logs else ""
        self.status_label.config(text=f"Showing {log_count} log entries{filter_text}")

    def populate_syslog_dropdown(self):
        """Populate the syslog dropdown with available identifiers"""
        try:
            log_entries = self.reports.get_log_entries()
            identifiers = set()

            for log_entry in log_entries:
                identifier = log_entry.get_syslog_identifier()
                if identifier and identifier != "N/A":
                    identifiers.add(identifier)

            sorted_identifiers = [""] + sorted(list(identifiers))
            self.syslog_combo['values'] = sorted_identifiers
            self.syslog_combo.current(0)

        except Exception as e:
            print(f"Error populating syslog dropdown: {e}")

    # ==================== FILTER METHODS ====================

    def refresh_logs(self):
        """Refresh the logs display"""
        try:
            self.all_logs = self.load_logs_from_db()
            self.display_logs(self.all_logs)
            self.status_label.config(text=f"Loaded {len(self.all_logs)} log entries successfully")
        except Exception as e:
            self.status_label.config(text=f"Error loading logs: {str(e)}")
            messagebox.showerror("Error", f"Failed to load logs:\n{e}")

    def apply_all_filters(self):
        """Apply all active filters and display results"""
        active_filters = []
        self.current_filter_info = []

        try:
            # Get filter values
            severity_str = self.filter_severity.get().strip()
            syslog_id = self.filter_syslog.get().strip()
            datetime_str = self.filter_datetime.get().strip()

            # If no filters are set, show all logs
            if not severity_str and not syslog_id and not datetime_str:
                self.display_logs(self.all_logs)
                messagebox.showinfo("No Filters Set", "No filters were set. Showing all logs.")
                return

            # Start with all log entries from database
            current_log_entries = self.reports.get_log_entries()

            # Apply Severity Filter
            if severity_str:
                try:
                    severity_int = int(severity_str.split(" - ")[0]) if " - " in severity_str else int(severity_str)
                    current_log_entries = [log for log in current_log_entries
                                          if log.get_severity() == severity_int]
                    active_filters.append(f"Severity = {severity_int}")
                except ValueError:
                    messagebox.showerror("Invalid Severity", f"Invalid severity value: '{severity_str}'")
                    return

            # Apply Syslog Filter
            if syslog_id:
                current_log_entries = [log for log in current_log_entries
                                      if log.get_syslog_identifier() == syslog_id]
                active_filters.append(f"Syslog = '{syslog_id}'")

            # Apply Time Filter
            if datetime_str:
                try:
                    # Convert "YYYY-MM-DD HH:MM:SS" to "YYYY-MM-DDTHH:MM:SS" for comparison
                    datetime_iso = datetime_str.replace(' ', 'T')
                    
                    current_log_entries = [log for log in current_log_entries
                                          if log.get_realtime() < datetime_iso]
                    active_filters.append(f"Time < {datetime_str}")

                except Exception as e:
                    messagebox.showerror("Time Filter Error",
                                       f"Error applying time filter.\n\n"
                                       f"Error: {e}")
                    return

            # Convert filtered log entries to display format
            final_filtered_logs = self._convert_log_entries_to_display(current_log_entries)

            # Store current filter info for report generation
            self.current_filter_info = active_filters

            # Display filtered results
            self.display_logs(final_filtered_logs)

            # Show result message
            filter_summary = "\n".join([f"• {f}" for f in active_filters])
            messagebox.showinfo("Filters Applied",
                              f"Found {len(final_filtered_logs)} log entries matching:\n\n{filter_summary}")

        except Exception as e:
            print(f"Filter error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Filter Error", f"Error applying filters:\n{e}")

    def show_available_values(self):
        """Show all available filter values"""
        try:
            log_entries = self.reports.get_log_entries()

            # Get severities
            severities = set()
            for log_entry in log_entries:
                severity = log_entry.get_severity()
                if severity is not None:
                    severities.add(severity)

            severity_list = sorted(list(severities))
            severity_text = "\n".join([f"{s} - {self.get_severity_label(str(s))}"
                                      for s in severity_list])

            # Get syslog identifiers
            identifiers = set()
            for log_entry in log_entries:
                identifier = log_entry.get_syslog_identifier()
                if identifier and identifier != "N/A":
                    identifiers.add(identifier)

            identifier_list = sorted(list(identifiers))
            identifier_text = "\n".join(identifier_list[:30])
            if len(identifier_list) > 30:
                identifier_text += f"\n... and {len(identifier_list) - 30} more"

            # Get time range
            if log_entries:
                first_time = log_entries[0].get_realtime()
                last_time = log_entries[-1].get_realtime()
                time_text = f"From: {first_time}\nTo: {last_time}"
            else:
                time_text = "No logs available"

            # Show all info
            info_text = (
                f"AVAILABLE SEVERITY VALUES:\n"
                f"{severity_text}\n\n"
                f"AVAILABLE SYSLOG IDENTIFIERS:\n"
                f"{identifier_text}\n\n"
                f"TIME RANGE:\n"
                f"{time_text}\n\n"
                f"Total logs in database: {len(log_entries)}"
            )

            messagebox.showinfo("Available Filter Values", info_text)

        except Exception as e:
            messagebox.showerror("Error", f"Error getting available values:\n{e}")

    def clear_filter(self):
        """Clear all filters"""
        self.filter_severity.set("")
        self.filter_syslog.set("")
        self.filter_datetime.set("")
        self.current_filter_info = []
        self.display_logs(self.all_logs)
        messagebox.showinfo("Filters Cleared", "All filters have been cleared.")

    def generate_logs_report(self):
        """Generate a Markdown report of currently displayed logs with email option"""
        try:
            # Get currently displayed logs from the treeview
            displayed_logs = []
            for item_id in self.tree.get_children():
                item = self.tree.item(item_id)
                values = item['values']

                # Find matching log from all_logs
                for log in self.all_logs:
                    colored_datetime = f"● {log['datetime']}"
                    if colored_datetime == values[0] and log['message'] == values[1]:
                        displayed_logs.append(log)
                        break

            if not displayed_logs:
                messagebox.showwarning("No Logs", "No logs available to generate report.")
                return

            # Ask if user wants to send via email
            send_email = messagebox.askyesno(
                "Email Report",
                f"Generate report for {len(displayed_logs)} log entries.\n\n"
                "Do you want to send this report via email?\n"
                "(Email must be configured in Email Interface)"
            )

            # Generate report with email option
            filter_info = self.current_filter_info if self.current_filter_info else None
            success, result = self.report_generator.generate_report(
                displayed_logs,
                filter_info,
                send_email=send_email
            )

            if success:
                email_status = "\n✉️ Email sent successfully!" if send_email else ""
                if "Email sending failed" in result:
                    email_status = "\n⚠️ Report saved but email sending failed.\nPlease check your email configuration."

                messagebox.showinfo(
                    "Report Generated",
                    f"Report successfully generated!\n\n"
                    f"Location: {result}\n"
                    f"Log entries included: {len(displayed_logs)}"
                    f"{email_status}"
                )
            else:
                messagebox.showerror("Report Error", f"Failed to generate report:\n{result}")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating report:\n{e}")

    # ==================== DETAIL VIEW ====================

    def show_log_details(self, event):
        """Show detailed log information"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        # Find matching log
        selected_log = None
        for log in self.all_logs:
            colored_datetime = f"● {log['datetime']}"
            if colored_datetime == values[0] and log['message'] == values[1]:
                selected_log = log
                break

        if not selected_log:
            messagebox.showwarning("Log Not Found", "Could not find the selected log entry.")
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

        tk.Label(
            header_frame,
            text="Log Entry Details",
            font=('Helvetica', 16, 'bold'),
            bg='#34495e',
            fg='white'
        ).pack(expand=True)

        # Scrollable text area
        text_frame = tk.Frame(detail_window, bg='#f0f0f0')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)

        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 10))
        text_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)

        text_widget.pack(side='left', fill='both', expand=True)
        text_scrollbar.pack(side='right', fill='y')

        # Format details
        try:
            raw_format_json = json.loads(selected_log['raw_format'])
            formatted_json = json.dumps(raw_format_json, indent=2)
        except:
            formatted_json = selected_log['raw_format']

        details = f"""
LOG ENTRY DETAILS
{'=' * 80}

Date/Time: {selected_log['datetime']}
Hostname: {selected_log['hostname']}
Severity: {selected_log['severity']} - {self.get_severity_label(selected_log['severity'])}
Identifier: {selected_log['identifier']}

Full Message:
{'-' * 80}
{selected_log['full_message']}

Raw Log Format (JSON):
{'-' * 80}
{formatted_json}
"""

        text_widget.insert('1.0', details)
        text_widget.config(state='disabled')

        # Close button
        tk.Button(
            detail_window,
            text="Close",
            command=detail_window.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Helvetica', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=20,
            pady=8
        ).pack(pady=10)

    # ==================== NAVIGATION ====================

    def go_to_email_interface(self):
        """Navigate back to email interface"""
        self.root.destroy()
        try:
            from ui.email_interface import create_email_interface
            create_email_interface()
        except ImportError:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            try:
                from ui.email_interface import create_email_interface
                create_email_interface()
            except Exception as e:
                messagebox.showerror("Navigation Error", 
                                   f"Could not load email interface:\n{e}\n\n"
                                   f"Please ensure email_interface.py exists in the ui/ folder.")


def create_logs_interface():
    """Function to create and run the logs interface"""
    app = LogsInterface()
    app.create_logs_interface()


if __name__ == '__main__':
    create_logs_interface()