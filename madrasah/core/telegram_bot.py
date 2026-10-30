from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from asgiref.sync import sync_to_async
from decouple import config
from .models import ParentPortal, Attendance, Grade

TOKEN = config("TELEGRAM_BOT_TOKEN")

# Ботни яратамиз
application = ApplicationBuilder().token(TOKEN).build()

# /start буйруғи
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    contact_button = KeyboardButton(text="📱 Телефон номерди жөнөтүү", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(
        f"Саламатсызбы, {user_first_name}!\n"
        f"Имам Аль-Бухорий медресесинин расмий ботуна кош келдиңиз.\n\n"
        f"Балаңыздын маалыматтарын көрүү үчүн алгач төмөнкү баскычты басып, телефон номериңизди жөнөтүңіз:",
        reply_markup=reply_markup
    )

@sync_to_async
def get_and_update_parent(clean_phone, user_id):
    parent = ParentPortal.objects.filter(phone__icontains=clean_phone).first()
    if parent:
        parent.telegram_chat_id = str(user_id)
        parent.save()
        return parent
    return None

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        phone = contact.phone_number
        clean_phone = phone.replace("+", "")
        parent = await get_and_update_parent(clean_phone, update.effective_user.id)
        
        if parent:
            await update.message.reply_text(
                f"✅ Куттуктайбыз, {parent.parent_name}! Сиздин Telegram профилиңиз системага ийгиликтүү туташтырылды.\n\n"
                f"Эми буйруқларни колдоно аласыз:\n"
                f"/davomat — Акыркы катышуу\n"
                f"/baholar — Акыркы баалар\n"
                f"/kontrakt — Контракт маалыматтары",
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(
                "❌ Кечиресиз, бул телефон номер медресе базасынан табылган жок.",
                reply_markup=ReplyKeyboardRemove()
            )

@sync_to_async
def get_student_attendances(user_id):
    parent = ParentPortal.objects.filter(telegram_chat_id=str(user_id)).first()
    if not parent:
        return None, []
    return parent, list(Attendance.objects.filter(student=parent.student).order_by('-date')[:5])

async def davomat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parent, attendances = await get_student_attendances(update.effective_user.id)
    if not parent:
        await update.message.reply_text("⚠️ Аккаунтиңиз туташтырыла элек. /start басыңыз.")
        return
    if not attendances:
        await update.message.reply_text("Катышуу маалыматтары али жок.")
        return

    msg = f"📌 *{parent.student.name} — акыркы катышуулар:*\n\n"
    status_map = {'present': '✅ Келди', 'absent': '❌ Келган жок', 'late': '⚠️ Кечикти', 'excused': 'ℹ️ Себептүү'}
    for att in attendances:
        msg += f"📅 {att.date}: {status_map.get(att.status, att.status)}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

@sync_to_async
def get_student_grades(user_id):
    parent = ParentPortal.objects.filter(telegram_chat_id=str(user_id)).first()
    if not parent:
        return None, []
    return parent, list(Grade.objects.filter(student=parent.student).order_by('-date')[:5])

async def baholar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parent, grades = await get_student_grades(update.effective_user.id)
    if not parent:
        await update.message.reply_text("⚠️ Аккаунтиңиз туташтырыла элек. /start басыңыз.")
        return
    if not grades:
        await update.message.reply_text("Баалар али жок.")
        return

    msg = f"📚 *{parent.student.name} — акыркы баалар:*\n\n"
    for g in grades:
        msg += f"📖 {g.subject}: *{g.score} балл* ({g.date})\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

@sync_to_async
def get_student_contract(user_id):
    return ParentPortal.objects.filter(telegram_chat_id=str(user_id)).first()

async def kontrakt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parent = await get_student_contract(update.effective_user.id)
    if not parent:
        await update.message.reply_text("⚠️ Аккаунтиңиз туташтырыла элек. /start басыңыз.")
        return
    student = parent.student
    msg = (
        f"💳 *Контракт маалыматтары*\n\n"
        f"👨‍👦 Окуучу: {student.name}\n"
        f"💰 Жалпы: {student.contract_amount} сом\n"
        f"✅ Төлөнгөнү: {student.total_paid} сом\n"
        f"⚠️ Карыз: {student.remaining_debt} сом"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# Ҳандлерларни қўшиш
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("davomat", davomat_command))
application.add_handler(CommandHandler("baholar", baholar_command))
application.add_handler(CommandHandler("kontrakt", kontrakt_command))
application.add_handler(MessageHandler(filters.CONTACT, handle_contact))