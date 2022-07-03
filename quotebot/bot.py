import datetime
import re

from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from typing import Type

from .db import QuoteDatabase


class Config(BaseProxyConfig):
  def do_update(self, helper: ConfigUpdateHelper) -> None:
    helper.copy_dict("permissions")


class QuoteBot(Plugin):
  db: QuoteDatabase

  async def start(self) -> None:
    self.db = QuoteDatabase(self.database)
    self.config.load_and_update()

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
    if self.is_authorized("delete", evt.sender):
      self.db.delete(int(quote_id))
      await evt.reply("Quote deleted!")
    else:
      await evt.reply("Get fucked")

  @quote.subcommand(help="Add many quotes in bulk")
  @command.argument("quotes", pass_raw=True)
  async def bulk_add(self, evt: MessageEvent, quotes: str) -> None:
    if self.is_authorized("delete", evt.sender):
      new_quotes = quotes.split("\n")
      for quote in new_quotes:
        self.db.add(date=(datetime.datetime.fromtimestamp(evt.timestamp / 1000)), message=quote, submitter=evt.sender)
      await evt.reply("All quotes have been added!")
    else:
      await evt.reply("No thanks.)")
  
  @quote.subcommand(help="Fetch the most recent quote from the quote database")
  async def last(self, evt: MessageEvent) -> None:
    fetched_quote = self.db.last()
    if fetched_quote:
      response = f"(#{fetched_quote['id']}) {fetched_quote['message']}"
    else:
      response = "The quote database is empty!"
    await evt.reply(response)

  @quote.subcommand(help="Find a quote containing the mentioned text")
  @command.argument("text", pass_raw=True)
  async def find(self, evt: MessageEvent, text: str) -> None:
    fetched_quote = self.db.find(text)
    if fetched_quote:
      response = f"(#{fetched_quote['id']}) {fetched_quote['message']}"
    else:
      response = "Quote not found."
    await evt.reply(response)

  @classmethod
  def get_config_class(cls) -> Type[BaseProxyConfig]:
    return Config

  def is_authorized(self, command, username):
    whitelist = self.config['permissions']['whitelist'][command]
    for whitelist_item in whitelist:
      if re.fullmatch(whitelist_item, username):
        return True
    return False