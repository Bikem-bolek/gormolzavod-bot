import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")


users = {}

valid_codes = {
    "KURT100": 50,
    "KURT200": 50,
    "KURT500": 50,
    "GORMOL100": 50,
    "AKMOLA200": 50,
}

used_codes = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        """
🎁 Гормолзавод Бонус бағдарламасы

Қош келдіңіз!

Командалар:

/register - Тіркелу
/bonus - Бонустарым
/gifts - Сыйлықтар
/rules - Ережелер
/contacts - Байланыс

📌 Кодты жай ғана чатқа жіберіңіз.
"""
    )


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id in users:
        await update.message.reply_text(
            "✅ Сіз бұрыннан тіркелгенсіз."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "📝 Атыңызды енгізіңіз:"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["name"] = update.message.text

    await update.message.reply_text(
        "📱 Телефон нөміріңізді енгізіңіз:"
    )

    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = context.user_data["name"]
    phone = update.message.text

    users[update.effective_user.id] = {
        "name": name,
        "phone": phone,
        "bonus": 50
    }

    await update.message.reply_text(
        f"""
✅ Тіркелу сәтті аяқталды!

👤 Аты: {name}
📱 Телефон: {phone}

🎁 Қош келдіңіз бонусы:
50 ұпай

💰 Баланс:
50 ұпай
"""
    )

    return ConversationHandler.END


async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = users.get(update.effective_user.id)

    if not user:
        await update.message.reply_text(
            "Алдымен /register арқылы тіркеліңіз."
        )
        return

    await update.message.reply_text(
        f"""
🎁 Менің бонустарым

👤 {user['name']}

💰 Баланс:
{user['bonus']} ұпай
"""
    )


async def gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🎁 Сыйлықтар

500 ұпай ➜ 5% жеңілдік

1000 ұпай ➜ 10% жеңілдік

2000 ұпай ➜ 15% жеңілдік

5000 ұпай ➜ Тегін өнім

10000 ұпай ➜ Өнімдер жиынтығы

20000 ұпай ➜ Бас жүлде
"""
    )


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
📋 Акция ережелері

1. Өнімді сатып алыңыз
2. QR кодты сканерлеңіз
3. Ботқа тіркеліңіз
4. Кодты енгізіңіз
5. Ұпай жинаңыз
6. Сыйлық алыңыз
"""
    )


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
📞 Байланыс

ТОО «Гормолзавод»

☎️ +7 747 377 15 29

📧 ok@gormolzavod.kz

📍 Көкшетау қаласы
"""
    )


async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.upper().strip()

    commands = [
        "/START",
        "/REGISTER",
        "/BONUS",
        "/GIFTS",
        "/RULES",
        "/CONTACTS"
    ]

    if text in commands:
        return

    user = users.get(update.effective_user.id)

    if not user:
        await update.message.reply_text(
            "❌ Алдымен /register арқылы тіркеліңіз."
        )
        return

    if text in used_codes:
        await update.message.reply_text(
            """
⚠️ Бұл код бұрын тіркелген.

Басқа код енгізіңіз.
"""
        )
        return

    if text not in valid_codes:
        await update.message.reply_text(
            """
❌ Код жарамсыз!

Кодты қайта тексеріп енгізіңіз.
"""
        )
        return

    points = valid_codes[text]

    user["bonus"] += points

    used_codes.add(text)

    if user["bonus"] >= 500:

        await update.message.reply_text(
            f"""
✅ Код сәтті тіркелді!

🎁 +{points} бонус қосылды.

💰 Сіздің балансыңыз:
{user['bonus']} ұпай

🎉 Құттықтаймыз!

Сіз сыйлық алуға жеткілікті ұпай жинадыңыз.
"""
        )

    else:

        remain = 500 - user["bonus"]

        await update.message.reply_text(
            f"""
✅ Код сәтті тіркелді!

🎁 +{points} бонус қосылды.

💰 Жалпы бонус:
{user['bonus']} ұпай

🎯 Келесі сыйлыққа дейін:
{remain} ұпай қалды.
"""
        )


app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("register", register)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
    },
    fallbacks=[],
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("bonus", bonus))
app.add_handler(CommandHandler("gifts", gifts))
app.add_handler(CommandHandler("rules", rules))
app.add_handler(CommandHandler("contacts", contacts))

app.add_handler(conv_handler)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        check_code
    )
)

print("✅ Bot started!")

app.run_polling()
