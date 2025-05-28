import imaplib
import email

from email.header import decode_header
from config import EMAIL, PASSWORD, client

def decode_header_value(value):
    """
    Decodes an email header value into a readable string.
    If header is missing, returns '(no subject)'.
    """
    if not value:
        return "(no subject)"
    decoded, charset = decode_header(value)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(charset or "utf-8", errors="ignore")
    return decoded

def summarize_email(text):
    """
    Summarizes the given email text using OpenAI GPT.
    Returns a short summary.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You briefly explain the essence of the email."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error summarizing email: {e}"

def check_inbox(limit=5):
    """
    Connects to Gmail inbox via IMAP, retrieves the last `limit` emails,
    decodes subjects and senders, summarizes the email body with GPT,
    and returns a formatted summary string.
    """
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        _, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        sorted_ids = sorted(email_ids, key=lambda x: int(x))[-limit:]

        output = []
        for num in sorted_ids:
            _, data = mail.fetch(num, "(RFC822)")
            for part in data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    subject = decode_header_value(msg["Subject"])
                    sender = decode_header_value(msg.get("From"))

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                charset = part.get_content_charset()
                                body = part.get_payload(decode=True).decode(charset or "utf-8", errors="ignore")
                                break
                    else:
                        charset = msg.get_content_charset()
                        body = msg.get_payload(decode=True).decode(charset or "utf-8", errors="ignore")

                    summary = summarize_email(body[:1000])
                    output.append(f"From:: {sender}\nSubject: {subject}\n {summary}\n")

        mail.logout()
        return "\n".join(output) if output else "No emails."

    except Exception as e:
        return f"Error checking mail: {e}"
