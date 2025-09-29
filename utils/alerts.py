import resend
import sqlite3
import time
import threading
from typing import Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.LogEntry import LogEntry

class AlertSender:
    def __init__(self, api_key: str = "re_Sfmiu7dp_EwgtNFH1LPy4GQgTqiQRktoD", db_path: str = "../data/Sqlite3.db"):
        resend.api_key = api_key
        self.recipient_email = "ioanavalerya@gmail.com"
        self.sender_email = "onboarding@resend.dev"
        self.db_path = db_path
        self.monitoring = False
        self.monitor_thread = None



    def send_security_alert(self, log_entry, sender_email: str = None, sender_password: str = None) -> bool:
        """
        Send security alert email for critical log entries

        Args:
            log_entry: LogEntry object with severity 5-6
            sender_email: Not used with Resend (kept for compatibility)
            sender_password: Not used with Resend (kept for compatibility)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            severity_names = {
                "5": "NOTICE",
                "6": "INFORMATIONAL"
            }

            severity_name = severity_names.get(str(log_entry.get_severity()), "UNKNOWN")

            subject = f"📊 Log Alert: {severity_name} - {log_entry.get_hostname()}"

            body = f"""
Log Alert Detected

Severity: {severity_name} (Priority {log_entry.get_severity()})
Hostname: {log_entry.get_hostname()}
Timestamp: {log_entry.get_realtime()}
Message: {log_entry.get_description()}

Raw Log Entry:
{log_entry.get_raw_format()[:500]}...

This is an automated alert from your cybersecurity monitoring system for priority 5-6 events.
"""

            params = {
                "from": self.sender_email,
                "to": [self.recipient_email],
                "subject": subject,
                "text": body,
            }

            email = resend.Emails.send(params)
            print(f"Alert email sent for {severity_name} event (ID: {email.get('id', 'unknown')})")
            return True

        except Exception as e:
            print(f"Failed to send alert email: {e}")
            return False

    def is_alert_priority(self, priority: Optional[str]) -> bool:
        """
        Check if log priority requires alerting (5-6)

        Args:
            priority: Priority string from log entry

        Returns:
            bool: True if priority is 5-6, False otherwise
        """
        if priority is None:
            return False

        try:
            priority_int = int(priority)
            return priority_int in [5, 6]
        except (ValueError, TypeError):
            return False

    def check_new_logs(self):
        """Check for new log entries and send alerts for severity 5-6"""
        try:
            connection_obj = sqlite3.connect(self.db_path)
            cursor_obj = connection_obj.cursor()

            query = "SELECT id,raw_format, time_stamp, severity, description, hostname, updated FROM logs WHERE updated = 0 AND severity IN ('5', '6')"
            cursor_obj.execute(query)

            new_logs = cursor_obj.fetchall()

            for log_row in new_logs:
                log_id, raw_format, timestamp, severity, description, hostname, updated = log_row

                log_entry = LogEntry(raw_format)

                if self.is_alert_priority(severity):
                    if self.send_security_alert(log_entry):
                        update_query = "UPDATE logs SET updated = 1 WHERE id = ?"
                        cursor_obj.execute(update_query, (log_id,))


            connection_obj.commit()
            connection_obj.close()

        except sqlite3.Error as e:
            print(f"Database error while checking new logs: {e}")
        except Exception as e:
            print(f"Error checking new logs: {e}")

    def start_monitoring(self, interval: int = 30):
        """
        Start monitoring for new log entries

        Args:
            interval: Check interval in seconds (default 30)
        """
        if self.monitoring:
            print("Monitoring is already running")
            return

        self.monitoring = True

        def monitor_loop():
            print(f"Started log monitoring with {interval}s interval")
            while self.monitoring:
                self.check_new_logs()
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring for new log entries"""
        if self.monitoring:
            self.monitoring = False
            print("Stopped log monitoring")
        else:
            print("Monitoring is not running")

    def is_critical_priority(self, priority: Optional[str]) -> bool:
        """
        Check if log priority requires alerting (0-3) - kept for backward compatibility

        Args:
            priority: Priority string from log entry

        Returns:
            bool: True if priority is 0-3, False otherwise
        """
        if priority is None:
            return False

        try:
            priority_int = int(priority)
            return 0 <= priority_int <= 3
        except (ValueError, TypeError):
            return False
