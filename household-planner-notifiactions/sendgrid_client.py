import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

from db.db import access_secret_version


sg_client = sendgrid.SendGridAPIClient(api_key=access_secret_version("send-grid-api-key"))


def send_notification(sender_email: str, email: str, subject: str, content: str):
    from_email = Email(sender_email)
    to_email = To(email)
    content = Content("text/plain", content)
    mail = Mail(from_email, to_email, subject, content)
    mail_json = mail.get()

    response = sg_client.client.mail.send.post(request_body=mail_json)

    return response