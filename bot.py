from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from telegram import ReplyKeyboardMarkup, Update
import logging
from bot_data import sheet_ul, claims_ul, receipt_del
import os
import copy
from datetime import datetime

PORT = int(os.environ.get('PORT', 5000))

TOKEN = os.getenv('BOT_TOKEN')

updater = Updater(token=TOKEN, use_context=True)

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

CHOOSE_USER, TYPING_REPLY, UPLOAD_QN, CLAIM_CHOICE, CLAIM_PRICE, CLAIM_QTY, RECEIPT_PIC, CLAIM_REMARKS, CHOOSE_MODE= range(9)

def start(update = Update, context = CallbackContext) -> int:
    update.message.reply_text("I exist to serve the hey, you got mail! main committee, use /help to learn more about what i can do")
    context.user_data['username'] = update.message.chat.username
    print(context.user_data)
    
    return CHOOSE_MODE

def helpy(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="/caps: type /caps followed by whatever u want me to yell! \n\n /claims: to make claims for your project related expenses!")

def caps(update, context):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

def greentea(update, context):
    update.message.reply_text('i like ayataka only pls')

edit_qn = [['ADD','SUBTRACT']]

upload_qn = [['Upload','Edit']]

claim_upload_qn = [['Upload','Claim']]

logs_options = [
    ['Original_ENG', 'Original_TL'],
    ['Original_CHI', 'Original_ML','Spare Umbrellas'],
]

user_selector = [['Advait','Jaslyn','Jiwon'],['Joanne','Triston','Weilin']]

claim_but = [['Claim']]

stop_but = [['Stop']]

general_claims = [
    ['Stamps', 'Transport', 'Domain'],
    ['Stickers', 'Welfare','Stationery'],
    ['Card Printing','Others'],
]

STOP_BUTTON = ReplyKeyboardMarkup(stop_but, one_time_keyboard=True)
claim_upload_markup = ReplyKeyboardMarkup(claim_upload_qn, one_time_keyboard=True)
general_claims_markup = ReplyKeyboardMarkup(general_claims, one_time_keyboard=True)
claim_but_markup = ReplyKeyboardMarkup(claim_but, one_time_keyboard=True)
upload_qn_markup = ReplyKeyboardMarkup(upload_qn, one_time_keyboard=True)
edit_qn_button = ReplyKeyboardMarkup(edit_qn, one_time_keyboard=True)
user_selector_markup = ReplyKeyboardMarkup(user_selector, one_time_keyboard=True)
logs_buttons = ReplyKeyboardMarkup(logs_options, one_time_keyboard=True)

 
def facts_to_str(facts):
# returns user data in readable way
    output_list = facts['user']
    y = f"User: {output_list[0]} \n"
    output_str = [y]

    if facts['entry'] == 'claims':
        for i in range(len(output_list)):
            try:
                m = f"{output_list[i+1][0]} : {output_list[i+1][2]} ({output_list[i+1][3]})"
            except:
                continue
            output_str.append(m)
        return "\n".join(output_str)

    for i in range(len(output_list)):
        try:
            m = f"{output_list[i+1][0]} : {output_list[i+1][1]}"
        except:
            continue
        output_str.append(m)
    
    return "\n".join(output_str)

def claims(update: Update, context: CallbackContext) -> int:
    context.user_data['entry'] = 'claims'
    context.user_data['username'] = update.message.chat.username
    username = context.user_data['username']
    
    update.message.reply_text(
            "First, let me know which committee member you are!",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ['Advait','Jaslyn','Jiwon','Joanne','Triston'],
                    ['Raynard','Weilin','Sheena','Ke Wei'],
                    ['Chelvis','Max','Devan','Sofea','Evelyn'],
                    ['Bryan','Aldrich','Hui Shan','Maira','Dylan']
                ], one_time_keyboard=True
        )
    )

    return CHOOSE_USER

def user_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['user'] = [text]

    if context.user_data['entry'] == 'claims':
        update.message.reply_text('Press "Claim" to make your claim! ', reply_markup=claim_but_markup)
            
        return CLAIM_CHOICE   

def claim_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    update.message.reply_text("What are you submitting this claim for?", reply_markup=general_claims_markup)

    return CLAIM_PRICE

def claim_price(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['item'] = text
    update.message.reply_text(
        f"What is the price (in SGD) of one unit of {text}? \n\nAlternatively, you can make a bulk claim and \
        indicate your quantity as 1 (e.g. if you chose 'Stationery' which may include multiple pens or glue-tape,\
        you may submit as one item)"
    )

    return CLAIM_QTY

def claim_qty(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['price'] = text
    update.message.reply_text(f"How many of {context.user_data['item']} at SGD {text} per pc?")

    return RECEIPT_PIC

def receipt_ul(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    context.user_data['claim_qty'] = text

    update.message.reply_text(f"Please send me your receipt(s) to claim {text} pcs of {context.user_data['item']} at SGD {context.user_data['price']} in one image!")

    return CLAIM_REMARKS

def claim_remarks(update: Update, context: CallbackContext) -> int:
    image = update.message.photo[-1].file_id
    t = str(datetime.now())[:10]
    print(image)
    context.user_data['image'] = image
    claimant = context.user_data['user'][0]
    item = context.user_data['item']
    price = context.user_data['price']
    qty = context.user_data['claim_qty']
    receipt_img = context.bot.get_file(image)
    receipt_img.download(f'receipts/{t}-{claimant}-{item}-SGD{price}x{qty}.jpg')

    update.message.reply_text(
                f"Any remarks to your claim of {context.user_data['claim_qty']} pcs of {context.user_data['item']} at SGD {context.user_data['price']}?"
                , reply_markup=ReplyKeyboardMarkup([['NIL']], one_time_keyboard=True
            )
        )

    print(context.user_data)
    print(facts_to_str(context.user_data))
    
    return TYPING_REPLY

def received_information(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    
    if context.user_data['entry'] == 'claims':
        print(text)
        context.user_data['remarks']=text

        user_data = context.user_data
        item = user_data['item']
        user_data['user'].append([item,user_data['claim_qty'],str(float(user_data['price']) * float(user_data['claim_qty'])), user_data['remarks'], user_data['image']])
        print(user_data)

        for x in ['item','claim_qty','price','remarks','image']:
            if x in user_data.keys():
                del user_data[x]

        update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"\n{facts_to_str(user_data)} \n\nDo you want to Upload or make more claims?",
            reply_markup=claim_upload_markup,
        )

        return UPLOAD_QN

def data_ul(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    print(text)
    user_data = context.user_data
    
    if context.user_data['entry'] == 'claims':
        if text == 'Upload':
            claims_ul()
            receipt_del()
            update.message.reply_text(f'Uploading the following claims to Finance Sheet (New) on Google Sheets: \n{facts_to_str(user_data)} \n\n'
            'You may start a new entry by calling /claims again! \n\n'
            'Or end this session with /stop')
            print(user_data)
            ul_data = copy.deepcopy(user_data)
  
            context.bot.sendMessage(chat_id='-432713338', text=f'@jiwoney a new claim (SGD) has appeared! \n\n{facts_to_str(user_data)}')
            
            try:
                for x in range(len(user_data['user'])):
                    image_id = user_data['user'][x+1][4]
                    context.bot.sendPhoto(chat_id='-432713338', photo=f"{image_id}")
                    user_data['user'][x+1].remove(image_id)
            except:
                pass
            
            print(user_data)
            ul_data = copy.deepcopy(user_data)
            sheet_ul(ul_data)
            print(ul_data)
            print(user_data)
            
            user_data.clear()
            
            return CHOOSE_MODE

        if text == 'Claim':
            update.message.reply_text("What are you submitting this claim for?", reply_markup=general_claims_markup)
            return CLAIM_PRICE
        


def stop(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Thanks! Just say the magic word if you need my help again!")
    return ConversationHandler.END

def main():

    greentea_handler = CommandHandler('greentea', greentea)

    start_handler = CommandHandler('pokka', start, Filters.user(user_id=[
        52460092,113264290,783785579,411680827,222872163,828268987,
        303655147,563051070,355666223,352265020,189083051,244712716,
        686899058,762923285,1057892382,257797566,321001655,221420498,845410147
            ]
        )
    )   

    help_handler = CommandHandler('help', helpy)
   
    caps_handler = CommandHandler('caps', caps)

    conv_handler = ConversationHandler(
        entry_points=[start_handler],
        states={
            CHOOSE_MODE: [
                CommandHandler('claims', claims),caps_handler, help_handler, greentea_handler
            ],
            CHOOSE_USER: [
                MessageHandler(Filters.regex('^(Advait|Jaslyn|Jiwon|Joanne|Triston|Weilin|Shophouse|Sheena|Ke Wei|Raynard|Max|Devan|Sofea|Hui Shan|Aldrich|Bryan|Dylan|Maira|Chelvis|Evelyn)$'), user_choice)
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Stop$')),
                    received_information,
                )
            ],
            UPLOAD_QN: [
                MessageHandler(Filters.text, data_ul)
            ],
            CLAIM_CHOICE: [
                MessageHandler(Filters.regex('^Claim$') & ~(Filters.command | Filters.regex('^Stop$')), claim_choice)
            ],
            CLAIM_PRICE: [
                MessageHandler(Filters.regex('^(Stamps|Transport|Domain|Stickers|Welfare|Stationery|Card Printing|Others)$'), claim_price)
            ],
            CLAIM_QTY: [
                MessageHandler(Filters.regex(r"^([-+]?\d*\.\d+|\d+)$") & ~(Filters.command | Filters.regex('^Stop$')), claim_qty)
            ],
            RECEIPT_PIC: [
                MessageHandler(Filters.regex(r"^([-+]?\d*\.\d+|\d+)$") & ~(Filters.command | Filters.regex('^Stop$')), receipt_ul)
            ],
            CLAIM_REMARKS: [
                MessageHandler(Filters.photo & ~(Filters.command | Filters.regex('^Done$')), claim_remarks)
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^(Stop)$'), stop),CommandHandler('stop', stop)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    # updater.bot.setWebhook('https://ancient-hamlet-17787.herokuapp.com/' + TOKEN)
    updater.bot.setWebhook('https://ayatakabot.onrender.com/' + TOKEN)

if __name__ == '__main__':
    main()