from datetime import datetime
from peewee import (SqliteDatabase,
                    Model,
                    CharField,
                    IntegerField,
                    DateTimeField)

db: SqliteDatabase = SqliteDatabase('database/my_data.db')


class BaseModel(Model):
    class Meta:
        database: SqliteDatabase = db


class User(BaseModel):
    name: CharField = CharField()
    telegram_id: IntegerField = IntegerField()
    date: DateTimeField = DateTimeField(default=datetime.now)
    city: CharField = CharField()
    check_in: CharField = CharField()
    check_out: CharField = CharField()
    hotel: CharField = CharField()
    link: CharField = CharField()




