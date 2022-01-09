from dataclasses import dataclass

from google.cloud import firestore


db = firestore.Client()


@dataclass
class MailTemplate:
    from_mail: str
    content: str


def get_mail_template():
    mail_template = db.collection("templates").document("mail").get()

    return MailTemplate(content=mail_template.get("content"), from_mail=mail_template.get("from_mail"))
