#!/usr/bin/python3

import telepot
import json
import datetime
import logging
import configparser
import time

bot = ""
token = ""
use_whitelist = True
whitelist = []
botusername = ""

def handle_message(msg):
    global botusername

    # Get the first word in the message - the command.
    command = msg['text'].split(' ', 1)[0]

    # Detect group chats and handle addressing of commands.
    if msg['chat']['type'] == 'group':
        logging.debug("Message is group type.")
        try:
            if command.split('@', 1)[1] == botusername:
                logging.debug("Message received for this bot.")
                # If it was a group addressed command, cut the address out.
                command = command.split('@', 1)[0]
            else:
                logging.debug("Message destined for another bot, drop it.")
                return
        except IndexError:
            logging.info("This message had no specified receiver.")
    logging.info("Received command %s", command)

    chat_id = msg['chat']['id']

    if(command == '/start'):
        bot.sendMessage(chat_id,
            "Hi there! I see you're new. Type /help to get started!"
        )

    elif(command == '/help'):
        bot.sendMessage(chat_id,
            'Warning: This bot is very much in development.\n' +
            '    /help - Print this help.\n' +
            '    /latex <latex body> - render latex as a standalone\n'
            )

#    elif(command == '/latex'):
#        render_latex(msg['text'])

    elif(command in ('/beep', 'Beep')):
        bot.sendMessage(chat_id, 'Boop!')

    elif(command in ('/boop', 'Boop')):
        bot.sendMessage(chat_id, 'Beep!')

    else:
        bot.sendMessage(chat_id,
            'Sorry, I don\'t know how to handle the command: ' +
            command +
            '. Try /help' )

def on_chat_message(msg):
    global bot, use_whitelist, whitelist
    # Get the important info about the message.
    content_type, chat_type, chat_id = telepot.glance(msg)

    logging.info(msg)

    # We're only handling text messages.
    if(content_type == 'text'):
        if use_whitelist:
            if int(msg['from']['id']) in whitelist:
                logging.info("Approved user command received.")
                handle_message(msg)
            else:
                # Send the not-whitelisted command.
                if msg['text'] == '/start':
                    bot.sendMessage(chat_id,
                        "This bot requires you to be added to the whitelist " +
                        "to use. Please speak to the owner to proceed."
                    )
                logging.warning(
                    "New user or group %s activated the bot.",
                    chat_id
                )
        else:
            handle_message(msg)

def logging_init():
    # Set up Logging.
    logfilename = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-bot.log")
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s: %(message)s",
        level=logging.INFO
    )
    logging.info("Logging to %s", logfilename)

def parse_config():
    global token, use_whitelist, whitelist
    # Open the config file and parse it.
    conf = configparser.ConfigParser()
    configstatus = conf.read("botconf.conf")

    if len(configstatus) == 0:
        logging.error("Couldn't find bootconf.conf - cannot proceed.")
        exit(1)

    if configstatus[0] == "botconf.conf":
        logging.info("bootconf.conf read.")
    else:
        logging.error("Couldn't find bootconf.conf - cannot proceed.")
        exit(1)

    try:
        token = conf['DEFAULT']['token']
        logging.info("Token read ok")
    except KeyError:
        logging.error("Couldn't find token field in config - cannot proceed.")
        exit(1)

    try:
        if(conf['DEFAULT']['use_whitelist']).lower() in ('false', 'no', '0'):
            logging.warning("Whitelist is not being used.")
            use_whitelist = False
        else:
            use_whitelist = True
            logging.warning("Using whitelist.")
    except KeyError:
        logging.error(
            "Couldn't find use_whitelist field in config - cannot proceed."
        )
        exit(1)

    if(use_whitelist):
        try:
            # Convert each user id in the whiteist to an integer.
            whitelist = [
                int(user) for user in conf['DEFAULT']['whitelist'].split()
            ]
        except KeyError:
            logging.error(
                "Couldn't find whitelist field in config - cannot proceed."
            )
            exit(1)
        except ValueError:
            logging.error(
                "Non-integer value found in whitelist - cannot proceed."
            )
            exit(1)

        if(len(whitelist) == 0):
            logging.warning("No users are whitelisted!")

def bot_init():
    global token, bot, botusername
    # Get the bot up and running.
    bot = telepot.Bot(token)
    try:
        # getMe gets info about the bot as a user.
        thisBot = bot.getMe()
    except telepot.exception.UnauthorizedError:
        logging.error(
            "Couldn't authorise token with the telegram server " +
            "- cannot proceed."
        )
        exit(1)
    except json.decoder.JSONDecodeError:
        logging.error(
            "Issue decoding token - " +
            "please check it has been copied to the config file properly - " +
            "cannot proceed."
        )
        exit(1)
    logging.info("Bot set up successfully.")
    logging.debug("Bot username: %s", thisBot['username'])
    logging.debug("Bot ID: %s", thisBot['id'])
    logging.debug("Bot first name: %s", thisBot['first_name'])

    botusername = thisBot['username']

    # Set up the bot interrupt.
    bot.message_loop({'chat': on_chat_message})

if __name__ == '__main__':
    logging_init()
    parse_config()
    bot_init()
    # Spin forever serving the interrupt.
    while True:
        time.sleep(10)
