# Chatbot

A Chatbot for Facebook Page.

## Before running the code

1. Create a Facebook Page.
2. Get the access token and verify token from the Facebook page.
3. On the Webhooks panel, subscribe to the `messages`.
4. On the Messenger panel, under the Settings, fill in the `Callback
   URL` and `Verify token`.  For example:

   - Callback URL: https://weesan.serveo.net/webhook
   - Verify token: TOKEN

## To run the code

### On one terminal
```
$ ssh -R weesan:80:localhost:5000 serveo.net
```

### On another terminal
```
$ export ACCESS_TOKEN="..."
$ export VERIFY_TOKEN="TOKEN"
$ ./chatbot
```

## To try the chatbot

1. Go the Facebook page or use the Facebook Messenger.
2. Search for the Facebook page.
3. Start chatting with the chatbot.

For example:
```
Me:  Hi
Bot: Greetings!  Welcome to ELSA!
Bot: To search for a product, please type its name!
Me:  red nike tennis shoes

Bot: What category?
Me:  Shoes

Bot: Which store?
Me:  Nike

Bot: <show a list of matched shoes from Nike store>
```
