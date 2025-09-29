import resend
import sqlite3
import time
import threading
from typing import Optional
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from domain.LogEntry import LogEntry

# Import email configuration function
try:
    from ui.email_interface import get_email_config
except ImportError:
    # Fallback if email_interface is not available
    def get_email_config():
        return {'alert_email': '', 'alert_priority': 6}

class AlertSender:
    def __init__(self, api_key: str = "re_S5RXcYYE_Kkaz3zskzALB5Jh2Dbwjghc4", db_path: str = "data/Sqlite3.db"):
        resend.api_key = api_key
        self.sender_email = "onboarding@resend.dev"
        self.db_path = db_path
        self.monitoring = False
        self.monitor_thread = None

        # Load email configuration
        self._load_email_config()

    def _load_email_config(self):
        """Load email configuration from the interface"""
        config = get_email_config()
        self.recipient_email = config.get('alert_email', 'ioanavalerya@gmail.com')  # fallback to original
        self.alert_priority_threshold = config.get('alert_priority', 4)  # configurable threshold

    def send_security_alert(self, log_entry, sender_email: str = None, sender_password: str = None) -> bool:
        """
        Send security alert email for critical log entries

        Args:
            log_entry: LogEntry object that meets priority threshold
            sender_email: Not used with Resend (kept for compatibility)
            sender_password: Not used with Resend (kept for compatibility)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Reload config in case it changed
        self._load_email_config()

        # Skip sending if no recipient email configured
        if not self.recipient_email:
            print("No recipient email configured, skipping alert")
            return False
        try:
            severity_names = {
                "0": "EMERGENCY",
                "1": "ALERT",
                "2": "CRITICAL",
                "3": "ERROR",
                "4": "WARNING",
                "5": "NOTICE",
                "6": "INFORMATIONAL"
            }

            severity_name = severity_names.get(str(log_entry.get_severity()), "UNKNOWN")

            subject = f"📊 Log Alert: {severity_name} - {log_entry.get_syslog_identifier()}"

            body = f"""
Log Alert Detected

Severity: {severity_name} (Priority {log_entry.get_severity()})
Syslog Identifier: {log_entry.get_syslog_identifier()}
Timestamp: {log_entry.get_realtime()}
Message: {log_entry.get_description()}

Raw Log Entry:
{log_entry.get_raw_format()[:500]}...

This is an automated alert from your cybersecurity monitoring system.
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
        Check if log priority requires alerting based on configured threshold

        Args:
            priority: Priority string from log entry

        Returns:
            bool: True if priority meets or exceeds threshold, False otherwise
        """
        if priority is None:
            return False

        try:
            priority_int = int(priority)
            # Alert if priority is <= configured threshold (0=Emergency...6=Info)
            return priority_int <= self.alert_priority_threshold
        except (ValueError, TypeError):
            return False

    def check_new_logs(self):
        """Check for new log entries and send alerts based on configured priority threshold"""
        try:
            connection_obj = sqlite3.connect(self.db_path)
            cursor_obj = connection_obj.cursor()

            # Get all unprocessed logs - we'll filter by priority in code
            query = "SELECT id,raw_format, time_stamp, severity, description, syslog_identifier, updated FROM logs WHERE updated = 0"
            cursor_obj.execute(query)

            new_logs = cursor_obj.fetchall()
            print(f'DEBUG: number of new log entries {len(new_logs)}')

            for log_row in new_logs:
                log_id, raw_format, timestamp, severity, description, syslog_identifier, updated = log_row

                log_entry = LogEntry(raw_format)

                update_query = "UPDATE logs SET updated = 1 WHERE id = ?"
                cursor_obj.execute(update_query, (log_id,))
                connection_obj.commit()

                if self.is_alert_priority(severity):
                    self.send_security_alert(log_entry)

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
