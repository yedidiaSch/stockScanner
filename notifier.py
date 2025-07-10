import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(
    tickers,
    html_reports,
    recipient_email,
    sender_email,
    sender_password
):
    """
    Sends an HTML email alert with symbols and their fundamental reports.

    Parameters:
        tickers (list): List of stock symbols with buy signals.
        html_reports (list): List of HTML report strings (same order as tickers).
        recipient_email (str): Email address of the recipient.
        sender_email (str): Email address of the sender.
        sender_password (str): Password for the sender's email account.
    """
    if not tickers:
        return

    # Construct the HTML body
    html = """
    <html>
    <head>
    <style>
      body { font-family: Arial, sans-serif; }
      table { border-collapse: collapse; width: 80%; margin-bottom:20px; }
      th, td { border: 1px solid #ddd; padding: 6px; }
      th { background-color: #4CAF50; color: white; }
    </style>
    </head>
    <body>
    """

    html += "<h2>📈 Buy Signals Alert</h2>"
    html += "<p><b>Symbols with signals:</b></p>"
    html += "<ul>"
    for t in tickers:
        html += f"<li>{t}</li>"
    html += "</ul><hr>"

    for report in html_reports:
        html += report + "<hr>"

    html += "</body></html>"

    # Create the email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📈 Trading Signals and Fundamentals"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    text_part = MIMEText("Signals: " + ", ".join(tickers), "plain")
    html_part = MIMEText(html, "html")

    msg.attach(text_part)
    msg.attach(html_part)

    # Send the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Email sent.")
