import datetime

from maubot import Plugin, MessageEvent
from maubot.handlers import command

from .db import QuoteDatabase

class QuoteBot(Plugin):
  db: QuoteDatabase

  async def start(self) -> None:
    self.db = QuoteDatabase(self.database)

  @command.new("quote", aliases=["q"], require_subcommand=False)
  async def quote(self, evt: MessageEvent) -> None:
    fetched_quote = self.db.get()
    if fetched_quote:
      response = f"(#{fetched_quote['id']}) {fetched_quote['message']}"
    else:
      response = "The quote database is empty!"
    await evt.reply(response)

  @quote.subcommand(help="Add a quote to the quote database")
  @command.argument("quote_body", pass_raw=True)
  async def add(self, evt: MessageEvent, quote_body: str) -> None:
    new_quote = self.db.add(submitter=evt.sender, message=quote_body, date=datetime.datetime.fromtimestamp(evt.timestamp / 1000))
    await evt.reply(f"Quote added!")

  @quote.subcommand(help="Delete a specific quote by ID")
  @command.argument("quote_id")
  async def delete(self, evt: MessageEvent, quote_id: str) -> None:
    if evt.sender == "@razerbeans:matrix.gigafloppy.com":
      self.db.delete(int(quote_id))
      await evt.reply("Quote deleted!")
    else:
      await evt.reply("Get fucked")

  @quote.subcommand(help="Add many quotes in bulk")
  @command.argument("quotes", pass_raw=True)
  async def bulk_add(self, evt: MessageEvent, quotes: str) -> None:
    if evt.sender == "@razerbeans:matrix.gigafloppy.com":
      new_quotes = quotes.split("\n")
      for quote in new_quotes:
        self.db.add(date=(datetime.datetime.fromtimestamp(evt.timestamp / 1000)), message=quote, submitter=evt.sender)
      await evt.reply("All quotes have been added!")
    else:
      await evt.reply("No thanks.)")