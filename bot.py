#!/usr/bin/python3

import telepot

import datetime
import logging
import configparser

bot = ""

use_whitelist = True
whitelist = []

def bot_init():
    global use_whitelist, whitelist, bot
    # Set up Logging.
    logfilename = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-bot.log")
    logging.basicConfig(
        format="%(asctime)s:%(levelname)s: %(message)s",
        level=logging.DEBUG
    )
    logging.info("Logging to %s", logfilename)

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
        logging.error("Couldn't find use_whitelist field in config - cannot proceed.")
        exit(1)

    if(use_whitelist):
        try:
            # Convert each user id in the whiteist to an integer.
            whitelist = [int(user) for user in conf['DEFAULT']['whitelist'].split()]
        except KeyError:
            logging.error("Couldn't find whitelist field in config - cannot proceed.")
            exit(1)
        except ValueError:
            logging.error("Non-integer value found in whitelist - cannot proceed.")
            exit(1)

        if(len(whitelist) == 0):
            logging.warning("No users are whitelisted!")

    # Finally try and get the bot up and running.
    bot = telepot.Bot(token)
    try:
        # getMe gets info about the bot as a user.
        thisBot = bot.getMe()
    except telepot.exception.UnauthorizedError:
        logging.error("Couldn't authorise token with the telegram server - cannot proceed.")
        exit(1)
    except json.decoder.JSONDecodeError:
        logging.error("Issue decoding token - please check it has been copied to the config file properly - cannot proceed.")
        exit(1)
    logging.info("Bot set up successfully.")
    logging.debug("Bot username: %s", thisBot['username'])
    logging.debug("Bot ID: %s", thisBot['id'])
    logging.debug("Bot first name: %s", thisBot['first_name'])

if __name__ == '__main__':
    bot_init()
