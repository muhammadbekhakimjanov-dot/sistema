import os
import django
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from asgiref.sync import sync_to_async

# Django чөйрөсүн тууралоо
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'madrasah.config.settings')
django.setup()

from madrasah.core.models import ParentPortal, Attendance, Grade

# /start буйругу
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    contact_button = KeyboardButton(text="📱 Телефон номерди жөнөтүү", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Саламатсызбы, {user_first_name}!\n"
        f"Имам Аль-Бухорий медресесинин расмий ботуна кош келдиңиз.\n\n"
        f"Балаңыздын маалыматтарын көрүү жана көзөмөлдөө үчүн алгач төмөнкү баскычты басып, телефон номериңизди жөнөтүңүз:",
        reply_markup=reply_markup
    )

# Базадан ота-онани қидириш ва сақлаш (sync_to_async ёрдамида)
@sync_to_async
def get_and_update_parent(clean_phone, user_id):
    parent = ParentPortal.objects.filter(phone__icontains=clean_phone).first()
    if parent:
        parent.telegram_chat_id = str(user_id)
        parent.save()
        return parent
    return None

# Телефон номерди кабыл алып, база менен байланыштыруу
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        phone = contact.phone_number
        clean_phone = phone.replace("+", "")
        
        parent = await get_and_update_parent(clean_phone, update.effective_user.id)
        
        if parent:
            await update.message.reply_text(
                f"✅ Куттуктайбыз, {parent.parent_name}! Сиздин Telegram профилиңиз системага ийгиликтүү туташтырылды.\n\n"
                f"Эми төмөнкү буйруқтарды колдоно аласыз:\n"
                f"attendance /davomat — Балаңыздын акыркы катышуусун көрүү\n"
                f"attendance /baholar — Акыркы бааларын көрүү\n"
                f"attendance /kontrakt — Контракт жана карыз маалыматтарын көрүү",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "❌ Кечиресиз, бул телефон номер медресе базасынан табылган жок. Сураныч, администрацияга кайрылыңыз.",
                reply_markup=ReplyKeyboardRemove()
            )


# Базадан давоматни олиб келиш (sync_to_async)
@sync_to_async
def get_student_attendances(user_id):
    parent = ParentPortal.objects.filter(telegram_chat_id=str(user_id)).first()
    if not parent:
        return None, []
    attendances = list(Attendance.objects.filter(student=parent.student).order_by('-date')[:5])
    return parent, attendances

# /davomat командаси
async def davomat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    parent, attendances = await get_student_attendances(user_id)

    if not parent:
        await update.message.reply_text("⚠️ Сиздин Telegram аккаунтиңиз системага туташтырыла элек. Сураныч, /start басып номер жөнөтүңүз.")
        return

    if not attendances:
        await update.message.reply_text(f"Урматтуу {parent.parent_name}, уулуңуз {parent.student.name} боюнча катышуу маалыматтары али жок.")
        return

    msg = f"📌 *{parent.student.name}* ({parent.student.group}) — акыркы катышуулар:\n\n"
    status_map = {
        'present': '✅ Катышты (Келди)',
        'absent': '❌ Келган жок',
        'late': '⚠️ Кечикти',
        'excused': 'ℹ️ Себептүү'
    }
    
    for att in attendances:
        status_text = status_map.get(att.status, att.status)
        msg += f"📅 {att.date}: {status_text}\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# Базадан баҳоларни олиб келиш (sync_to_async)
@sync_to_async
def get_student_grades(user_id):
    parent = ParentPortal.objects.filter(telegram_chat_id=str(user_id)).first()
    if not parent:
        return None, []
    grades = list(Grade.objects.filter(student=parent.student).order_by('-date')[:5])
    return parent, grades

# /baholar командаси
async def baholar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    parent, grades = await get_student_grades(user_id)

    if not parent:
        await update.message.reply_text("⚠️ Сиздин Telegram аккаунтиңиз системага туташтырыла элек. Сураныч, /start басып номер жөнөтүңүз.")
        return

    if not grades:
        await update.message.reply_text(f"Урматтуу {parent.parent_name}, уулуңуз {parent.student.name} боюнча баалар али жок.")
        return

    msg = f"📚 *{parent.student.name}* ({parent.student.group}) — акыркы баалар:\n\n"
    for g in grades:
        msg += f"📖 {g.subject}: *{g.score} балл* ({g.date})\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# Базадан контракт маълумотларини олиб келиш (sync_to_async)
@sync_to_async
def get_student_contract(user_id):
    parent = ParentPortal.objects.filter(telegram_chat_id=str(user_id)).first()
    if not parent:
        return None
    return parent

# /kontrakt командаси
async def kontrakt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    parent = await get_student_contract(user_id)

    if not parent:
        await update.message.reply_text("⚠️ Сиздин Telegram аккаунтиңиз системага туташтырыла элек. Сураныч, /start басып номер жөнөтүңүз.")
        return

    student = parent.student
    msg = (
        f"💳 *Контракт маалыматтары*\n\n"
        f"👨‍👦 Окуучу: {student.name} ({student.group})\n"
        f"💰 Жалпы контракт: {student.contract_amount} сом\n"
        f"✅ Төлөнгөнү: {student.total_paid} сом\n"
        f"⚠️ Калган карыз: {student.remaining_debt} сом"
    )

    await update.message.reply_text(msg, parse_mode="Markdown")


if __name__ == '__main__':
    TOKEN = "8723045070:AAGCb6vWDINDNTbKSLYDLthP9_ufxYJq2II"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Бардык буйруқлар ва ҳандлерларни ботга улаймиз
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("davomat", davomat_command))
    app.add_handler(CommandHandler("baholar", baholar_command))
    app.add_handler(CommandHandler("kontrakt", kontrakt_command))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    print("🤖 Бот иштеп баштады...")
    app.run_polling()