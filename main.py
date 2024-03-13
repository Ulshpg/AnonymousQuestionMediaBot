from datetime import datetime, timedelta
import math
from sendMessage import sendMessage
from buttons import *
from config import *
from states import *
import html
from database import insert_data, get_names, get_all_vips, add_vip, check_user_exists, delete_vip_by_id, get_vip_data_by_id, get_stats, increment_field_by_id
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


dp = Dispatcher(bot, storage=MemoryStorage())
yoomoney_client = Client(YOOMONEY_TOKEN)


async def date_in_a_30_days():
    current_datetime = datetime.now()
    date_in_one_week = current_datetime + timedelta(days=30)
    timestamp_in_one_week = int(date_in_one_week.timestamp())
    print(f"Дата окончания: {datetime.utcfromtimestamp(timestamp_in_one_week)}")
    return timestamp_in_one_week


class VIP:
    users = list()


    async def update_vip_users():
        VIP.users = await get_all_vips()

    async def add_vip_user(id):
        VIP.users = await add_vip(id, await date_in_a_30_days())

    async def del_vip_user(id):
        VIP.users = await delete_vip_by_id(id)


async def if_less(text):
    if text is None:
        return True
    return True if len(text) < LIMIT_SYMBOLS else False

async def check_end(user_id):
    sec_now = datetime.now()
    sec_now = int(sec_now.timestamp())
    sec_end = await get_vip_data_by_id(user_id)
    if sec_end:
        if sec_now > sec_end:
            return True
        return False
    else:
        text = f"Не удается получить дату пользователя {user_id}"
        await bot.send_message(ADMIN_ID, text)
        print(f"\n{text}\n")

async def check_payment(label):
    history = yoomoney_client.operation_history()
    print(f"\nLabel: {label}")
    for operation in history.operations:
        if operation.label == label and operation.status == "success":
            print(f"ПЛАТЁЖ {operation.amount} УСПЕШНО ПРОШЁЛ")
            return True
            break
    else:
        print("ПЛАТЁЖ НЕ ОБНАРУЖЕН")
        return False

async def get_username(tmp_username):
    if "none" == str(tmp_username).lower():
        username = "Отсутствует"
    else:
        username = f"@{tmp_username}"
    return username

async def on_startup(_):
    print("Бот онлайн")
    await VIP.update_vip_users()

@dp.message_handler(commands="start", state='*')
async def commands_start(message, state=FSMContext):
    user_id = message.from_user.id
    name_user = message.from_user.first_name
    username = await get_username(message.from_user.username)
    await insert_data(user_id, name_user, username)
    if len(message.text.split()) > 1: # реферальная система
        unique_code = message.text.split()[1]
        if unique_code.isdigit():
            unique_code = int(unique_code)
            if unique_code == user_id:
                await message.answer("⚙ <i>Вы не можете написать сами себе!</i>", reply_markup=removeButton, parse_mode="HTML")
                await state.finish()
            else:
                if await check_user_exists(unique_code):
                    await increment_field_by_id(unique_code, "TRANSITIONS")
                    message = await message.answer("💬Сейчас ты можешь отправить <b>анонимное сообщение</b> тому человеку, \
                                        который опубликовал эту ссылку.\n\n✍🏻 Отправить можно:\n- 🌅<b>фото</b>\n- 📹<b>видео</b>\n- 💬<b>текст</b>\n- 🔊<b>голосовые</b>\n- 📷<b>видеосообщения</b>\n- 📑<b>стикеры</b>", reply_markup=cancelMenu, parse_mode="HTML")
                    await User.write.set()
                    async with state.proxy() as data:
                        data['other_id'] = unique_code
                        data['message_id'] = message.message_id
                else:
                    await message.answer("<i>Такого пользователя не найдено</i>\n\nОбратитесь в поддержку /support", parse_mode='HTML')
                    print(f"id {unique_code} не было найдено в базе")
        else:
            await message.answer("<i>Ошибка параметра.\nПараметр start не может содержать в себе символы, кроме цифр</i>\n\nОбратитесь в поддержку /support", parse_mode="HTML")
            print(f"Неверный id {unique_code}")
    else:
        await message.answer(f"🔗 <b>Вот твоя личная ссылка:</b>\n\n{LINK}?start={message.from_user.id}\n\nОпубликуй её в <b>Telegram</b>, <b>TikTok</b>, <b>VK</b>, <b>Instagram</b> и получай анонимные сообщения\n\n<i>/mystats - узнать свою статистику\n/support - обратиться в поддержку</i>", 
                             reply_markup=removeButton, 
                             disable_web_page_preview=True,
                             parse_mode="HTML")

@dp.message_handler(commands="support", state='*')
async def commands_support(message, state=FSMContext):
    await message.answer("⚙ <i>Если у Вас появились вопросы по работе бота, то можете написать сюда -</i> @AnQSupport", parse_mode="HTML")
    await state.finish()

@dp.message_handler(commands="link", state='*')
async def commands_support(message, state=FSMContext):
    await message.answer(f"🔗 <b>Вот твоя личная ссылка:</b>\n\n{LINK}?start={message.from_user.id}\n\nОпубликуй её в <b>Telegram</b>, <b>TikTok</b>, <b>VK</b>, <b>Instagram</b> и получай анонимные сообщения", 
                             reply_markup=removeButton, 
                             disable_web_page_preview=True,
                             parse_mode="HTML")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "cancel", state=(User.write, User.answer, None))
async def user_write_cancel(call, state):
    await call.answer("Отмена отправки")
    await call.message.edit_text(f"⚙ <b>Вы отменили отправку сообщения!</b>\n\n🔗 Вот твоя личная ссылка:\n\n{LINK}?start={call.from_user.id}\n\nОпубликуй её и получай анонимные сообщения", parse_mode="HTML", disable_web_page_preview=True)
    await state.finish()

@dp.message_handler(content_types=types.ContentType.ANY, state=User.write)
async def user_write(message: types.Message, state=FSMContext):
    user_id = message.from_user.id
    recip_id = await sendMessage(user_id, message, state)
    if recip_id:
        await increment_field_by_id(user_id, "SENT")
        await increment_field_by_id(recip_id, "RECEIVED")
    await state.finish()

            
@dp.callback_query_handler(lambda c: "NEW" in c.data, state="*")
async def again_send_message(call: types.callback_query, state=FSMContext):
    await call.answer("Новое сообщение")
    await call.message.edit_reply_markup()
    message = await call.message.answer("<b>Отправь новое сообщение пользователю</b>", reply_markup=cancelMenu, parse_mode="HTML")
    async with state.proxy() as data:
        data['message_id'] = message.message_id
        data['other_id'] = str(call.data)[3:]
    await User.write.set()

@dp.callback_query_handler(lambda c: "HU" in c.data, state="*")
async def WhoIsIt(call, state=FSMContext):
    user_id = call.from_user.id
    if user_id in VIP.users:
        name, username = await get_names(int(call.data[2:]))
        name = html.escape(name)
        username = html.escape(username)
        if await check_end(user_id):
            await call.answer("Кончилась")
            await bot.send_message(user_id, f"<b>Срок действия подписки закончился.</b>\nЕсли хочешь снова видеть имена отправителей, то можно приобрести <b>VIP</b>👑\n\n<b>Цена:</b> <s>{FIRST_PRICE} рублей</s> <b>{PRICE} рублей</b> (-{100-int(math.ceil(PRICE*100/FIRST_PRICE))}%)\n<b>Срок: 30 ДНЕЙ</b>", 
                               parse_mode="HTML", 
                               reply_markup = await GetPaymentsMenu(user_id))
            await VIP.del_vip_user(user_id)
        else:
            await call.answer("Человек")
            await bot.send_message(user_id, f"<b>Данные о человеке, который отправил сообщение выше:</b>\n\n<b>Имя -</b> {name}\n<b>Юзернейм -</b> {username}", parse_mode="HTML", reply_to_message_id=call.message.message_id, protect_content=True)
    else:
        await call.answer("Покупка VIP")
        await bot.send_message(user_id, f"<b>Хочешь узнать, кто такое отправляет?</b>\n\nЕсли хочешь видеть имена отправителей, то можно приобрести <b>VIP</b>👑\n\n<b>Цена:</b> <s>{FIRST_PRICE} рублей</s> <b>{PRICE} рублей</b> <i>(-{100-int(math.ceil(PRICE*100/FIRST_PRICE))}%)</i>\n<b>Срок: 30 ДНЕЙ</b>", 
                               parse_mode="HTML", 
                               reply_markup = await GetPaymentsMenu(user_id))

@dp.callback_query_handler(lambda c: "check" == c.data, state="*")
async def CheckPayment(call, state=FSMContext):
    user_id = call.from_user.id
    if user_id not in VIP.users:
        label = "M"+str(user_id)
        if await check_payment(label):
            await VIP.add_vip_user(user_id)
            await call.answer("Оплата прошла успешно")
            await bot.edit_message_text("<b>Вы приобрели VIP-статус👑</b>\n\n<b>Теперь Вы видите информацию о пользователе, который вам написал!</b>\n\n<i><b>СРОК ДЕЙСТВИЯ: 7 ДНЕЙ</b></i>", 
                                        chat_id=user_id, 
                                        message_id=call.message.message_id, 
                                        parse_mode="HTML")
            print(f"{user_id} добавлен VIP\n")
        else:
            await call.answer("Оплата не получена")
    else:
        await call.answer("Вы уже VIP")

@dp.message_handler(Text("Отмена ❌"), state=User.answer)
async def user_write_cancel(message: types.Message, state):
    await message.answer("Вы отменили отправку ответа!", reply_markup=removeButton)
    await state.finish()

@dp.callback_query_handler(lambda c: "AN" in c.data, state="*")
async def answer(call, state):
    user_id = call.from_user.id
    await call.answer("Ответ пользователю")
    message = await bot.send_message(user_id, "<b>Отправьте ваш ответ на анонимное сообщение</b>", reply_markup=cancelMenu, parse_mode="HTML")
    await User.answer.set()
    async with state.proxy() as data:
        data['other_id'] = call.data[2:]
        data["message_id"] = message.message_id

@dp.message_handler(content_types=ALL_CONTENT_TYPE, state=User.answer)
async def user_answer(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    async with state.proxy() as data:
        recip_id = await sendMessage(user_id, message, state, answer=True)
        if recip_id:
            await increment_field_by_id(user_id, "SENT")
            await increment_field_by_id(recip_id, "RECEIVED")
        await state.finish()

@dp.message_handler(commands="mystats", state="*")
async def user_write(message: types.Message, state=FSMContext):
    user_id = message.from_user.id
    recevied, sent, transitions = await get_stats(user_id)
    await message.answer(f"🌟<b>Ваша статистика:</b>\n\n\n💬 <i><b>Получено:</b></i> {recevied}\n\n↩️ <i><b>Отправлено:</b></i> {sent}\n\n👁‍🗨 <i><b>Переходов по вашей ссылке:</b></i> {transitions}\n\n\n<i>{SMALL_LINK}</i>", parse_mode="HTML")


# админка #
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID, commands="add_vip", state="*")
async def add_new_vip_users_admin(message: types.Message, state: FSMContext):
    text = message.text
    if len(text.split(" ")) == 2:
        _, user_id = text.split(" ")
        if user_id.isdigit():
            try:
                await VIP.add_vip_user(int(user_id))
                await message.answer("пользователь добавлен")
            except:
                await message.answer("Неизвестная ошибка")
        else:
            await message.answer("ID должен быть числом")
    else:
        await message.answer("Неправильное количество атрибутов")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID, commands="del_vip", state="*")
async def del_vip_vip_users_admin(message: types.Message, state: FSMContext):
    text = message.text
    if len(text.split(" ")) == 2:
        _, user_id = text.split(" ")
        if user_id.isdigit():
            try:
                await VIP.del_vip_user(int(user_id))
                await message.answer("пользователь удалён")
            except:
                await message.answer("Неизвестная ошибка")
        else:
            await message.answer("ID должен быть числом")
    else:
        await message.answer("Неправильное количество атрибутов")

@dp.callback_query_handler(state="*")
async def not_available(call, state=FSMContext):
    await call.answer("Действие недоступно")
    await call.message.delete() 

@dp.message_handler(state="*")
async def not_state(message, state=FSMContext):
    await message.answer(f"🔗 <b>Вот твоя личная ссылка:</b>\n\n{LINK}?start={message.from_user.id}\n\nОпубликуй её в <b>Telegram</b>, <b>TikTok</b>, <b>VK</b>, <b>Instagram</b> и получай анонимные сообщения\n\n<i>/mystats - узнать свою статистику\n/support - обратиться в поддержку</i>", 
                             reply_markup=removeButton, 
                             disable_web_page_preview=True,
                             parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)