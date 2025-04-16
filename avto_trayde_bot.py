import time
import ccxt
import my_secrets as ms
from datetime import datetime

# Binance API ulanishi
exchange = ccxt.binance({
    'apiKey': ms.Api_klyuch,
    'secret': ms.Secret_klyuch,
    'enableRateLimit': True,
})

# Sozlamalar
CHECK_INTERVAL = 10  # tekshirish oralig‘i (soniya)
CHANGE_PERCENT = 0.5  # o'zgarish foizi
my_usdt_amount = 1  # siz istagancha USD lik savdo miqdori
avto = False
log_list_bot_wrtie = []

# Sotib olingan narxni saqlash
last_btc_buy_price = None
last_eth_buy_price = None


def format_price(price):
    return "{:,.2f}".format(price)


def calculate_change(current, previous):
    return ((current - previous) / previous) * 100


def get_current_prices():
    try:
        btc = exchange.fetch_ticker("BTC/USDT")['last']
        eth = exchange.fetch_ticker("ETH/USDT")['last']
        return btc, eth
    except Exception as e:
        print(f"❌ Narxlarni olishda xato: {e}")
        return None, None


def get_trade_amount(symbol, usdt_balance):
    ticker = exchange.fetch_ticker(symbol)
    price = ticker['last']
    amount = usdt_balance / price
    return round(amount, 6)


def log_trade(symbol, side, amount, price):
    total = amount * price
    log_list_bot_wrtie.append(
        f"{datetime.now()} | {side.upper()} | {symbol} | Amount: {amount:.6f} | Price: {price:.2f} | Total: {total:.2f} USDT")
    with open("trade_log.txt", "a") as log_file:
        log_file.write(
            f"{datetime.now()} | {side.upper()} | {symbol} | Amount: {amount:.6f} | Price: {price:.2f} | Total: {total:.2f} USDT\n")


def make_trade(symbol, side, amount):
    global last_btc_buy_price, last_eth_buy_price
    try:
        order = exchange.create_market_order(symbol, side, amount)
        current_price = exchange.fetch_ticker(symbol)['last']
        print(f"✅ {side.upper()} qilindi: {symbol} - {amount:.6f} @ {format_price(current_price)}")

        log_trade(symbol, side, amount, current_price)

        if side == "buy":
            if symbol == "BTC/USDT":
                last_btc_buy_price = current_price
                print(f"📊 Sotib olingan BTC narxi: {format_price(last_btc_buy_price)}")
            elif symbol == "ETH/USDT":
                last_eth_buy_price = current_price
                print(f"📊 Sotib olingan ETH narxi: {format_price(last_eth_buy_price)}")
    except Exception as e:
        print(f"❌ Savdo xatosi ({symbol} - {side}): {e}")


def automatik_Binance_Trade_Bot():
    print("🤖 Avtomatik Binance Trade Bot ishga tushdi")
    prev_btc, prev_eth = get_current_prices()

    if prev_btc is None or prev_eth is None:
        print("❌ Dastlabki narxlarni olishda xato. Dastur to‘xtatildi.")
        return

    print(f"📊 Boshlang‘ich narxlar | BTC: {format_price(prev_btc)} | ETH: {format_price(prev_eth)}")

    while avto:
        try:
            time.sleep(CHECK_INTERVAL)
            current_btc, current_eth = get_current_prices()
            if current_btc is None or current_eth is None:
                continue

            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n🕒 {current_time} | BTC: {format_price(current_btc)} | ETH: {format_price(current_eth)}")

            balance = exchange.fetch_balance()

            # BTC uchun
            if last_btc_buy_price is not None:
                btc_change = calculate_change(current_btc, last_btc_buy_price)
                if abs(btc_change) >= CHANGE_PERCENT:
                    print("BTC mos keldi")  # 🔔 Faqat shuni chiqaradi
                    if btc_change > 0:
                        btc_amount = balance['BTC']['free']
                        if btc_amount > 0.0001:
                            make_trade("BTC/USDT", "sell", btc_amount)
                    else:
                        if balance['USDT']['free'] > my_usdt_amount:
                            amount = get_trade_amount("BTC/USDT", my_usdt_amount)
                            make_trade("BTC/USDT", "buy", amount)

            # ETH uchun
            if last_eth_buy_price is not None:
                eth_change = calculate_change(current_eth, last_eth_buy_price)
                if abs(eth_change) >= CHANGE_PERCENT:
                    print("ETH mos keldi")  # 🔔 Faqat shuni chiqaradi
                    if eth_change > 0:
                        eth_amount = balance['ETH']['free']
                        if eth_amount > 0.001:
                            make_trade("ETH/USDT", "sell", eth_amount)
                    else:
                        if balance['USDT']['free'] > my_usdt_amount:
                            amount = get_trade_amount("ETH/USDT", my_usdt_amount)
                            make_trade("ETH/USDT", "buy", amount)

            prev_btc, prev_eth = current_btc, current_eth

        except KeyboardInterrupt:
            print("\n\n\n🛑 Dastur to‘xtatildi")
            break
        except Exception as e:
            print(f"⚠️ Xato: {e} | 30 soniya kutamiz...")
            time.sleep(30)

    print("\n\n🛑 Avto trading to‘xtatildi !\n\n")
