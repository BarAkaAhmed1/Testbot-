import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")

scores = {}
active = {}

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ברוכים הבאים! 🎮\n"
        "/play — להתחיל סיבוב\n"
        "/score — לראות ניקוד"
    )

async def play(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    number = random.randint(10, 99)
    active[chat_id] = str(number)
    await update.message.reply_text(f"⚡ מי כותב ראשון את המספר הזה?\n\n*{number}*", parse_mode="Markdown")

async def guess(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.strip()

    if chat_id not in active:
        return

    if text == active[chat_id]:
        del active[chat_id]

        if chat_id not in scores:
            scores[chat_id] = {}
        scores[chat_id][user.id] = scores[chat_id].get(user.id, 0) + 1
        pts = scores[chat_id][user.id]

        await update.message.reply_text(
            f"🏆 {user.first_name} ניצח!\n"
            f"סה״כ נקודות: {pts}\n\n"
            f"/play לסיבוב הבא"
        )

async def score(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in scores or not scores[chat_id]:
        await update.message.reply_text("עדיין אין ניקוד. /play להתחיל!")
        return

    lines = []
    for uid, pts in sorted(scores[chat_id].items(), key=lambda x: -x[1]):
        try:
            member = await ctx.bot.get_chat_member(chat_id, uid)
            name = member.user.first_name
        except:
            name = str(uid)
        lines.append(f"{name}: {pts} נקודות")

    await update.message.reply_text("📊 טבלת ניקוד:\n\n" + "\n".join(lines))

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("score", score))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guess))
app.run_polling()
