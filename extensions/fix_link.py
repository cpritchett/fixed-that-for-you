"""
Fix message links
"""
import asyncio
from typing import Union
from datetime import datetime, timedelta
import tldextract
from interactions import (
    BrandColors,
    Button,
    ButtonStyle,
    ContextMenuContext,
    Embed,
    Extension,
    check,
    listen,
    Member,
    Message,
    MessageFlags,
    message_context_menu,
    slash_command,
    User,
    Permissions
)
from interactions.api.events import MessageCreate
from src import logutil, linkparser

logger = logutil.init_logger(__name__)

class FixLink(Extension):
  async def is_a_bot(self, author: Union[Member, User]) -> bool:
    return author.bot

  async def not_a_bot(ctx: ContextMenuContext) -> bool:
    result = not ctx.target.author.bot
    return result

  def is_apple_stocks_url(self, url: str) -> bool:
    """Check if a URL is an Apple Stocks link"""
    try:
      extracted_url = tldextract.extract(url)
      return (extracted_url.registered_domain == 'apple.com' and 
              extracted_url.subdomain == 'stocks')
    except Exception:
      return False

  async def handle_apple_stocks_timeout(self, message: Message):
    """Optional feature: timeout users who post Apple Stocks links"""
    try:
      # Only attempt timeout if the message is in a guild (not DM)
      if message.guild is None:
        return
      
      # Check if the bot has timeout permissions
      bot_member = await message.guild.fetch_member(message._client.user.id)
      if not bot_member.guild_permissions.MODERATE_MEMBERS:
        logger.info("Bot lacks MODERATE_MEMBERS permission for Apple Stocks timeout")
        return
      
      # Check if the message author is a Member (not just User) and can be timed out
      if isinstance(message.author, Member) and not message.author.guild_permissions.ADMINISTRATOR:
        # Timeout for 5 minutes (300 seconds)
        timeout_until = datetime.now() + timedelta(minutes=5)
        
        await message.author.timeout(
          timeout_until,
          reason="Posted Apple Stocks link - automatic timeout"
        )
        
        # Send a message about the timeout
        await message.channel.send(
          f"⏰ {message.author.mention} has been timed out for 5 minutes for posting Apple Stocks links.",
          silent=True,
          flags=MessageFlags.SILENT
        )
        
        logger.info(f"Applied 5-minute timeout to {message.author} for Apple Stocks link")
      
    except Exception as e:
      # Silently fail - timeout is optional feature
      logger.debug(f"Could not apply Apple Stocks timeout: {e}")
      pass

  close_button = Button(
                  label="Close",
                  custom_id="close_msg",
                  style=ButtonStyle.GREY
                )

  async def get_new_links(self, embeds: list[Embed]):
    url_list = []

    # Iterate through embeds in the original message and try to fix the links
    for embed in embeds:
      new_url = linkparser.LinkParser(embed.url).fix()
      if new_url is not None:
        url_list.append(new_url)
    return url_list
  
  async def no_link_found(self, ctx:ContextMenuContext):
      await ctx.send(
          content="",
          ephemeral=True,
          embed=Embed(
              description="No valid link was found in the selected message!",
              color=BrandColors.YELLOW
          ),
          components=[
            self.close_button
          ]
      )

  @listen(MessageCreate)
  async def on_message_create(self, event: MessageCreate):
    not_a_bot = not await self.is_a_bot(event.message.author)
    if (not_a_bot):
      await asyncio.sleep(2) # This is required because the original embed isn't always instantly available
      message: Message = event.message
      
      # Check for Apple Stocks links in embeds and message content for timeout (optional feature)
      has_apple_stocks = False
      
      # Check embeds for Apple Stocks links
      if len(message.embeds) > 0:
        for embed in message.embeds:
          if embed.url and self.is_apple_stocks_url(embed.url):
            has_apple_stocks = True
            break
      
      # Also check message content for Apple Stocks links (in case no embeds)
      if not has_apple_stocks and message.content:
        import re
        # Simple regex to find URLs in message content
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, message.content)
        for url in urls:
          if self.is_apple_stocks_url(url):
            has_apple_stocks = True
            break
      
      # Apply timeout for Apple Stocks links regardless of whether they're fixed
      if has_apple_stocks:
        await self.handle_apple_stocks_timeout(message)
      
      # If there are embeds in the original message try to fix the links
      if len(message.embeds) > 0:
        new_links = await self.get_new_links(message.embeds)
        new_links_list = "\n".join([i for i in new_links])

        # If any links were fixed, return them in a new message
        if len(new_links_list) > 0:
          await message.channel.send(
            content=new_links_list,
            silent=True,
            flags=MessageFlags.SILENT
          )
          return

  @check(check=not_a_bot)
  @message_context_menu(name="View Fixed Links")
  async def fix_links(self, ctx: ContextMenuContext):
      message: Message = ctx.target
      # If there are embeds in the original message try to fix the links
      if len(message.embeds) > 0:
        new_links = await self.get_new_links(message.embeds)
        new_links_list = "\n".join([i for i in new_links])

        # If any links were fixed, return them in a new message
        if len(new_links_list) > 0:
          await ctx.send(
            content=new_links_list,
            silent=True,
          )
          return
      # Else, fallback to "no valid link found" message
      await self.no_link_found(ctx)

  @slash_command(name="help")
  async def help(self, ctx: ContextMenuContext):
      await ctx.send(
          content='Right-click/long-press a message with a social media or news link, \
go to "Apps", then click "View Fixed Links".',
          ephemeral=True,
          components=[
            self.close_button
          ]
      )