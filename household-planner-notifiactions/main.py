from datetime import timedelta, datetime
from typing import Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

import pytz

import sendgrid_client

from mako.template import Template

from firestore_client import get_mail_template

from db.db import engine

from sqlalchemy import text

app = FastAPI()
origins = ["*"]

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/send_notifications")
async def send_notifications():
    with engine.connect() as con:
        batch = con.execute("""SELECT chor_id,
                       chor_start_date,
                       chor_occurence,
                       chor_name,
                       chor_description,
                       user_name,
                       user_email
                FROM chores
                         JOIN household_members hm on hm.hsme_id = chores.chor_hsme_id
                         JOIN users u on hm.hsme_user_id = u.user_id
                WHERE MOD(EXTRACT(DAY FROM (NOW() - chor_start_date))::SMALLINT, chor_occurence) = 0
                  AND EXTRACT(HOUR FROM NOW()) >= EXTRACT(HOUR FROM chor_start_date) - 1
                  AND ((chore_last_notification_sent_at IS NOT NULL
                    AND chore_last_notification_sent_at::DATE <> NOW()::DATE)
                    OR chore_last_notification_sent_at IS NULL)
                  LIMIT 5""")

    for rs in batch:
        process(rs)


def process(rs: Tuple):
    chor_id = rs[0]
    chor_start_date = rs[1]
    chor_occurence = rs[2]
    chor_name = rs[3]
    chor_description = rs[4]
    user_name = rs[5]
    user_email = rs[6]

    mail_tmp = get_mail_template()

    timezone = pytz.timezone('Europe/Warsaw')
    next_occurence_date = calculate_next_occurence_date(chor_start_date, chor_occurence).replace(tzinfo=pytz.utc).astimezone(timezone)
    tmp = Template(mail_tmp.content).render(user_name=user_name, chor_name=chor_name,
                                            next_occurence_date=f"{next_occurence_date.hour:02d}:{next_occurence_date.minute:02d}",
                                            chor_description=chor_description)

    status = sendgrid_client.send_notification(mail_tmp.from_mail, user_email, chor_name, tmp)

    with engine.connect() as con:
        con.execute(text("""
        UPDATE chores
        SET chore_last_notification_sent_at = CURRENT_TIMESTAMP 
        WHERE chor_id = :chor_id"""), chor_id=chor_id)


def calculate_next_occurence_date(s_date, interval):
    start_date = s_date.replace(tzinfo=pytz.UTC)
    now = datetime.now().replace(tzinfo=pytz.UTC)
    if now <= start_date:
        return start_date
    delta = now - start_date
    delta_days = delta.days
    mod = delta_days % interval
    next_occurence_date = start_date + timedelta(days=(delta_days + (interval - mod)))
    return next_occurence_date


