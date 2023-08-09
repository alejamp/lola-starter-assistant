#---------------------------------------------------------------------------------------------------
# COIN GURU
# Virtual Assistant based on Lola Platform
#---------------------------------------------------------------------------------------------------
# This is a simple example of how to use 
# Lola SDK to build an AI Virtual Assistant that can answer questions related 
# to the cryptocurrency market.
# Features:
# - Get the price of a cryptocurrency in a specific currency
# - Restrict the assests to the "BTC", "ETH", "ADA", "DOT", "XRP", "LTC", checkout prompt.state.json
# - Implement limits on the number of requests per user based on credits (tokens are used as credits)
#---------------------------------------------------------------------------------------------------


import os
from time import sleep
from lolapy import LolaSDK
from lolapy import LolaContext
from lolapy import ResponseText, ResponseImage
import requests
import json
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),    # load development variables
    **os.environ,               # override loaded values with environment variables
}

# Set the initial token credits for the user
tokenStartCredits = 700

# Create a new instance of Lola SDK
# Lola SDK will listen for events and commands from the selected Assistant
lola = LolaSDK(
    lola_token=config['ASSISTANT_TOKEN'],
    prompter_url=config['PROMPTER_URL'],
    # Set to HOST env var to 0.0.0.0 on Railways or Heroku or any other cloud provider
    host=config['HOST'],  
    port=int(config['PORT']),
    # this must be a public url, you can use ngrok to expose your localhost, check README.md
    webhook_url=config['WEBHOOK_URL'],
    # Optional for Session Store into Redis instead of local memory
    # redis_url=config['REDIS_URL']
)

# Hook on every new conversation started by a new user
@lola.on_event('onNewConversation')
def handle_new_conversation(session, ctx: LolaContext, msg):
    print(f'Got new conversation message: {msg["text"]}')
    img_url = "https://firebasestorage.googleapis.com/v0/b/numichat.appspot.com/o/bitcoin-btc-banner-bitcoin-cryptocurrency-concept-banner-background-vector.jpeg?alt=media&token=d9a4e055-e61c-40ac-9584-51d7a3709901"


    # This line will send a message to the user without passing trough the AI
    # but the AI is going to response to the user after this message    
    #------------------------------------------------------------------------
    return ResponseImage(img_url, "Welcome to CoinGuru!").Send()

    # If you want to response to the user and then disable the AI response
    # only for this message, you can use the following line
    # note the DisableAI() method, this will disable the AI response
    #------------------------------------------------------------------------
    # return ResponseImage(img_url, "Welcome to the game!").DisableAI().Send()


# Hook on every message received by Lola from the user
@lola.on_event('onTextMessage')
def handle_text_message(session, ctx: LolaContext, msg):

    # This line will print the message on the console
    print(f'Got text message: {msg["text"]}')

    # Limits on credits (tokens)
    # ctx.stats is where you can get the number of tokens used by the user
    #------------------------------------------------------------------------
    used_tokens = ctx.stats.getTokens()
    messages = ctx.stats.getMessagesSent()
    cost = used_tokens * (0.06/1000)
    print(f'Tokens used: {str(used_tokens)} \nMessages sent: {str(messages)}\nEstimated Cost: ${cost:.4f}')

    # Init credits for this user
    # Session store is a local storage for each user
    #------------------------------------------------------------------------
    available_tokens = ctx.session_store.get('available_tokens')
    if available_tokens == None:
        available_tokens = ctx.session_store.set('available_tokens', tokenStartCredits)
    tokensLeft = available_tokens - used_tokens
    print(f'Tokens left: {str(tokensLeft)}')

    # If the user has no more credits (tokens) then disable the AI response
    if used_tokens > available_tokens:
        return ResponseText('You have no more credits, write: more_credits for more tokens.').DisableAI().Send()

    # This line will pass trough the message to the client (user)
    # A simple echo on each message received.
    # the the original message will process by the AI
    # and the response from AI will be sent to the user.
    #------------------------------------------------------------------------
    # ctx.messanger.send_text_message(f'Echo from python: {msg["text"]}')

    # This line will send a message to the user without passing trough the AI
    # Uncomment this line to see the difference
    #------------------------------------------------------------------------
    # return ResponseText('Welcome to the jungle!').DisableAI().Send()
    

# Hook on every image received by Lola from the user
@lola.on_event('onImage')
def handle_text_message(session, ctx: LolaContext, msg):
    attach = msg['attachments'][0]
    print(f'Got image message: {attach["url"]}')
    
    # TODO: download image?
    # TODO: process image?

    # TIMEOUT EXAMPLE
    #------------------------------------------------------------------------
    # Lola allows you to send a timeout to the user
    # The timeout will be triggered after the specified time in seconds
    # You can specify a label to identify the timeout
    # In this case, the timeout will be triggered after 5 seconds
    # check down bellow a method decorated with @lola.on_timeout()
    #------------------------------------------------------------------------
    ctx.set_timeout(5, 'send_promo')    
    

    # If you want to force a response from the AI, you can use the following line
    # ---------------------------------------------------------------------------------
    return ResponseText('You\'ve sent me an image? you made it? Awesome painting').DisableAI().Blend().Send()


@lola.on_command('get_cryptocurrency_price')
def handle_get_cryptocurrency_price(session, ctx: LolaContext, cmd):


    print(f'Got command!')
    cryptocurrency = cmd['data']['args']['cryptocurrency']
    currency = cmd['data']['args']['currency']
    print(f'User wants to know the price of {cryptocurrency} in {currency}')

    # This line will send a message to the user without passing trough the AI
    # but the AI is going to response to the user after this message    
    #------------------------------------------------------------------------
    ctx.messanger.send_text_message("Hold on... let me check the price", blend=True)
    ctx.messanger.send_typing_action()

    # Request to coinbase API to get the price of the cryptocurrency
    #------------------------------------------------------------------------
    url = f"https://api.coinbase.com/v2/prices/{cryptocurrency}-{currency}/spot"
    response = requests.get(url)
    data = json.loads(response.text)

    # When you want to response to a command:
    # you can take the json and build a natural lang response or 
    # you can send the json as a response to the command
    #------------------------------------------------------------------------
    return ResponseText(json.dumps(data)).Send()





# Hook on every timeout triggered
@lola.on_timeout()
def handle_timeout(session, ctx: LolaContext, label):
    print(f'Timeout reached for label: {label}')

    # This line will send a message to the user
    # The difference with the previous example is that this message
    # will be blended with the Chat Context (previous messages)
    # Note that every time you use ctx.messanger.send... the message is sent
    # immediately to the user.
    #------------------------------------------------------------------------
    ctx.messanger.send_text_message(
        f'Did you know that you can get a discount at CoinGuru if you use the code 1234?', 
        blend=True
    )

    # Wait for 2 seconds...
    sleep(2)

    # After 2 seconds, send another message to the user
    #------------------------------------------------------------------------
    img_url = "https://firebasestorage.googleapis.com/v0/b/numichat.appspot.com/o/Perf_Lola%2BH.way%20banner.png?alt=media&token=8a0dac42-1f76-4754-ac9c-40a93ba02125"
    ctx.messanger.send_image_message(img_url, 'Powered by Lola Platform')






# Lola SDK is ready to listen for events
# -----------------------------------------------------
# lola.listen()
# -----------------------------------------------------

# Development only
# Start listening with debug mode, 
# if you want to see the logs comming from the server
# -----------------------------------------------------
lola.listen(debug=True)
# -----------------------------------------------------
# In production don't forget to set debug to False
 
