# 🤖 Bot de Tareas — Telegram

Bot personal para gestionar tareas con recordatorios automáticos.

## Comandos
| Comando | Descripción |
|---|---|
| `/add <tarea>` | Agregar nueva tarea |
| `/list` | Ver tareas pendientes |
| `/done <id>` | Marcar tarea como completada |
| `/progress` | Ver porcentaje de avance |
| `/all` | Ver todas las tareas |

---

## ⚙️ Setup local (probar en tu PC)

```bash
pip install -r requirements.txt
export BOT_TOKEN="tu_token_aqui"
export CHAT_ID="tu_chat_id"
python bot.py
```

**¿Cómo obtengo mi CHAT_ID?**
Abre Telegram, busca @userinfobot y escríbele. Te responde con tu ID.

---

## 🚀 Deploy gratis en Render

1. Sube estos 3 archivos a un repo de GitHub (público o privado)
2. Entra a https://render.com y crea cuenta gratis
3. Click en **New → Web Service**
4. Conecta tu repo de GitHub
5. Configura:
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
6. En **Environment Variables** agrega:
   - `BOT_TOKEN` = tu token de BotFather
   - `CHAT_ID` = tu chat ID numérico
7. Click **Deploy** ✅

### ⚠️ Render free tier se "duerme" tras 15min sin tráfico HTTP
Para evitarlo, el bot usa polling (no webhook) así que seguirá funcionando.
Render puede reiniciarlo pero los recordatorios seguirán llegando.

---

## 🕐 Cambiar horario de recordatorios

En `bot.py`, líneas del scheduler:
```python
scheduler.add_job(morning_summary, "cron", hour=8, minute=0, ...)   # 8:00 AM
scheduler.add_job(evening_reminder, "cron", hour=21, minute=0, ...) # 9:00 PM
```
Cambia `hour` y `minute` a tu gusto.

## 🌍 Cambiar zona horaria

En `bot.py`:
```python
TZ = pytz.timezone("America/Bogota")  # Cámbialo si estás en otro país
```
Otras opciones: `America/Mexico_City`, `America/Santiago`, `Europe/Madrid`