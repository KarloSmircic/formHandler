from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import urllib.parse
import json

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

app = FastAPI()

file = open("setup.json", "r")
setup = file.read()
file.close()
setup = json.loads(setup)

APIKEY = os.getenv("APIKEY")

@app.post("/{url}/")
async def root(url, request: Request):
    formtype = setup.get(url)
    if formtype == None: return "There was an error please contact the admin."

    a = urllib.parse.parse_qs(await request.body(), keep_blank_values=True)
    a = {k.decode("utf-8"): list(map(lambda x: x.decode("utf-8"), v)) for k, v in a.items()}
    emailOut = {}
    for k, v in a.items():
        if k[0] != "_":
            emailOut[k] = v

    html_message = formtype["message_before"]
    for k, v in emailOut.items():
        html_message += f"<br>{k}: {v}"

    message = Mail(
        from_email=formtype["from"],
        to_emails=formtype["recipients"],
        subject=formtype["title"],
        html_content=html_message)
    try:
        sg = SendGridAPIClient(APIKEY)
        response = sg.send(message)
        if response != 202:
            print(response.status_code)
            print(response.body)
            print(response.headers)
    except Exception as e:
        print(e)
        return "There was an error please contact the admin."

    return RedirectResponse(a["_redirect"][0])
