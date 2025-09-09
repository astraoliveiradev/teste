import { createCanvas, loadImage } from '@napi-rs/canvas'

export async function loadBufferAsImage(buffer) {
  const img = await loadImage(buffer)
  return img
}

export function drawCircularAvatar(ctx, img, x, y, d) {
  const r = d / 2
  ctx.save()
  ctx.beginPath()
  ctx.arc(x + r, y + r, r, 0, Math.PI * 2)
  ctx.closePath()
  ctx.clip()
  ctx.drawImage(img, x, y, d, d)
  ctx.restore()
}

export function parseColor(value, fallback = '#5865F2') {
  if (!value) return fallback
  return value
}

export function drawRing(ctx, x, y, d, color, thickness) {
  const r = d / 2
  ctx.save()
  ctx.beginPath()
  ctx.arc(x + r, y + r, r - thickness / 2, 0, Math.PI * 2)
  ctx.strokeStyle = color
  ctx.lineWidth = thickness
  ctx.stroke()
  ctx.restore()
}

export function drawDoubleRing(ctx, x, y, d, color, thickness, gap) {
  const r = d / 2
  ctx.save()
  ctx.strokeStyle = color
  ctx.lineWidth = thickness
  ctx.beginPath()
  ctx.arc(x + r, y + r, r - thickness / 2, 0, Math.PI * 2)
  ctx.stroke()
  ctx.beginPath()
  ctx.arc(x + r, y + r, r - thickness / 2 - gap - thickness, 0, Math.PI * 2)
  ctx.stroke()
  ctx.restore()
}

export function drawDottedRing(ctx, x, y, d, color, count = 48, dotR = 2) {
  const cx = x + d / 2
  const cy = y + d / 2
  const radius = d / 2 - dotR - 1
  ctx.save()
  ctx.fillStyle = color
  for (let i = 0; i < count; i++) {
    const theta = (2 * Math.PI * i) / count
    const px = cx + Math.cos(theta) * radius
    const py = cy + Math.sin(theta) * radius
    ctx.beginPath()
    ctx.arc(px, py, dotR, 0, Math.PI * 2)
    ctx.fill()
  }
  ctx.restore()
}

export function estimateCenterRadiusFromOverlayAlpha(overlay, threshold = 10, padding = 2) {
  const w = overlay.width
  const h = overlay.height
  const cx = Math.floor(w / 2)
  const cy = Math.floor(h / 2)
  const data = overlay.getContext('2d').getImageData(0, 0, w, h).data
  function alphaAt(xx, yy) {
    const idx = (yy * w + xx) * 4 + 3
    return data[idx]
  }
  function scan(dx, dy) {
    let r = 0
    let x = cx
    let y = cy
    while (x >= 0 && x < w && y >= 0 && y < h) {
      if (alphaAt(x, y) > threshold) break
      r += 1
      x += dx
      y += dy
    }
    return Math.max(0, r - padding)
  }
  const up = scan(0, -1)
  const down = scan(0, 1)
  const left = scan(-1, 0)
  const right = scan(1, 0)
  const radius = Math.min(up, down, left, right)
  if (radius <= 0) return null
  return radius
}

export async function composeWithOverlay(avatarBuffer, overlayPath, scale = 1.0) {
  const overlay = await loadImage(overlayPath)
  const w = overlay.width
  const h = overlay.height
  const canvas = createCanvas(w, h)
  const ctx = canvas.getContext('2d')

  const avatar = await loadBufferAsImage(avatarBuffer)

  // Paint overlay to be able to read alpha
  ctx.clearRect(0, 0, w, h)
  ctx.drawImage(overlay, 0, 0)

  const radius = estimateCenterRadiusFromOverlayAlpha(canvas)
  let d
  if (radius == null) {
    d = Math.floor(Math.min(w, h) * 0.85 * Math.max(0.1, Math.min(2.0, scale)))
  } else {
    d = Math.floor(radius * 2 * Math.max(0.1, Math.min(2.0, scale)))
  }
  const x = Math.floor((w - d) / 2)
  const y = Math.floor((h - d) / 2)

  // Clear and draw
  ctx.clearRect(0, 0, w, h)
  drawCircularAvatar(ctx, avatar, x, y, d)
  ctx.drawImage(overlay, 0, 0)

  return canvas
}
