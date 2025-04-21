import ccxt
from datetime import datetime
import csv
import traceback
import asyncio
from dotenv import load_dotenv
import os

# .env faylini yuklash
load_dotenv()

# API kalitlarini o'qish
api_key = os.getenv('binance_demo_api')
secret_key = os.getenv('binance_demo_secret')

# Binance bozorini sozlash
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
        'adjustForTimeDifference': True,
        'recvWindow': 60000,
    }
})

# Sandbox rejimiga o'tkazish
exchange.set_sandbox_mode(True)
# Sozlamalar
sikl_aylanish_vaqti = 15
sotib_olish_narhi = 70
start_sotish_narhi = 155
coin_olish_narhi = 2000
sotib_olindi = False
sotildi = False
avto = True
curs_ozgarish_farqi = 375
RISK_REWARD_RATIO = 3
STOP_LOSS_PERCENT = 5  # Stop loss foizi (misol: 5%)
COINS = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]

# Coin holatlari
coin_data = {
    symbol: {
        "initial_price": None,
        "last_buy_price": None,
        "target_price": None,
        "bought": False,
        "sell_multiplier": start_sotish_narhi
    } for symbol in COINS
}

log_list_bot_write = []


def format_price(price):
    return f"${price:,.2f}"


def log_console(msg):
    log_list_bot_write.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    print(log_list_bot_write[-1])
    save_log_to_file()


def save_log_to_file():
    try:
        with open("bot_log.txt", "a", encoding="utf-8") as f:
            for line in log_list_bot_write:
                f.write(line + "\n")
        log_list_bot_write.clear()
    except Exception:
        error_log(traceback.format_exc())


def error_log(error_text):
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n{error_text}\n{'=' * 80}\n")


def get_prices(symbols):
    try:
        tickers = exchange.fetch_tickers(symbols)
        return {symbol: tickers[symbol]['last'] for symbol in symbols}
    except Exception as e:
        log_console(f"❌ Narxlarni olishda xato: {e}")
        return {}


def get_balance():
    try:
        balance = exchange.fetch_balance()
        usdt_balance = balance['total']['USDT']
        coin_balances = {coin.split('/')[0]: balance['total'].get(coin.split('/')[0], 0) for coin in COINS}
        return usdt_balance, coin_balances
    except Exception:
        error_log(traceback.format_exc())
        return 0, {}


def get_trade_amount(symbol, usdt_amount, price):
    return round(usdt_amount / price, 6) if price else 0


def buy(symbol, price):
    global sotib_olindi, sotildi
    try:
        usdt_balance, _ = get_balance()
        if usdt_balance < coin_olish_narhi:
            log_console(f"⚠️ {symbol} uchun yetarli USDT yo‘q.")
            return

        amount = get_trade_amount(symbol, coin_olish_narhi, price)
        exchange.create_market_order(symbol, "buy", amount)

        coin_data[symbol].update({
            'last_buy_price': price,
            'target_price': price + (coin_data[symbol]['sell_multiplier'] * RISK_REWARD_RATIO),
            'bought': True,
            'sell_multiplier': coin_data[symbol]['sell_multiplier'] * 2
        })
        sotib_olindi = True
        sotildi = False
        log_console(f"✅ {symbol} xarid qilindi @ {format_price(price)}")
        log_console(f"🎯 Maqsad narx: {format_price(coin_data[symbol]['target_price'])}")
    except Exception:
        error_log(traceback.format_exc())


def sell(symbol, price):
    global sotib_olindi, sotildi
    try:
        coin = symbol.split("/")[0]
        balance = exchange.fetch_balance()
        amount = balance[coin]['free']
        if amount < 0.0001:
            log_console(f"⚠️ {symbol} sotish uchun balans yetarli emas.")
            return

        exchange.create_market_order(symbol, "sell", amount)

        sotib_olindi = False
        sotildi = True
        log_console(f"✅ {symbol} sotildi @ {format_price(price)} | Miqdor: {amount:.6f}")

        log_data = {
            "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "symbol": symbol,
            "amount": amount,
            "price": price,
            "total": round(price * amount, 2)
        }

        with open("trade_log.csv", "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=log_data.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(log_data)

        coin_data[symbol].update({
            "last_buy_price": None,
            "target_price": None,
            "initial_price": price,
            "bought": False,
            "sell_multiplier": start_sotish_narhi
        })
    except Exception:
        error_log(traceback.format_exc())


async def multi_coin_bot():
    log_console("🤖 Multi-Coin Trade Bot ishga tushdi")
    while avto:
        try:
            print("\n" + "=" * 80)
            print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Monitoring...")
            print("=" * 80)

            prices = get_prices(COINS)
            usdt_balance, _ = get_balance()

            for symbol in COINS:
                price = prices.get(symbol)
                if not price:
                    continue

                coin = coin_data[symbol]
                if coin['initial_price'] is None:
                    coin['initial_price'] = price
                    log_console(f"📌 {symbol} boshlang‘ich narxi: {format_price(price)}")
                    continue

                diff = price - coin['initial_price']
                status = "Monitoring 🔍"

                # Narx o‘zgarishi
                if price <= coin['initial_price'] - curs_ozgarish_farqi:
                    log_console(
                        f"🔻 {symbol} narxi {curs_ozgarish_farqi}$ tushdi: {format_price(coin['initial_price'])} ➡ {format_price(price)}")
                    if not coin['bought'] or (coin['last_buy_price'] and price >= coin['last_buy_price']):
                        coin['initial_price'] = price
                        log_console(f"📉 {symbol} yangi boshlang‘ich narx: {format_price(price)}")
                elif price >= coin['initial_price'] + curs_ozgarish_farqi:
                    log_console(
                        f"🔺 {symbol} narxi {curs_ozgarish_farqi}$ oshdi: {format_price(coin['initial_price'])} ➡ {format_price(price)}")
                    coin['initial_price'] = price
                    log_console(f"📈 {symbol} yangi boshlang‘ich narx: {format_price(price)}")

                # Stop loss tekshiruvi
                if coin['bought'] and price <= coin['last_buy_price'] * (1 - STOP_LOSS_PERCENT / 100):
                    sell(symbol, price)
                    status = "💰 Stop Loss Triggered"
                # Target price tekshiruvi
                elif coin['bought'] and price >= coin['target_price']:
                    sell(symbol, price)
                    status = "💰 Sell"
                # Sotib olish tekshiruvi
                elif not coin['bought'] and price <= sotib_olish_narhi:
                    buy(symbol, price)
                    status = "🛒 Buy"

                print(
                    f"{symbol.ljust(10)} | Narx: {format_price(price).ljust(12)} | Farq: {diff:+.2f}$ | Status: {status}")

            print("=" * 80)
            await asyncio.sleep(sikl_aylanish_vaqti)
        except Exception:
            error_log(traceback.format_exc())

    log_console("🛑 Bot to‘xtatildi.")


# 🔹 Coinlarning joriy narxlarini olish uchun funksiya
def get_current_coin_prices():
    prices = get_prices(COINS)
    return prices
