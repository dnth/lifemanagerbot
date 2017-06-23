#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
from emoji import emojize
import MySQLdb as mdb
import datetime

from db_helper import check_for_existing_user, get_user_engname, get_user_info, nc_entry


db_charset='utf8'
db_host='127.0.0.1'
db_user="root"
db_passwd="root"
db_in_use="national_db"

# Global variables
secret_key = 'cumulonimbus'


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, NC_DETAILS, NC_DET_TYPING_REPLY = range(4)



reply_keyboard_dept = [['CL','JS', 'BF'], ['YM', 'CM', 'SSM'], ['YF', 'CF','SSF'], ['MW', 'OV', 'GS']]
markup_dept = ReplyKeyboardMarkup(reply_keyboard_dept)

reply_keyboard_gender = [['Male', 'Female']]
markup_gender = ReplyKeyboardMarkup(reply_keyboard_gender)



reply_kb_church = [
    ['LWC', 'LLC', 'BC'],
    ['NLC', 'LCC', 'LFC'],
    ['LHC']
]
markup_list_church = ReplyKeyboardMarkup(reply_kb_church)

reply_kb_ncdept = [['Campus', 'Youth', 'Others']]
markup_kb_ncdept = ReplyKeyboardMarkup(reply_kb_ncdept)

reply_kb_perstype = [['Circle', 'Square'],['Triangle', 'S']]
markup_kb_perstype = ReplyKeyboardMarkup(reply_kb_perstype)

reply_kb_ncclass = [['A Class', 'B Class', 'C Class']]
markup_kb_ncclass = ReplyKeyboardMarkup(reply_kb_ncclass)

reply_keyboard = [['Start Conversation', 'End Conversation'],
                  ['Real Name', 'Nick Name'],
                  ['Gender', 'Department'],
                  ['Email','Contact Number'],
                  ['Secret Key','Done'],
                  ]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


# main menu keyboard here
main_menu_kb = [['Start Conversation','End Conversation'],
                ['National Newcomer List','View Statistics'],
                ['Key in NC Details', 'Update NC Details'],
                ['Key NC Attendance', 'Delete NC']
                ]
markup_main_menu_kb = ReplyKeyboardMarkup(main_menu_kb)



nc_det_kb = [
            ['Name', 'Evangelism Date'],
            ['Gender', 'Age'],
            ['Department','Church'],
            ['Company/University', 'Job/Course'],
            ['Type', 'Class'],
            ['Done', '/cancel']
            ]
markup_nc_det_kb = ReplyKeyboardMarkup(nc_det_kb)


def start(bot, update):
    print "{} is prompting the bot".format(update.message.chat_id)

    try:
        user_exists = check_for_existing_user(telegram_id=update.message.chat_id)

    except Exception as e:
        print e

    else:
        if user_exists:
            # print "User exists!"
            user_data_dict = get_user_info(telegram_id=update.message.chat_id)
            print "[{}] {} starts talking".format(datetime.datetime.now(), get_user_engname(update.message.chat_id).encode('utf-8'))

            if user_data_dict['isAdmin'] == 'No':
                update.message.reply_sticker('BQADAgADWgADVSx4CwEjojGmsKGbAg')
                update.message.reply_text(
                    "Hi *{}*, we meet again, what can I do for you today?".format(user_data_dict['nick_name'].encode('utf-8')),
                    reply_markup=markup_main_menu_kb,
                    parse_mode=telegram.ParseMode.MARKDOWN)

                return CHOOSING
            else:
                update.message.reply_sticker('BQADAgADWgADVSx4CwEjojGmsKGbAg')
                update.message.reply_text("Hey whatsup boss *{}*, we meet again! What can I do for you today?".format(
                    user_data_dict['nick_name'].encode('utf-8')),
                                          reply_markup=markup_main_menu_kb,
                                          parse_mode=telegram.ParseMode.MARKDOWN)
                return CHOOSING


        else:
            update.message.reply_sticker('BQADAgADZgADVSx4C4I00LsibnWGAg')
            update.message.reply_text(
                "Hi! I am the National Manager Bot! I will need some information before we proceed. "
                "Why don't you tell me something about yourself? Choose from the items below..",
                reply_markup=markup)

            return CHOOSING


def updatekey(bot, update, args):
    updated_key = " ".join(args)
    global secret_key
    secret_key = updated_key
    update.message.reply_text("Key updated to {}".format(secret_key))



def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    # if we dont have all the required keys, re register again

    # check if Name exists
    if 'Real Name' not in user_data:
        update.message.reply_text("You didn't seem to tell me your name..", reply_markup=markup)
        return CHOOSING

    # check if Department exists
    if 'Department' not in user_data:
        update.message.reply_text("You didn't seem to tell me which department you belong to..", reply_markup=markup)
        return CHOOSING

    # check if Gender exists
    if 'Gender' not in user_data:
        update.message.reply_text("You didn't seem to tell me your gender..", reply_markup=markup)
        return CHOOSING

    # check if Email exists
    if 'Email' not in user_data:
        update.message.reply_text("You didn't seem to tell me your Email..", reply_markup=markup)
        return CHOOSING

    # check if Contact Number exists
    if 'Contact Number' not in user_data:
        update.message.reply_text("You didn't seem to tell me your contact number..", reply_markup=markup)
        return CHOOSING

    if 'Secret Key' not in user_data:
        update.message.reply_text("You didn't seem to enter the secret key..", reply_markup=markup)
        return CHOOSING

    elif 'Secret Key' in user_data:
        if user_data['Secret Key'] == secret_key:
            update.message.reply_text("I learned these facts about you:"
                                  "%s"% facts_to_str(user_data))

            update.message.reply_text("For your safety (and mine too), it is highly recommended that you clear this chat history as it "
                                      "contains your personal information!")




            try:
                db = mdb.connect(charset=db_charset, host=db_host, user=db_user, passwd=db_passwd, db=db_in_use)
                cur = db.cursor()

                #check if telegram id exists
                user_telegram_id = update.message.chat_id
                cur.execute("SELECT EXISTS(SELECT * FROM members_list WHERE telegram_id='{}' )".format(user_telegram_id))
                user_exist = cur.fetchall()[0]


                if user_exist == ('0L'):
                    update.message.reply_text("You seem to exist in my db")
                else:
                    # if no proceed to enter data

                    update.message.reply_text("Entering your information. Stay with me...")
                    update.message.reply_text("...")
                    update.message.reply_text("...")
                    update.message.reply_text("...")

                    cur.execute("INSERT INTO members_list (nick_name, real_name, dept, gender, contact_num, telegram_id, email) "
                                "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                                .format(user_data['Nick Name'], user_data['Real Name'], user_data['Department'], user_data['Gender'],
                                        user_data['Contact Number'], user_telegram_id, user_data['Email']))

                    update.message.reply_text("Registration complete!")
                    update.message.reply_text("Welcome *{}*, from now on, I am at your command. I will assist you wherever possible within my capability as a robot. "
                                   "Let's make HISTORY!".format(user_data['Nick Name']),
                                              reply_markup=markup_main_menu_kb,
                                              parse_mode=telegram.ParseMode.MARKDOWN)

                    update.message.reply_sticker("BQADAgADRgADVSx4C5-O4uhXcrjOAg")


            except Exception as e:
                print e
                print "Error in connecting to database. I cannot seem to record your response. Please try again later"
                update.message.reply_text("Error in connecting to database. I cannot seem to record your response. Please try again later")
            finally:
                db.commit()
                db.close()


        #if secret key is not correct, do not key in.. prompt user to try again
        else:
            update.message.reply_text("You seem to have the wrong Secret Key. "
                                      "Did you get the right key from those humans from LHC Admins? "
                                      "Please get the secret key and key in here..")
            return CHOOSING

    user_data.clear()
    return ConversationHandler.END


def done_nc_det(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    # verify all entry here
    if 'Name' not in user_data:
        update.message.reply_text("You did not tell me the name of your NC..")
        return NC_DETAILS

    if 'Gender' not in user_data:
        update.message.reply_text("You did not tell me the gender of your NC..")
        return NC_DETAILS

    if 'Department' not in user_data:
        update.message.reply_text("You did not tell me the department of your NC..")
        return NC_DETAILS

    if 'Church' not in user_data:
        update.message.reply_text("You did not tell me the church NC belongs to..")
        return NC_DETAILS

    if 'Evangelism Date' not in user_data:
        update.message.reply_text("You did not tell me the date when your NC is evangelized..")
        return NC_DETAILS


    else:

        # inspect date format
        try:
            datetime.datetime.strptime(user_data['Evangelism Date'], '%Y-%m-%d')
            # done doesnt work
        except:
            update.message.reply_text("Wrong date format, please re-enter the date in the following format yyyy-mm-dd\n\n"
                                  "For example 1978-06-01" )
            return NC_DETAILS

        # should we have incomplete keys
        if 'Age' not in user_data:
            user_data['Age'] = None
        if 'Type' not in user_data:
            user_data['Type'] = None
        if 'Company/University' not in user_data:
            user_data['Company/University'] = None
        if 'Job/Course' not in user_data:
            user_data['Job/Course'] = None

        # enter into db here
        nc_entry(nc_name=user_data['Name'], nc_dept=user_data['Department'], nc_church=user_data['Church'],
                 nc_gend=user_data['Gender'], nc_age=user_data['Age'], nc_ev_date=user_data['Evangelism Date'],
                 nc_niche_course=user_data['Job/Course'], nc_comp_uni=user_data['Company/University'],
                 nc_perso_type=user_data['Type'])


        update.message.reply_sticker("CAADAgADQgADVSx4C1--9Yr_WY3AAg")
        update.message.reply_text("I have recorded your NC details as below:\n"
                                  "{}\n"
                                  "Thanks! Come back when you have more NCs for me~".format(facts_to_str(user_data)),
                                  reply_markup=markup_main_menu_kb)
        user_data.clear()
        return ConversationHandler.END




def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation." % user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=markup_main_menu_kb)

    return ConversationHandler.END

def end_conv(bot, update, user_data):
    update.message.reply_sticker("BQADAgADSgADVSx4C_alFsjOJxXLAg")
    update.message.reply_text("Thank you for talking to me! Type /start or press on *Start Conversation* when you wanna talk again.. ",
                              parse_mode=telegram.ParseMode.MARKDOWN)

    try:
        print "[{}] {} left conversation".format(datetime.datetime.now(), get_user_engname(update.message.chat_id).encode('utf-8'))

    except Exception as e:
        print "[{}] {} Anonymous user left conversation".format(datetime.datetime.now(), update.message.chat_id)

    finally:
        user_data.clear()
        return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def regular_choice(bot, update, user_data):
    text = update.message.text

    user_data['choice'] = text

    update.message.reply_text('Your %s? Yes, I would love to hear about that!' % text.lower())

    if user_data['choice'] == "Department":
        # markup_dept =
        update.message.reply_text(emojize("Please select from the list of departments on the keyboard below. \n"
                                  "In case you're lost with the abbreviations, here's a list to help you out.\n"
          ":star2: *CL* - Church Leader\n"
          ":couple: *JS* - JS\n"
          ":family: *BF* - Blessed Family\n"
          ":panda_face: *YM* - Youth Male\n"
          ":princess: *YF* - Youth Female\n"
          ":boy: *CM* - Campus Male\n"
          ":girl: *CF* - Campus Female\n"
          ":hamster: *SSM* - SS Male\n"
          ":penguin: *SSF* - SS Female\n"
          ":snowflake: *MW* - Milky Way\n"
          ":cloud: *OV* - Overseas Member\n"
          ":speech_balloon: *GS* - Guest", use_aliases=True),reply_markup=markup_dept, parse_mode=telegram.ParseMode.MARKDOWN)

    if user_data['choice'] == 'Secret Key':
        update.message.reply_text("Enter the Secret Key given to you by the humans from LHC Admin..")


    if user_data['choice'] == 'Gender':
        update.message.reply_text("Well, if you don't mind me asking, are you a male or female?", reply_markup=markup_gender)


    return TYPING_REPLY

def nc_details_keyin(bot, update, user_data):
    text = update.message.text

    user_data['choice'] = text

    update.message.reply_text('Your NC %s? Yes, I would love to hear about that!' % text.lower())

    if user_data['choice'] == 'Gender':
        update.message.reply_text("Well, if you don't mind me asking, is your NC a male or female?", reply_markup=markup_gender)

    if user_data['choice'] == 'Church':
        update.message.reply_text("Erm.. your NC currently attending which church ar?", reply_markup=markup_list_church)

    if user_data['choice'] == 'Evangelism Date':
        update.message.reply_text("When did you evangelized this NC? Please enter the date in the following format yyyy-mm-dd\n\n"
                                  "For example 1978-06-01")

    if user_data['choice'] == 'Type':
        update.message.reply_text("Your NC belongs to which type of personality?", reply_markup=markup_kb_perstype)

    if user_data['choice'] == 'Department':
        update.message.reply_text("Which church department is your NC put under?", reply_markup=markup_kb_ncdept)

    if user_data['choice'] == 'Class':
        update.message.reply_text("Please rate your NC. Which class does your NC belongs to?", reply_markup=markup_kb_ncclass)


    return NC_DET_TYPING_REPLY


def received_information(bot, update, user_data):
    text = update.message.text

    category = user_data['choice']
    user_data[category] = text.encode('utf-8')
    del user_data['choice']



    update.message.reply_text("Neat! Just so you know, this is what you already told me: {}".format(facts_to_str(user_data)),
                              reply_markup=markup)
    update.message.reply_text("You can tell me more, or change your opinion on something. \n"
                              "Press *Done* if you're sure of the information you gave me.")


    return CHOOSING

def received_nc_det(bot, update, user_data):
    text = update.message.text

    category = user_data['choice']
    user_data[category] = text.encode('utf-8')
    del user_data['choice']


    update.message.reply_text(
        "Neat! Just so you know, this is what you already told me about your NC: {}".format(facts_to_str(user_data)),
        reply_markup=markup_nc_det_kb)
    update.message.reply_text("You can tell me more, or change your opinion on something. \n"
                              "Press *Done* if you're sure of the information you gave me.\n"
                              "If you wish to quit, type /cancel")

    return NC_DETAILS



def facts_to_str(user_data):
    facts = list()
    for key, value in user_data.items():
        facts.append('<{}> : {}'.format(key, value))
        # facts.append('<%s> : %s' % (key, value))

    return "\n".join(facts).join(['\n', '\n'])


def key_in(bot, update):
    update.message.reply_text("You *MUST* key in the following fields:\n"
                              "*Name*\n*Gender*\n*Evangelism Date*\n*Department*\n*Church*. \n"
                              "As for the others, you will be able to update them later..\n\n"
                              "Please select from the items below:",
                              reply_markup=markup_nc_det_kb,
                              parse_mode=telegram.ParseMode.MARKDOWN)
    return NC_DETAILS





def main(TOKEN):
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), RegexHandler('^(Start Conversation)$', callback=start)],

        states={

            CHOOSING: [RegexHandler('^(Real Name|Nick Name|Department|Contact Number|Email|Secret Key|Gender)$',
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Done$', done, pass_user_data=True),

                       RegexHandler('^(Key in NC Details)$', callback=key_in),

                       ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],

            NC_DETAILS:[RegexHandler('^(Name|Gender|Class|Church|Department|Job/Course|Company/University|Type|Evangelism Date|Age)$', nc_details_keyin, pass_user_data=True),
                        RegexHandler('^Done$', done_nc_det, pass_user_data=True)],
            NC_DET_TYPING_REPLY: [MessageHandler(Filters.text, received_nc_det, pass_user_data=True)],

        },

        fallbacks=[CommandHandler('cancel', cancel), RegexHandler('^End Conversation$', end_conv, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    upkey_handler = CommandHandler('updatekey', callback=updatekey, pass_args=True)
    dp.add_handler(upkey_handler)

    # keyin_nc_det_handler = RegexHandler('^(Key in NC Details)$', callback=key_in)
    # dp.add_handler(keyin_nc_det_handler)


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    file = open('../tokens/pvlifemanagerbot_token.txt')
    token = file.readlines()
    token = token[0].strip('\n')
    print "Life Manager Bot is listening.."
    main(token)