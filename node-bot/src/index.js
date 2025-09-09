import 'dotenv/config'
import { Client, GatewayIntentBits, Partials, AttachmentBuilder } from 'discord.js'
import { createCanvas, loadImage } from '@napi-rs/canvas'
import fs from 'node:fs'
import path from 'node:path'
import {
  loadBufferAsImage,
  drawCircularAvatar,
  drawRing,
  drawDoubleRing,
  drawDottedRing,
  composeWithOverlay,
  parseColor,
} from './image.js'

const TOKEN = process.env.DISCORD_TOKEN
const PREFIX = process.env.COMMAND_PREFIX || '!'
if (!TOKEN) throw new Error('Defina DISCORD_TOKEN no .env')

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.DirectMessages,
  ],
  partials: [Partials.Channel],
})

client.once('ready', () => {
  console.log(`Logado como ${client.user.tag}`)
})

async function getImageBufferFromMessage(message) {
  if (message.attachments?.size) {
    for (const att of message.attachments.values()) {
      if (att.contentType?.startsWith('image/')) {
        const data = await fetch(att.url).then(r => r.arrayBuffer())
        return Buffer.from(data)
      }
    }
  }
  if (message.reference?.messageId) {
    try {
      const refMsg = await message.channel.messages.fetch(message.reference.messageId)
      if (refMsg.attachments?.size) {
        for (const att of refMsg.attachments.values()) {
          if (att.contentType?.startsWith('image/')) {
            const data = await fetch(att.url).then(r => r.arrayBuffer())
            return Buffer.from(data)
          }
        }
      }
    } catch {}
  }
  const avatarURL = message.author.displayAvatarURL({ size: 512, extension: 'png' })
  const data = await fetch(avatarURL).then(r => r.arrayBuffer())
  return Buffer.from(data)
}

client.on('messageCreate', async (message) => {
  if (message.author.bot) return
  if (!message.content.startsWith(PREFIX)) return

  const [cmd, sub, ...args] = message.content.slice(PREFIX.length).trim().split(/\s+/)
  if (cmd !== 'decorar') return

  try {
    await message.channel.sendTyping()
    const buffer = await getImageBufferFromMessage(message)
    const baseImg = await loadBufferAsImage(buffer)

    const size = 512
    const canvas = createCanvas(size, size)
    const ctx = canvas.getContext('2d')

    // Default draw avatar
    drawCircularAvatar(ctx, baseImg, 0, 0, size)

    let outCanvas = canvas

    switch ((sub || 'anel').toLowerCase()) {
      case 'anel': {
        const color = parseColor(args[0] || '#5865F2')
        drawRing(ctx, 0, 0, size, color, Math.max(4, Math.floor(size * 0.08)))
        break
      }
      case 'duplo': {
        const color = parseColor(args[0] || '#5865F2')
        drawDoubleRing(ctx, 0, 0, size, color, Math.max(3, Math.floor(size * 0.05)), Math.floor(size * 0.06))
        break
      }
      case 'pontilhado': {
        const color = parseColor(args[0] || '#5865F2')
        const count = Number.isInteger(Number(args[1])) ? Number(args[1]) : 48
        drawDottedRing(ctx, 0, 0, size, color, count, Math.max(2, Math.floor(size * 0.02)))
        break
      }
      case 'overlay': {
        const file = args[0]
        const scale = Math.max(0.5, Math.min(1.5, Number(args[1]) || 1.0))
        if (!file) {
          await message.reply('Informe o arquivo em assets/overlays. Ex.: !decorar overlay borboleta.png 1.0')
          return
        }
        const overlayPath = path.resolve(process.cwd(), 'assets', 'overlays', file)
        if (!fs.existsSync(overlayPath)) {
          await message.reply('Overlay não encontrado em assets/overlays')
          return
        }
        outCanvas = await composeWithOverlay(buffer, overlayPath, scale)
        break
      }
      default: {
        const color = parseColor(args[0] || '#5865F2')
        drawRing(ctx, 0, 0, size, color, Math.max(4, Math.floor(size * 0.08)))
        break
      }
    }

    const outBuffer = outCanvas.toBuffer('image/png')
    const attachment = new AttachmentBuilder(outBuffer, { name: 'decorated.png' })
    await message.reply({ files: [attachment] })
  } catch (e) {
    await message.reply('Erro ao processar imagem: ' + e.message)
  }
})

client.login(TOKEN)
