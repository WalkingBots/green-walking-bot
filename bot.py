# создаем телеграм бота
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.utils.request import Request

import config
import dump

req = Request(proxy_url=config.proxy)
bot = Bot(config.token, request=req)
upd = Updater(bot=bot, use_context=True)
dp = upd.dispatcher

# логирование
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def getLocation(chat_id):
    location_keyboard = KeyboardButton(text="Send location", request_location=True)
    custom_keyboard = [[ location_keyboard ]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

# приветственное сообщение
def hello(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Привет! Я кофейный бот, который поможет тебе найти лучший кофе поблизости. "
                                  "Введите команду /coffee чтобы оставить отзыв")

ASK_NAME, ASK_TYPE, ASK_RATING, ASK_COMMENT, ASK_LOCATION = 1,2,3,4,5
data = dict()
empty_review = ["","","",""]
# оставить отзыв
def coffee(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id,text="Создаю новый отзыв. Пожалуйста, введите название кофейни.")
    return ASK_NAME

#Обработка информации
def proceedName(update,context):
    data[update.message.from_user.username] = empty_review
    data[update.message.from_user.username][ASK_NAME-1]=(update.message.text+'\n')
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Пожалуйста, введите вид кофе.")
    return ASK_TYPE
def proceedType(update,context):
    data[update.message.from_user.username] = empty_review
    data[update.message.from_user.username][ASK_TYPE-1]=(update.message.text+'\n')
    context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, введите оценку от 1 до 10.")
    return ASK_RATING

def proceedRating(update,context):
    data[update.message.from_user.username] = empty_review
    data[update.message.from_user.username][ASK_RATING-1]=(update.message.text+"\n")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, введите комментарий (- если нет комментариев).")
    return ASK_COMMENT

def proceedComment(update,context):
    data[update.message.from_user.username] = empty_review
    data[update.message.from_user.username][ASK_COMMENT-1]=(update.message.text+"\n")
    context.bot.send_message(chat_id=update.effective_chat.id,text="Пожалуйста, скиньте локацию кофейни.")
    return ASK_LOCATION

def proceedLocation(update,context):
    location=update.message.location
    textdata=""
    for i in range(1,ASK_COMMENT):
        textdata+=data[update.message.from_user.username][i-1]
    dump.data_with_location("text", textdata+str(location.longitude)+','+str(location.latitude),
                            update.message.from_user.username,
                            update.message.location)

    context.bot.send_message(chat_id=update.effective_chat.id,text="Отзыв сохранен. Спасибо!")

    return ConversationHandler.END

def cancel(update,context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Отмена отзыва.")

#создаем обработчики
ch=ConversationHandler(
    entry_points=[CommandHandler('coffee', coffee)],

    states={
        ASK_NAME: [MessageHandler(Filters.text, proceedName)],

        ASK_TYPE: [MessageHandler(Filters.text, proceedType)],

        ASK_RATING: [MessageHandler(Filters.text, proceedRating)],

        ASK_COMMENT: [MessageHandler(Filters.text, proceedComment)],

        ASK_LOCATION: [MessageHandler(Filters.location, proceedLocation)]
    },

    fallbacks=[CommandHandler('cancel', cancel)]
)



# добавляем всех обработчиков в диспетчер
dp.add_handler(CommandHandler('start', hello))
dp.add_handler(ch)

def main():
    # запускаем бота
    upd.start_polling()
    upd.idle()

if __name__ == '__main__':
    main()
