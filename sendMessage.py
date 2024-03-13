from config import ADMIN_ID, bot
import html
from buttons import againSendMenu, GetResultMenu
from aiogram.utils.exceptions import BotBlocked, UserDeactivated
from datetime import datetime


async def sendMessage(sender_id, message, state, answer=False):
    async with state.proxy() as data:
        recip_id = data["other_id"]
        
        await handle_edit_message_reply_markup(sender_id, data["message_id"])
        res = await copy_message_and_notify(sender_id, recip_id, message, answer)

        return recip_id if res else None # при успешной отправке сообщения, возвращает ID получателя

async def handle_edit_message_reply_markup(sender_id, message_id):
    try:
        await bot.edit_message_reply_markup(sender_id, message_id)
    except:
        print(f"кнопка сообщения у пользователя {sender_id} не была удалена")

async def copy_message_and_notify(sender_id, recip_id, message, answer):
    try:
        mess_id = message.message_id
        if answer: # если это ответ
            message_about_new = "⬆️<b>На ваше сообщение ответили!</b>"
            result_message = "<b>Ваш ответ отправлен!</b>"
            button_for_recip = await againSendMenu(sender_id)
            button_for_sender = None
        else:
            message_about_new = "⬆️<b>Вы получили новое сообщение!</b>"
            result_message = "<b>Ваше сообщение отправлено!</b>"
            button_for_recip = await GetResultMenu(sender_id)
            button_for_sender = await againSendMenu(recip_id)
        
        if message.text: # тип сообщения
            await bot.send_message(recip_id, f"{html.escape(message.text)}\n\n{message_about_new}", reply_markup=button_for_recip, parse_mode="HTML")
        elif message.video or message.photo:
            caption = '' if message.caption is None else html.escape(message.caption)
            await bot.copy_message(recip_id, sender_id, mess_id, caption=f"{caption}\n\n{message_about_new}", reply_markup=button_for_recip, parse_mode="HTML")
        else:
            m = await bot.copy_message(recip_id, sender_id, mess_id)
            await bot.send_message(recip_id, message_about_new, reply_markup=button_for_recip, parse_mode="HTML", reply_to_message_id=m.message_id)

        await bot.send_message(sender_id, f"{result_message}\n\n<i>Чтобы получить личную ссылку нажми</i> /link", parse_mode="HTML", reply_markup=button_for_sender)

        try: # вдруг сломается отправка сообщения админу
            await bot.copy_message(ADMIN_ID, sender_id, mess_id)
        except:
            print("Не получилось отправить сообщение для админа")
        print(f"{sender_id} -> {recip_id}")
        return True

    except Exception as e:
        await handle_error(sender_id, e)
        return False

async def handle_error(sender_id, e):
    print(f"Дата и время ошибки {datetime.utcfromtimestamp(datetime.now().timestamp())}")
    print(e.args)
    comment = "Сообщение не было отправлено."
    if isinstance(e, BotBlocked):
        comment += " Пользователь заблокировал бота."
    elif isinstance(e, UserDeactivated):
        comment += " Пользователь был удалён."
    else:
        comment += " Неизвестная ошибка. Попробуйте обратиться в поддержку @AnQSupport"
    await bot.send_message(sender_id, f"⚙<i>{comment}</i>", parse_mode="HTML")
