#!/usr/bin/env python3

# From: https://github.com/masnun/fb-bot/blob/master/server.py

from flask import Flask, request
from fbchatbot import FBChatBot, Nlp
import requests
import urllib.parse
import json
import os

app = Flask(__name__)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("TOKEN")

APP_NAME = "ELSA"

class MyChatBot(FBChatBot):
    def __init__(self, access_token, verify_token):
        super().__init__(access_token, verify_token)

    def process_text(self, user, text, nlp = Nlp.NONE):
        app.logger.debug("Received text: %s, nlp: %x" % (text, nlp))

        if text == "lol":
            self.reply("")
            return

        if nlp & Nlp.BYE:
            self.reply(user, "Have a nice day.  Look forward to hearing from again!")
        elif user.new_user or \
           nlp & Nlp.GREETINGS or \
           text.lower() in [ "hi", "hello", "hola", "help", "start over" ]:
            # Start from the query.
            user.response = None
            user.query = None
            user.category = None
            user.store = None
            user.product = None
            user.receipt = None

            if user.new_user:
                self.reply(user, "Greetings!  Welcome to %s!" % APP_NAME)
            else:
                self.reply(user, "Welcome back to %s!" % APP_NAME)
            self.reply(user, "To search for a product, please type its name!")
        else:
            #resp = super().process_text(user, text)

            if user.query == None:
                app.logger.debug("query state")
                user.query = text

                user.response = self.query(user)
                if user.response == None:
                    app.logger.error("Failed to query: %s", text)
                    self.reply(user,
                               "Couldn't find any.  Please try other items.")
                    return

                categories = user.response["data"]["searchProduct"]["meta"]["categories"]
                self.quick_reply(user, "What category?", categories)
            elif user.category == None:
                app.logger.debug("category state")
                user.category = text

                user.response = self.query(user)
                if user.response == None:
                    app.logger.error("Failed to query: %s", text)
                    self.reply(user,
                               "Couldn't find any.  Please try other items.")
                    return

                stores = []
                for store in user.response["data"]["searchProduct"]["meta"]["stores"]:
                    stores.append(store["name"])

                # Truncate the array to 10, a limitation of quick reply.
                del(stores[10:])
                self.quick_reply(user, "Which store?", stores)

            elif user.store == None:
                app.logger.debug("store state")
                user.store = text

                user.response = self.query(user)
                if user.response == None:
                    app.logger.error("Failed to query: %s", text)
                    self.reply(user,
                               "Couldn't find any.  Please try other items.")
                    return

                products = []
                for product in user.response["data"]["searchProduct"]["products"]:
                    if product["availability"]:
                        products.append({
                            "title": product["title"],
                            "subtitle": product["currency"] + str(product["priceCurrent"] / 100),
                            "item_url": product["imageUrlPrimary"],
                            "image_url": product["imageUrlPrimary"],
                            "buttons": [{
                                "type": "web_url",
                                "url": "https://www.joinhoney.com/shop/" + product["store"]["label"] + "/p/" + product["productId"],
                                "title": "Buy"
                            }]
                        })

                # Truncate the array to 10, a limitation of quick reply.
                del(products[10:])
                app.logger.debug("product size %d" % len(products))
                self.generic_reply(user, "Choose your item, please!", products)

            elif user.product == None:
                app.logger.debug("product state")
                user.product = text

            elif user.receipt == None:
                app.logger.debug("receipt state")
                user.receipt = True

    def query(self, user):
        variables = {
            "query": urllib.parse.quote_plus(user.query),
            "meta": {
                "limit": 10,
                "offset": 0
            }
        }

        if user.category:
            variables["meta"]["categories"] = urllib.parse.quote_plus(user.category)

        # XXX: Need to find out the store API.
        #if user.store:
        #    variables["meta"]["stores"] = urllib.parse.quote_plus(user.store)

        query = "https://d.joinhoney.com/v3?operationName=searchProduct&variables=%s" % str(variables).replace("'", "\"").replace(" ", "")
        app.logger.debug("Query: %s" % query)

        r = requests.get(query)
        if r.status_code != requests.codes.ok:
            return None
        else:
            return r.json()


chatbot = MyChatBot(ACCESS_TOKEN, VERIFY_TOKEN)

# Flask's routing

@app.route('/webhook', methods=['GET'])
def handle_verification():
    return chatbot.verify(request.args)

@app.route('/webhook', methods=['POST'])
def handle_incoming_messages():
    app.logger.debug("Received: %s" % json.dumps(request.json, indent=2))
    chatbot.process(request.json)
    return "OK"

# Main function

if __name__ == '__main__':
    app.run(debug=True, port = 5000)
