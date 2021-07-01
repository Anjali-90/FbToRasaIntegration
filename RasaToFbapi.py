import sys
from fastapi import FastAPI , Request, Response, responses
import fastapi
import requests
import json
from requests.models import REDIRECT_STATI
from starlette.routing import Router
import uvicorn
from pymessenger import Bot

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.requests import HTTPConnection as HTTPConnection
from starlette.requests import Request as Request
import logging

from pydantic import BaseModel
from typing import Dict, List
import httpx
import os



app = FastAPI()
logger = logging.getLogger("gunicorn.error")


VERIFY_TOKEN = "Multimoodbot"
PAGE_ACCESS_TOKEN = "EAAEiZBzDtyvMBADc7Dxgt5XbzZBcREteVT7qN67BmcyFkzoehns0TNiRZAyJ5J2VMAqQe68qZAHG9g3EQvueCXuSiiZCb6ogYG9UKPGZBbff8yt6Yj4bHxCKZAYWRrTSg1XZBwsIoSH6xY7FdXSxrZCVo3TXwenJhegclJvvNOigW3uhwkuvTrZCqY"
#bot = Bot(PAGE_ACCESS_TOKEN)

async def send_message(
    page_access_token: str,
    recipient_id: str,
    message_text: str,
    message_type: str = "UPDATE",
):
    """
    Send message to specific user(By recipient ID) from specific page(By
    access token).
    Arguments:
        page_access_token: (string) Target page access token.
        recipient_id: (string) The ID of the user that the message is
         addressed to.
        message_text: (string) The content of the message.
        message_type: (string) The type of the target message.
         RESPONSE, UPDATE or MESSAGE_TAG - the accurate description -
         https://developers.facebook.com/docs/messenger-platform/send-messages/#messaging_types
    """
    r = httpx.post(
        "https://graph.facebook.com/v11.0/me/messages",
        params={"access_token": page_access_token},
        headers={"Content-Type": "application/json"},
        json={
            "recipient": {"id": recipient_id},
            "message": {"text": message_text},
            "messaging_type": message_type,
        },
    )
    #r.raise_for_status()   

# Adds support for GET requests to our webhook
@app.get('/webhook')
async def verify(request: Request):
    """
    On webook verification VERIFY_TOKEN has to match the token at the
    configuration and send back "hub.challenge" as success.
    """
    if request.query_params.get("hub.mode") == "subscribe" and request.query_params.get("hub.challenge"):
        if (not request.query_params.get("hub.verify_token") == VERIFY_TOKEN):
            return Response(content="Verification token mismatch", status_code=403)
        return Response(content=request.query_params["hub.challenge"])

    return "Webhook Verified",200


@app.post('/webhook')
async def recieve_msg(request : Request):
    data = await request.json() 

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                #Extract ids
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else:
                        messaging_text = 'No text'
                    
                    response = messaging_text 
                    sender = sender_id

                    r=requests.post('http://localhost:5005/webhooks/rest/webhook' , json={"sender": sender, "message":messaging_text})
                    list_of_dict= r.json()
                    
                    for i in list_of_dict:

                        dictionary=i
                        if 'text' in dictionary.keys() :
                            bot_message=i['text']
                        else :
                            bot_message=i['image']        

                        await send_message(page_access_token= PAGE_ACCESS_TOKEN , recipient_id=sender_id, message_text = bot_message)

                    #bot.send_text_message(sender_id,response)
                
    return "OK",200

   
if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1",port = 8000)



