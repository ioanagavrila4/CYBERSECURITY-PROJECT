"""
Log Report Generator Module
Generates formatted Markdown reports from security logs
"""

import os
import resend
from datetime import datetime
from collections import Counter

import markdown

# Import email configuration function
try:
    from ui.email_interface import get_email_config
except ImportError:
    # Fallback if email_interface is not available
    def get_email_config():
        return {'alert_email': '', 'alert_priority': 6}


class LogReportGenerator:
    """Generates Markdown reports from log data"""

    def __init__(self, api_key: str = "re_S5RXcYYE_Kkaz3zskzALB5Jh2Dbwjghc4"):
        self.report_dir = "reports"
        self._ensure_report_directory()

        # Setup Resend for email sending
        resend.api_key = api_key
        self.sender_email = "onboarding@resend.dev"

        # Load email configuration
        self._load_email_config()

    def _load_email_config(self):
        """Load email configuration from the interface"""
        config = get_email_config()
        self.recipient_email = config.get('alert_email', '')

    def _ensure_report_directory(self):
        """Create reports directory if it doesn't exist"""
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def _get_severity_label(self, severity):
        """Return severity label"""
        severity_labels = {
            '0': 'Emergency', '1': 'Alert', '2': 'Critical', '3': 'Error',
            '4': 'Warning', '5': 'Notice', '6': 'Info', '7': 'Debug'
        }
        return severity_labels.get(str(severity), 'Unknown')

    def _calculate_statistics(self, logs):
        """Calculate summary statistics from logs"""
        total_logs = len(logs)

        # Count by severity
        severity_counter = Counter()
        identifier_counter = Counter()

        for log in logs:
            severity = log.get('severity', 'N/A')
            if severity != 'N/A':
                severity_counter[severity] += 1

            identifier = log.get('identifier', 'N/A')
            if identifier != 'N/A':
                identifier_counter[identifier] += 1

        return {
            'total': total_logs,
            'by_severity': severity_counter,
            'by_identifier': identifier_counter
        }

    def _generate_markdown_content(self, logs, filter_info=None):
        """Generate Markdown formatted report content"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        stats = self._calculate_statistics(logs)

        # Build markdown
        md = []
        md.append("# Security Logs Report")
        md.append(f"\n**Generated:** {timestamp}\n")
        md.append("---\n")

        # Summary Statistics
        md.append("## Summary Statistics\n")
        md.append(f"- **Total Log Entries:** {stats['total']}\n")

        # Severity breakdown
        if stats['by_severity']:
            md.append("\n### Severity Breakdown\n")
            for severity in sorted(stats['by_severity'].keys()):
                count = stats['by_severity'][severity]
                label = self._get_severity_label(severity)
                percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
                md.append(f"- **{severity} - {label}:** {count} ({percentage:.1f}%)\n")

        # Top identifiers
        if stats['by_identifier']:
            md.append("\n### Top 10 Syslog Identifiers\n")
            top_identifiers = stats['by_identifier'].most_common(10)
            for identifier, count in top_identifiers:
                percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
                md.append(f"- **{identifier}:** {count} ({percentage:.1f}%)\n")

        # Filter information
        if filter_info:
            md.append("\n## Applied Filters\n")
            for filter_item in filter_info:
                md.append(f"- {filter_item}\n")
        else:
            md.append("\n## Applied Filters\n")
            md.append("- *No filters applied (showing all logs)*\n")

        # Logs table
        md.append("\n---\n")
        md.append("## Log Entries\n")
        md.append("\n| Date/Time | Severity | Identifier | Message |\n")
        md.append("|-----------|----------|------------|----------|\n")

        for log in logs:
            datetime_val = log.get('datetime', 'N/A')
            severity_val = log.get('severity', 'N/A')
            if severity_val != 'N/A':
                severity_display = f"{severity_val} - {self._get_severity_label(severity_val)}"
            else:
                severity_display = "N/A"

            identifier_val = log.get('identifier', 'N/A')
            message_val = log.get('message', 'N/A')

            # Escape pipe characters in message to avoid breaking table
            message_val = message_val.replace('|', '\\|')

            md.append(f"| {datetime_val} | {severity_display} | {identifier_val} | {message_val} |\n")

        md.append("\n---\n")
        md.append(f"\n*Report generated by CyberPolice Security Logs System on {timestamp}*\n")

        return ''.join(md)

    def generate_report(self, logs, filter_info=None, send_email=False):
        """
        Generate and save a Markdown report

        Args:
            logs: List of log dictionaries to include in report
            filter_info: Optional list of filter descriptions applied
            send_email: Whether to send the report via email

        Returns:
            tuple: (success: bool, filepath: str or error_message: str)
        """
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            filename = f"logs_report_{timestamp}.md"
            filepath = os.path.join(self.report_dir, filename)

            # Generate markdown content
            markdown_content = self._generate_markdown_content(logs, filter_info)

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Send email if requested
            if send_email:
                email_success = self.send_report_email(filepath, len(logs))
                if not email_success:
                    return True, f"{filepath} (Note: Email sending failed)"

            return True, filepath

        except Exception as e:
            return False, str(e)

    def from_md_to_html(self, logs, filter_info=None):
        success, filepath_to_md = self.generate_report(logs, filter_info, send_email=False)

        with open(filepath_to_md, 'r', encoding='utf-8') as f:
            md_content = f.read()

            # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)

        # Save HTML to corresponding file
        html_filepath = os.path.splitext(filepath_to_md)[0] + '.html'
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return html_filepath

    def send_report_email(self, report_filepath, log_count):
        """
        Send the generated report via email using Resend

        Args:
            report_filepath: Path to the generated report file
            log_count: Number of logs in the report

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Reload config in case it changed
        self._load_email_config()

        # Skip sending if no recipient email configured
        if not self.recipient_email:
            print("No recipient email configured, skipping email")
            return False

        try:
            # Read the markdown file content
            with open(report_filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Convert markdown to HTML
            html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

            # Create full HTML email with styling
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Logs Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        ul li {{
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }}
        ul li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: #3498db;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 30px 0;
        }}
        strong {{
            color: #2c3e50;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""

            # Plain text version as fallback
            text_body = f"""Your log report has been generated successfully.

Report Details:
- Total Log Entries: {log_count}
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{md_content}

---

This is an automated report from your cybersecurity monitoring system.
"""

            # Prepare email
            subject = "📊 Your Log Report Generated"

            params = {
                "from": self.sender_email,
                "to": [self.recipient_email],
                "subject": subject,
                "text": text_body,
                "html": html_content
            }

            email = resend.Emails.send(params)
            print(f"Report email sent successfully (ID: {email.get('id', 'unknown')})")
            return True

        except Exception as e:
            print(f"Failed to send report email: {e}")
            return False

