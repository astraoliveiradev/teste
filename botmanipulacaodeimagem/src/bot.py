import asyncio
import os
from typing import Optional

import discord
from discord.ext import commands
from PIL import Image
from dotenv import load_dotenv

from .image_utils import read_image_from_bytes, save_image_to_bytes
from .decorations import apply_ring, apply_gradient_ring, apply_glow, add_sticker, compose_profile_preview


load_dotenv()

COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)


async def _get_image_bytes_from_context(ctx: commands.Context) -> Optional[bytes]:
    # Priority: current message attachments -> referenced message attachments -> author's avatar
    if ctx.message.attachments:
        for att in ctx.message.attachments:
            if att.content_type and att.content_type.startswith("image/"):
                return await att.read()

    if ctx.message.reference:
        try:
            ref = ctx.message.reference
            ref_msg = ref.resolved if isinstance(ref.resolved, discord.Message) else await ctx.channel.fetch_message(ref.message_id)
            for att in ref_msg.attachments:
                if att.content_type and att.content_type.startswith("image/"):
                    return await att.read()
        except Exception:
            pass

    # Fallback: author's avatar
    return await ctx.author.display_avatar.read()


@bot.command(name="decorar")
async def decorar(ctx: commands.Context, subcomando: str = "anel", *args: str):
    """
    Usa a imagem anexada (ou avatar do autor) e aplica decorações.

    Exemplos:
    - !decorar
    - !decorar anel #ff00ff
    - !decorar gradiente #5865f2 #00d4ff
    - !decorar glow blue
    - !decorar adesivo estrela
    - !decorar perfil
    """
    await ctx.trigger_typing()

    try:
        img_bytes = await _get_image_bytes_from_context(ctx)
        if not img_bytes:
            return await ctx.reply("Não encontrei imagem ou avatar para processar.")

        image = read_image_from_bytes(img_bytes)
        sub = (subcomando or "anel").lower()

        if sub == "anel":
            color = args[0] if args else "#5865F2"
            out = apply_ring(image, color)
        elif sub == "gradiente" or sub == "gradiente2":
            c1 = args[0] if len(args) > 0 else "#5865F2"
            c2 = args[1] if len(args) > 1 else "#00d4ff"
            out = apply_gradient_ring(image, (c1, c2))
        elif sub == "glow":
            color = args[0] if args else "#5865F2"
            out = apply_glow(image, color)
        elif sub == "adesivo" or sub == "sticker":
            name = args[0] if args else "estrela"
            out = add_sticker(image, name)
        elif sub == "perfil" or sub == "profile":
            display_name = ctx.author.display_name
            out = compose_profile_preview(image, display_name=display_name)
        else:
            return await ctx.reply("Subcomando inválido. Use: anel | gradiente | glow | adesivo | perfil")

        buf = save_image_to_bytes(out, format="PNG")
        file = discord.File(buf, filename="decorated.png")
        await ctx.reply(file=file)
    except Exception as e:
        await ctx.reply(f"Ocorreu um erro ao processar a imagem: {e}")


@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    lines = [
        f"Prefixo: {COMMAND_PREFIX}",
        "Comandos:",
        f"{COMMAND_PREFIX}decorar [anel|gradiente|glow|adesivo|perfil] [opções]",
        f"Ex.: {COMMAND_PREFIX}decorar anel #ff00ff",
    ]
    await ctx.reply("\n".join(lines))


def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Defina DISCORD_TOKEN no ambiente (.env)")
    bot.run(token)


if __name__ == "__main__":
    main()
