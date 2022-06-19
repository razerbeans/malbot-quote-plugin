import datetime

from maubot import Plugin, MessageEvent
from maubot.handlers import command

from .db import QuoteDatabase

class QuoteBot(Plugin):
  db: QuoteDatabase

  async def start(self) -> None:
    self.db = QuoteDatabase(self.database)
  
  @command.new("quote", require_subcommand=False)
  async def quote(self, evt: MessageEvent) -> None:
    fetched_quote = self.db.get()
    await evt.reply(fetched_quote["message"])

  @quote.subcommand(help="Add a quote to the quote database")
  @command.argument("quote_body", pass_raw=True)
  async def add(self, evt: MessageEvent, quote_body: str) -> None:
    new_quote = self.db.add(submitter=evt.sender, message=quote_body, date=datetime.datetime.fromtimestamp(evt.timestamp / 1000))
    await evt.reply(f"Quote added!")
