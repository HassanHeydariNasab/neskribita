import os
import datetime
from peewee import *

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
db = SqliteDatabase('/home/hsn6/datumaro.db')
#db = SqliteDatabase(':memory:')

class Skribajxo(Model):
    enhavo = CharField(default='')
    class Meta:
        database = db

class Uzanto(Model):
    tid = IntegerField()
    nomo = CharField(default='')
    familio = CharField(default='')
    uzantnomo = CharField(default='')
    kontribuinta = IntegerField(default=0)
    lastaredakto = DateTimeField(default=datetime.datetime.now()-datetime.timedelta(seconds=30))
    class Meta:
        database = db
