# 🤖 Avto Trading Bot (Binance Demo + Telegram)

**ccxt** orqali Binance demo (testnet) hisobida avtomatik savdo qiluvchi va **aiogram** Telegram bot bilan boshqariladigan loyiha.

---

## ✨ Imkoniyatlar

- 📈 **Avto savdo:** ccxt orqali Binance demo hisobida buyurtmalar
- 🤖 **Telegram boshqaruvi:** botdan `/start`, savdoni yoqish/o'chirish
- 🌐 **Webhook rejimi:** Render'da ishlash uchun aiohttp webhook
- 📝 **Savdo loglari:** CSV faylga yozib borish
- 🧪 **Demo (sandbox) rejimi:** haqiqiy pul ishlatilmaydi

---

## 🛠 Texnologiyalar

| Texnologiya | Maqsad |
|---|---|
| **Python 3.10+** | Asosiy til |
| **ccxt** | Binance birjasi |
| **aiogram 3.x** | Telegram bot |
| **aiohttp** | Webhook server |
| **python-dotenv** | Muhit o'zgaruvchilari |

---

## ⚙️ O'rnatish

```bash
git clone https://github.com/dastonbek8747/Avto_trading_bot.git
cd Avto_trading_bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` fayl yarating:

```env
binance_demo_api=...
binance_demo_secret=...
Bot_token=123456:ABC...
WEBHOOK_URL=https://your-app.onrender.com
```

> 🔒 `.env` git'ga qo'shilmaydi.

---

## ▶️ Ishga tushirish

**Lokal (polling):**

```bash
python main.py
```

**Render (webhook):** `WEBHOOK_URL` ni sozlab, servisni joylashtiring. Port `10000`.

---

## 📁 Loyiha tuzilishi

```
Avto_trading_bot/
├── main.py              # Telegram bot + webhook
├── avto_trayde_bot.py   # Savdo mantiqi
├── requirements.txt
└── .gitignore
```

---

## ⚠️ Ogohlantirish

Demo rejimida ishlaydi. Haqiqiy savdoga o'tkazishdan oldin strategiyani uzoq vaqt sinab ko'ring. Muallif zarar uchun javobgar emas.

---

## 📄 Litsenziya

Litsenziya ko'rsatilmagan.
