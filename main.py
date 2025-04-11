# Bot do Betbô - Replit Ready (com link único para grupo VIP + gerenciamento + rota ativa)

from telegram import Update, ChatInviteLink, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging
import os
from flask import Flask
from threading import Thread

# Configurações
BOT_TOKEN = "7584520662:AAEC1EhcTCNdw16LjUUBhGGwUj4o-0w_vg4"
GROUP_ID = -1002586137239
ADMIN_ID = 1355815619  # Substitua pelo seu Telegram ID para receber notificações

# Ativar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Iniciar Flask para manter o Replit vivo
app_web = Flask('')


@app_web.route('/')
def home():
    return "🤖 Betbô está online."


def run_web():
    app_web.run(host='0.0.0.0', port=8080)


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text(
        "🤖 Bem-vindo ao Betbô, o robô que te entrega análises estatísticas sobre escanteios, cartões, gols e chutes a gol com base nos últimos jogos!\n\n"
        "Todos os sinais enviados no grupo são estudados, filtrados e baseados em dados reais. O objetivo é aumentar as chances com múltiplas inteligentes, sem prometer milagres.\n\n"
        "📌 Para acessar o grupo VIP com os sinais diários:\n"
        "1️⃣ Faça um Pix de R$5 para:\n"
        "🔑 Chave Pix: betbooficial@gmail.com\n"
        "2️⃣ Envie o comprovante aqui mesmo nesta conversa.\n\n"
        "Assim que validarmos, você receberá o link exclusivo de acesso ao grupo VIP! 🚀"
    )


# Comando para liberar o usuário manualmente: /liberar @usuario
async def liberar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Use: /liberar @usuario")
        return

    username = context.args[0].replace("@", "")
    try:
        user_id = None
        for u in context.bot_data.get("users", []):
            if u["username"] == username:
                user_id = u["id"]
                break

        if not user_id:
            await update.message.reply_text(
                "Usuário não encontrado nos registros recentes.")
            return

        invite_link: ChatInviteLink = await context.bot.create_chat_invite_link(
            chat_id=GROUP_ID, expire_date=None, member_limit=1)
        await context.bot.send_message(
            chat_id=user_id,
            text=
            f"🔓 Acesso liberado! Clique aqui para entrar no grupo VIP:\n{invite_link.invite_link}"
        )
        await update.message.reply_text(
            "✅ Link enviado com sucesso para o usuário.")

    except Exception as e:
        logger.error(f"Erro ao liberar acesso: {e}")
        await update.message.reply_text(
            "Erro ao gerar o link. Verifique o ID do grupo e as permissões do bot."
        )


# Comando /usuarios - listar todos os registrados
async def listar_usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ADMIN_ID:
        return

    usuarios = context.bot_data.get("users", [])
    if not usuarios:
        await update.message.reply_text("Nenhum usuário registrado ainda.")
        return
    lista = "\n".join(
        [f"• @{u['username']} (ID: {u['id']})" for u in usuarios])
    await update.message.reply_text(f"📋 Últimos usuários registrados:\n{lista}"
                                    )


# Registrar apenas mensagens privadas
async def registrar_usuario(update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    if update.message is None:
        return

    user = update.message.from_user
    usuarios = context.bot_data.get("users", [])
    if not any(u["id"] == user.id for u in usuarios):
        usuarios.append({
            "id": user.id,
            "username": user.username or "sem_username"
        })
        context.bot_data["users"] = usuarios
        logger.info(f"Usuário registrado: {user.username} ({user.id})")

    if update.message.photo:
        photo = update.message.photo[-1]
        await photo.get_file().then(
            lambda f: f.download_to_drive("comprovante_temp.jpg"))
        with open("comprovante_temp.jpg", "rb") as img:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=InputFile(img),
                caption=
                f"📬 Novo comprovante de @{user.username or 'sem_username'} (ID: {user.id})"
            )
        os.remove("comprovante_temp.jpg")
    elif update.message.document:
        await update.message.forward(chat_id=ADMIN_ID)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=
            f"📬 @{user.username or 'sem_username'} enviou um arquivo (ID: {user.id})"
        )
    else:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=
            f"📬 Novo comprovante de @{user.username or 'sem_username'} (ID: {user.id}): {update.message.text}"
        )

    await update.message.reply_text(
        "📩 Comprovante recebido! Em breve validaremos e liberamos o acesso. ✅")


# Inicializar bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("liberar", liberar))
app.add_handler(CommandHandler("usuarios", listar_usuarios))
app.add_handler(MessageHandler(filters.ALL, registrar_usuario))

if __name__ == "__main__":
    print("🚀 Betbô Bot está rodando!")
    Thread(target=run_web).start()  # Inicia a web app paralelamente
    app.run_polling()
