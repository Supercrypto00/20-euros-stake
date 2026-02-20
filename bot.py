import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

ASK_USERNAME, ASK_NETWORK, ASK_WALLET = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Réclamer mes 20€", callback_data="claim")]
    ])
    await update.message.reply_text(
        "🎁 Bienvenue ! Clique ci-dessous pour commencer.",
        reply_markup=keyboard
    )

async def claim_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📝 Envoie ton pseudo Stake :")
    return ASK_USERNAME

async def ask_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stake_username"] = update.message.text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Solana", callback_data="SOL"),
            InlineKeyboardButton("ETH", callback_data="ETH"),
            InlineKeyboardButton("BTC", callback_data="BTC"),
        ]
    ])

    await update.message.reply_text(
        "💳 Choisis le réseau :",
        reply_markup=keyboard
    )
    return ASK_NETWORK

async def ask_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["network"] = query.data

    await update.message.reply_text(
        "📩 Envoie ton adresse wallet :"
    )
    return ASK_WALLET

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔍 Vérification...")

    steps = [
        "🔍 Recherche du wallet...",
        "🧠 Analyse...",
        "📡 Vérification...",
        "✅ Wallet valide."
    ]

    for s in steps:
        await asyncio.sleep(1)
        await msg.edit_text(s)

    await update.message.reply_text(
        "✅ Demande envoyée.\n\n"
        "💸 Paiement sous 24h si aucun problème.\n\n"
        "⚠️ Problèmes possibles :\n"
        "• Double compte\n"
        "• Wager insuffisant\n"
        "• Wallet invalide"
    )

    await context.bot.send_message(
        ADMIN_ID,
        f"🆕 Nouvelle demande :\n"
        f"👤 User: {context.user_data['stake_username']}\n"
        f"🌐 Network: {context.user_data['network']}\n"
        f"💳 Wallet: {update.message.text}"
    )

    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(claim_button, pattern="claim")],
        states={
            ASK_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_network)
            ],
            ASK_NETWORK: [
                CallbackQueryHandler(ask_wallet)
            ],
            ASK_WALLET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, finish)
            ],
        },
        fallbacks=[],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    app.run_polling()


if __name__ == "__main__":
    main()
