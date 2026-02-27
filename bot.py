import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import init_db, add_task, get_tasks, complete_task, get_progress
from datetime import time
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
YOUR_CHAT_ID = int(os.environ.get("CHAT_ID", "0"))  # Tu chat ID personal
TZ = pytz.timezone("America/Bogota")  # Cambia a tu zona horaria


# ─── Comandos ────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *¡Hola! Soy tu agente de tareas.*\n\n"
        "📋 `/add <tarea>` — Agregar tarea\n"
        "📝 `/list` — Ver tareas pendientes\n"
        "✅ `/done <id>` — Marcar como hecha\n"
        "📊 `/progress` — Ver tu avance\n"
        "📅 `/all` — Ver todas (incluye completadas)",
        parse_mode="Markdown"
    )

async def add(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ Usa: `/add nombre de la tarea`", parse_mode="Markdown")
        return
    task_name = " ".join(ctx.args)
    task_id = add_task(task_name)
    await update.message.reply_text(f"✅ Tarea #{task_id} agregada:\n*{task_name}*", parse_mode="Markdown")

async def list_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks(done=False)
    if not tasks:
        await update.message.reply_text("🎉 ¡No tienes tareas pendientes!")
        return
    text = "📋 *Tareas pendientes:*\n\n"
    for t in tasks:
        text += f"  `#{t[0]}` {t[1]}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def all_tasks(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tasks = get_tasks(done=None)
    if not tasks:
        await update.message.reply_text("No tienes ninguna tarea aún.")
        return
    text = "📋 *Todas las tareas:*\n\n"
    for t in tasks:
        icon = "✅" if t[2] else "⏳"
        text += f"  {icon} `#{t[0]}` {t[1]}\n"
    await update.message.reply_text(text, parse_mode="Markdown")

async def done(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("❌ Usa: `/done <id>`", parse_mode="Markdown")
        return
    try:
        task_id = int(ctx.args[0])
        task_name = complete_task(task_id)
        if task_name:
            await update.message.reply_text(f"🎉 ¡Completada!\n*{task_name}*", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No encontré esa tarea.")
    except ValueError:
        await update.message.reply_text("❌ El ID debe ser un número.")

async def progress(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    total, done_count, pct = get_progress()
    bar = build_bar(pct)
    await update.message.reply_text(
        f"📊 *Tu progreso:*\n\n"
        f"{bar} `{pct}%`\n\n"
        f"✅ {done_count} completadas de {total} totales",
        parse_mode="Markdown"
    )

def build_bar(pct):
    filled = int(pct / 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty


# ─── Recordatorios automáticos ───────────────────────────────────────────────

async def morning_summary(app):
    tasks = get_tasks(done=False)
    total, done_count, pct = get_progress()
    bar = build_bar(pct)

    if not tasks:
        msg = "☀️ *¡Buenos días!*\n\n🎉 No tienes tareas pendientes. ¡Disfruta el día!"
    else:
        task_list = "\n".join([f"  • {t[1]}" for t in tasks[:10]])
        msg = (
            f"☀️ *¡Buenos días! Aquí tu resumen:*\n\n"
            f"📊 Progreso: {bar} `{pct}%`\n\n"
            f"📋 *Pendientes ({len(tasks)}):*\n{task_list}"
        )
        if len(tasks) > 10:
            msg += f"\n  ...y {len(tasks)-10} más"

    await app.bot.send_message(chat_id=YOUR_CHAT_ID, text=msg, parse_mode="Markdown")

async def evening_reminder(app):
    tasks = get_tasks(done=False)
    if tasks:
        task_list = "\n".join([f"  • {t[1]}" for t in tasks[:5]])
        msg = (
            f"🌙 *Recordatorio nocturno*\n\n"
            f"Aún tienes {len(tasks)} tarea(s) pendientes:\n{task_list}\n\n"
            f"¿Lograste avanzar hoy? Usa `/done <id>` para marcarlas ✅"
        )
        await app.bot.send_message(chat_id=YOUR_CHAT_ID, text=msg, parse_mode="Markdown")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("list", list_tasks))
    app.add_handler(CommandHandler("all", all_tasks))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("progress", progress))

    scheduler = AsyncIOScheduler(timezone=TZ)
    scheduler.add_job(morning_summary, "cron", hour=8, minute=0, args=[app])
    scheduler.add_job(evening_reminder, "cron", hour=21, minute=0, args=[app])
    scheduler.start()

    logger.info("Bot iniciado ✅")
    app.run_polling()

if __name__ == "__main__":
    main()