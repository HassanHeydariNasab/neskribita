import os
import urllib3
import datetime
import telepot
from flask import Flask, request
from simplediff import diff
from modeloj import db, Skribajxo, Uzanto
from peewee import *

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

secret = "8246"
o = open(os.path.join('/home/hsn6/token'))
t = o.read()
TOKEN = t[:-1]
o.close()
bot = telepot.Bot(TOKEN)
bot.setWebhook("https://hsn6.pythonanywhere.com/{}".format(secret), max_connections=10, allowed_updates='message')

app = Flask(__name__)

#db.connect()
db.create_tables([Skribajxo, Uzanto])
Skribajxo.create(enhavo='پنجره با صدای رعد باز شد و نور برق بر اتاق تابید.')

'''
@app.before_request
def _db_connect():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()
'''
def persi(n):
    return str(n).replace('0', '۰').replace('1', '۱').replace('2', '۲').replace('3', '۳').replace('4', '۴').replace('5', '۵').replace('6', '۶').replace('7', '۷').replace('8', '۸').replace('9', '۹')

@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        m = update["message"]["text"]
        #ms = m.split(' ')
        chat_id = update["message"]["chat"]["id"]
        try:
            uzanto = Uzanto.get(Uzanto.tid == chat_id)
        except Uzanto.DoesNotExist:
            uzanto = Uzanto.create(tid=chat_id)
        skribajxo = Skribajxo.get()
        if m == '/start':
            bot.sendMessage(chat_id, 'سلام.\n برای دریافت متن با آخرین تغییرات بزنید /g و متن را کپی کنید؛ حداکثر ۷ نویسه را تغییر دهید و بفرستید.')
        elif m == '/g':
            bot.sendMessage(chat_id, skribajxo.enhavo)
        else:
            if (datetime.datetime.now() - uzanto.lastaredakto).seconds >= datetime.timedelta(seconds=30).seconds:
                diferencoj = diff(skribajxo.enhavo, m)
                diferenco_nombro = 0
                for diferenco in diferencoj:
                    if diferenco[0] != '=':
                        diferenco_nombro += len(diferenco[1])
                #bot.sendMessage(chat_id, str(diferenco_nombro)+'\n'+str(diferencoj))
                if diferenco_nombro < 8:
                    skribajxo.enhavo = m
                    skribajxo.save()
                    uzanto.lastaredakto = datetime.datetime.now()
                    uzanto.save()
                    bot.sendMessage(chat_id, 'تغییرات با موفقیت انجام شد!')
                else:
                    bot.sendMessage(chat_id, 'حداکثر ۷ نویسه باید تغییر کند! ممکن است متنی که دارید قدیمی باشد. برای دریافت متن با آخرین تغییرات بزنید /g')
            else:
                bot.sendMessage(chat_id, '{} ثانیهٔ دیگر منتظر بمانید!'.format(persi(30-(datetime.datetime.now() - uzanto.lastaredakto).seconds)))
                    
    return "OK"
