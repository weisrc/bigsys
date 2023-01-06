import re
import discord
from typing import Tuple, Dict

MENTION_RE = re.compile(r'<@!?(\d{18})>')
CTX_TYPE = Dict[str, int]

def normalize(msg: str, client: discord.Client) -> Tuple[str, CTX_TYPE]:
  ctx = dict()
  def replace_mention(match: re.Match) -> str:
    id = int(match.group(1))
    user = client.get_user(id)
    if user:
      name = user.name
      ctx[name] = id
      return name
    return "someone"
  return MENTION_RE.sub(replace_mention, msg), ctx


def denormalize(msg: str, ctx: CTX_TYPE) -> str:
  for name, id in ctx.items():
    msg = msg.replace(name, f'<@{id}>')
  return msg
