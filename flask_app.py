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
#db.create_tables([Skribajxo, Uzanto])
#Skribajxo.create(enhavo='پنجره با صدای رعد باز شد و نور برق بر اتاق تابید.')

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
        chat = update["message"]["chat"]
        chat_id = chat["id"]
        skribajxo = Skribajxo.get()
        if m == '/g':
            bot.sendMessage(chat_id, skribajxo.enhavo)
        elif m == '/start':
            bot.sendMessage(170378225, u'یک گپ تازه با من شروع شد!')
            bot.sendMessage(chat_id, 'سلام.\n برای دریافت متن با آخرین تغییرات بزنید /g و متن را کپی کنید؛ حداکثر ۷ نویسه (حرف، فاصله و…) را تغییر دهید و بفرستید.')
        elif chat_id == 170378225 and  m == '/uzantoj':
            Uzantoj = Uzanto.select().order_by(Uzanto.id)
            uzantoj = ''
            for uzanto in Uzantoj:
                uzantoj += '>>> '+str(uzanto.tid)+': '+uzanto.nomo+':'+uzanto.familio+': @'+uzanto.uzantnomo+': '+str(uzanto.kontribuinta)+'\n'
            uzantoj += '---------\n'+str(Uzantoj.count())
            bot.sendMessage(170378225, uzantoj)
        else:
            try:
                uzanto = Uzanto.get(Uzanto.tid == chat_id)
            except Uzanto.DoesNotExist:
                try:
                    chat['username']
                except:
                    chat['username'] = ''
                try:
                    chat['first_name']
                except:
                    chat['first_name'] = ''
                try:
                    chat['last_name']
                except:
                    chat['last_name'] = ''
                uzanto = Uzanto.create(tid=chat['id'], uzantnomo=chat['username'], nomo=chat['first_name'], familio=chat['last_name'])
            if (datetime.datetime.now() - uzanto.lastaredakto).seconds >= datetime.timedelta(seconds=30).seconds:
                if ':\n' in m:
                    lasta_duponktoj = m.rindex(':\n')
                    m = m[lasta_duponktoj+2:]
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
                    uzanto.kontribuinta += diferenco_nombro
                    uzanto.save()
                    bot.sendMessage(chat_id, 'تغییرات با موفقیت انجام شد!')
                else:
                    bot.sendMessage(chat_id, 'حداکثر ۷ نویسه (حرف، فاصله و…) باید تغییر کند! دقت کنید که نام‌تان در ابتدای پیام ارسالی نباشد. ممکن است متنی که دارید قدیمی باشد. برای دریافت متن با آخرین تغییرات بزنید /g')
            else:
                bot.sendMessage(chat_id, '{} ثانیهٔ دیگر منتظر بمانید!'.format(persi(30-(datetime.datetime.now() - uzanto.lastaredakto).seconds)))
                    
    return "OK"
