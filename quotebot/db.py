from sqlalchemy import (Column, String, Integer, Text, DateTime, ForeignKey, Table, MetaData,
                        select, and_, text)
from sqlalchemy.engine.base import Engine
from sqlalchemy.sql.expression import func, select

class QuoteDatabase:
  quotes: Table
  db: Engine

  def __init__(self, db: Engine) -> None:
    self.db = db
    self.tz_cache = {}
    self.locale_cache = {}

    meta = MetaData()
    meta.bind = db

    self.quotes = Table("quotes", meta,
                          Column("id", Integer, primary_key=True, autoincrement=True),
                          Column("date", DateTime, nullable=False),
                          Column("message", Text, nullable=False),
                          Column("submitter", String(255), nullable=False))

    meta.create_all()

  def get(self, quote_id=None):
    if quote_id:
      return self.db.execute(self.quotes.select().where(self.quotes.c.id == quote_id))
    else:
      return self.db.execute(self.quotes.select().order_by(func.random()).limit(1)).first()

  def add(self, date, message, submitter):
    self.db.execute(self.quotes.insert().values(date=date, message=message, submitter=submitter))

  def delete(self, quote_id):
    self.db.execute(self.quotes.delete().where(self.quotes.c.id == quote_id))

  def last(self):
    return self.db.execute(self.quotes.select().order_by(self.quotes.c.id.desc()).limit(1)).first()