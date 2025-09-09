# Bot de Decoração de Avatar (Node.js)

Versão Node.js do bot com efeitos e sobreposições PNG. Inspirado em `discord-fake-avatar-decorations` [`https://github.com/ItsPi3141/discord-fake-avatar-decorations.git`](https://github.com/ItsPi3141/discord-fake-avatar-decorations.git) e no site [`https://discord-decorations.vercel.app/`](https://discord-decorations.vercel.app/).

## Requisitos
- Node.js 18+

## Instalação
```powershell
cd node-bot
npm install
copy env.example .env
notepad .env
```
Preencha `DISCORD_TOKEN`.

## Execução
```powershell
npm start
```

## Pasta de assets
- Crie `assets/overlays/` e coloque arquivos PNG (ex.: `borboleta.png`).
- O bot estima automaticamente o raio seguro pelo alpha do overlay para não ultrapassar a decoração.

## Uso
- `!decorar anel #ff00ff`
- `!decorar duplo #ff9900`
- `!decorar pontilhado #00ffcc 64`
- `!decorar overlay borboleta.png 1.0`

## Créditos
- Base de ideias e assets: [`https://github.com/ItsPi3141/discord-fake-avatar-decorations.git`](https://github.com/ItsPi3141/discord-fake-avatar-decorations.git)
- Website de referência: [`https://discord-decorations.vercel.app/`](https://discord-decorations.vercel.app/)
