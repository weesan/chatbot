import requests
from enum import IntEnum

MIN_CONF = 0.90

class User:
    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp
        self.new_user = True

class Nlp(IntEnum):
    NONE      = 0x0000
    BYE       = 0x0001
    GREETINGS = 0x0002
    SENTIMENT = 0x0004
    THANKS    = 0x0008

BUILTIN_TRAITS = [{
    "trait": "bye",
    "enum": Nlp.BYE,
}, {
    "trait": "greetings",
    "enum": Nlp.GREETINGS,
}, {
    "trait": "sentiment",
    "enum": Nlp.SENTIMENT,
}, {
    "trait": "thanks",
    "enum": Nlp.THANKS,
}]

class FBChatBot:
    FB_MESSENGER_EP = "https://graph.facebook.com/v16.0/me/messages"

    def __init__(self, access_token, verify_token):
        self._access_token = access_token
        self._verify_token = verify_token
        self._users = {}

    def reply(self, user, msg):
        message_data = {
            "recipient": { "id":   user.id },
            "message":   { "text": msg }
        }
        resp = requests.post(
            "%s?access_token=%s" % (self.FB_MESSENGER_EP, self._access_token),
            json = message_data)

        return resp.content.decode("ascii", "ignore")

    def quick_reply(self, user, title, msgs):
        message_data = {
            "recipient": { "id":   user.id },
            "message":   { "text": title, "quick_replies": [] }
        }

        for msg in msgs:
            message_data["message"]["quick_replies"].append({
                "content_type": "text",
                "title": msg,
                "payload": msg,
            })

        resp = requests.post(
            "%s?access_token=%s" % (self.FB_MESSENGER_EP, self._access_token),
            json = message_data)

        return resp.content.decode("ascii", "ignore")

    def generic_reply(self, user, title, msgs):
        message_data = {
            "recipient": { "id":   user.id },
            "message":   {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": msgs
                    }
                }
            }
        }

        resp = requests.post(
            "%s?access_token=%s" % (self.FB_MESSENGER_EP, self._access_token),
            json = message_data)

        return resp.content.decode("ascii", "ignore")

    '''
        "text": "...",
        "nlp": {
          "intents": [],
          "entities": {},
          "traits": {
            "wit$greetings": [
              {
                "id": "5900cc2d-41b7-45b2-b21f-b950d3ae3c5c",
                "value": "true",
                "confidence": 0.6191
              }
            ],
            "wit$bye": [
              {
                "id": "5900cc2e-09ed-4764-800c-11e7566acfac",
                "value": "true",
                "confidence": 0.9957
              }
            ]
          },
          "detected_locales": [
            {
              "locale": "en_XX",
              "confidence": 0.925
            }
          ]
        }
    '''
    def process_nlp(self, message):
        nlp = message.get("nlp")
        if not nlp: return Nlp.NONE

        traits = nlp.get("traits")
        if not traits: return Nlp.NONE

        res = Nlp.NONE
        for bt in BUILTIN_TRAITS:
            trait = "wit$%s" % bt["trait"]
            if (t := traits.get(trait)) and t[0]["confidence"] >= MIN_CONF:
                res |= bt["enum"]

        return res

    # Default is to echo back the text.
    def process_text(self, user, text, nlp = Nlp.NONE):
        return self.reply(user, text)

    '''
    Verification request:
    GET /webhook?hub.mode=subscribe&hub.challenge=947897363&hub.verify_token=TOKEN H
    TP/1.1
    Host: weesan.serveo.net
    Accept: */*
    Accept-Encoding: deflate, gzip
    User-Agent: facebookplatform/1.0 (+http://developers.facebook.com)
    X-Forwarded-For: 66.220.149.15

    Verification response:
    HTTP/1.0 200 OK
    Connection: close
    Content-Length: 9
    Content-Type: text/html; charset=utf-8
    Date: Wed, 15 May 2019 06:01:58 GMT
    Server: Werkzeug/0.15.2 Python/3.7.3

    947897363
    '''
    def verify(self, args):
        if args['hub.verify_token'] == self._verify_token:
            return args['hub.challenge']
        else:
            return "Invalid verification token"

    '''
    Text request:
    {
      "object": "page",
      "entry": [
        {
          "id": "395792661277528",
          "time": 1557726791572,
          "messaging": [
            {
              "sender": {
                "id": "2458090410869460"
              },
              "recipient": {
                "id": "395792661277528"
              },
              "timestamp": 1557726791132,
              "message": {
                "mid": "X2ID5EVdGxMY89VniMQ58iJy4yxtACA9aeK5fajmiR1x-XS-a88dcfaoppB0w5D_fUm7SpsM31mdUrVHtf5WA",
                "seq": 64747,
                "text": "hello"
              }
            }
          ]
        }
      ]
    }

    Emoji (sticker) request:
    {
      "object": "page",
      "entry": [
        {
          "id": "395792661277528",
          "time": 1557728034680,
          "messaging": [
            {
              "sender": {
                "id": "2458090410869460"
              },
              "recipient": {
                "id": "395792661277528"
              },
              "timestamp": 155772803237,
              "message": {
                "mid": "NVkxO1XQ-GECUffiCL8-fCJy4yxtACA9aeK5fajmiPQz40gND9lCxFkjUvkHQYYZPwHi8Op2fQWGaaYN1qMGlw",
                "seq": 64785,
                "sticker_id": 369239263222822,
                "attachments": [
                  {
                    "type": "imae",
                    "payload": {
                      "url": "https://scontent.xx.fbcdn.net/v/t39.1997-6/39178562_1505197616293642_5411344281094848512_n.png?_nc_cat=1&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.x&oh=c1c5aa96b479af93269dbd2d55e97a0e&oe=5D559475",
                      "Sticker_id": 369239263222822
                    }
                  }
                ]
              }
            }
          ]
        }
      ]
    }

    '''
    def process(self, data = {}):
        if "object" not in data:
            # XXX
            return "Error: missing object!"

        for entry in data["entry"]:
            entry_id = entry["id"]
            time = entry["time"]

            for messaging in entry["messaging"]:
                sender    = messaging["sender"]["id"]
                recipient = messaging["recipient"]["id"]
                timestamp = messaging["timestamp"]

                user = None
                if sender in self._users:
                    user = self._users[sender]
                    user.new_user = False
                else:
                    user = User(sender, timestamp)
                    self._users[sender] = user

                resp = "To be implememt"
                if "message" in messaging:
                    message = messaging["message"]
                    nlp = self.process_nlp(message)

                    if "text" in message:
                        self.process_text(user, message["text"], nlp)
                    elif "sticker_id" in message:
                        self.reply(user, ":)")

                elif "optin" in messaging:
                    self.reply(user, "optin")
                    pass
                elif "delivery" in messaging:
                    self.reply(user, "delivery")
                    pass
                elif "postback" in messaging:
                    self.reply(user, "delivery")
                    pass
                elif "read" in messaging:
                    self.reply(user, "read")
                    pass
                elif "account_linking" in messaging:
                    self.reply(user, "account_linking")
                    pass
                else:
                    self.reply(user, "Error: Unknown messaging event!")
