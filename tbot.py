#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
###########################################################################
#   Tbot v 1.1                                                            #
#   Author: Luiz Cruz                                                     #
#   Requirements: Python 3+ and python-telegram-bot                       #  
#                                                                         #      
###########################################################################

"""

import telegram, logging, configparser, sys, time, requests, pymongo
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from importlib import reload
from logging.handlers import RotatingFileHandler




# Enable rotating logging
logging.basicConfig(
        handlers=[RotatingFileHandler('./chat.log', maxBytes=100000, backupCount=10)],
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S')
logger = logging.getLogger(__name__)



#Config bot
config = configparser.ConfigParser()
config.read_file(open('config.ini'))

# MongoDB connect
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["tbot"]
mycol = mydb["permittedUsers"]
mydoc = mycol.find().sort("profileName")

permited_users = []
for x in mydoc:
  permited_users.append(x["profileName"])




def start_callback(update, context):
    update.message.reply_text("Seja bem vindo. Respeite e será respeitadoa.")

def dayquotes_callback(update, context):
    url = config['API']['highlow_endpoint']
    response = requests.get(url)
    output = response.json()
    datetime = output['high'][0]['DATA_BRASIL']
    data_date = datetime.split('T')
    texto =  "Aí vão as principais de "+ data_date[0] + "\n\n*Altas:*"
    for alta in output['high']: 
        texto = texto + " \n"+ str(alta['StockCode'])  + "("+ ('%.2f' % alta['OSCILACAO']) +" %)"  

    texto = texto + "\n\n*Baixas*:"
    for baixa in output['low']: 
        texto = texto+ " \n"+ str(baixa['StockCode'])  + "("+ ('%.2f' % baixa['OSCILACAO'])+" %)"  

    context.bot.send_message(chat_id=update.effective_chat.id, text=texto, parse_mode=telegram.ParseMode.MARKDOWN)
    


def on_join_callback(update,context): 
    # Ignore if message comes from a channel
    msg = getattr(update, "message", None)
    if msg.chat.type == "channel":
        return
    # Get message data
    chat_id = update.message.chat.id

    
    for join_user in update.message.new_chat_members:
        
        username_id = join_user.id

        #Permited users list
        #permited_users = ['@luizcruz0','@pabambino', '@Rbacarin', '@MeuDinheiro']

        if username_id not in permited_users:
                context.bot.kickChatMember(chat_id, username_id, 30); 
                update.message.reply_text("User "+join_user.name +"("+ username_id +") not permited. Chat ID: "+ str(chat_id))
                
                


def main():
    my_bot = Updater(token=config['DEFAULT']['token'],use_context=True)

    dp = my_bot.dispatcher

    dp.add_handler(CommandHandler("regras", start_callback))
    dp.add_handler(CommandHandler("altasebaixas", dayquotes_callback))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, on_join_callback))
    
    my_bot.start_polling()

    my_bot.idle() 



if __name__ == '__main__':
    main()
