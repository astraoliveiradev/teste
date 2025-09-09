## Bot de Decoração de Avatar para Discord (Python)

Crie avatares decorados a partir de imagens enviadas no Discord (ou seu avatar), inspirado no site "Discord Fake Avatar Decorations" [`https://discord-decorations.vercel.app/`](https://discord-decorations.vercel.app/).

### Funcionalidades
- Comando `!decorar` lê a imagem anexada (ou a do autor) e aplica efeitos:
  - **anel**: borda circular colorida (ex.: `!decorar anel #ff00ff`)
  - **gradiente**: anel com gradiente estilizado
  - **glow**: brilho ao redor do avatar
  - **adesivo**: adiciona um adesivo vetorial simples (estrela/coração)
  - **perfil**: gera uma prévia de "cartão de perfil" com nome e bio

### Requisitos
- Python 3.10+
- Windows PowerShell/Terminal

### Instalação (Windows)
1. No diretório do projeto, crie e ative um ambiente virtual:
   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
3. Configure o token do bot:
   - Copie `.env.example` para `.env` e preencha `DISCORD_TOKEN` com o token do seu bot criado no Portal de Desenvolvedores do Discord.

### Executando
```powershell
py -m src.bot
```

### Uso no Discord
- Em um canal onde o bot está presente, envie:
  - `!decorar` (sem anexos): usa seu avatar atual
  - `!decorar anel #ff00ff` (com ou sem anexo): aplica um anel colorido
  - `!decorar gradiente`
  - `!decorar glow blue`
  - `!decorar adesivo estrela`
  - `!decorar perfil` (usa textos padrão para nome/bio)

Se houver uma imagem anexada na mensagem (ou na mensagem citada como resposta), ela terá prioridade.

### Observações
- Este projeto não é afiliado à Discord Inc. O uso é apenas educativo e pessoal.
- Inspirado por: [`https://discord-decorations.vercel.app/`](https://discord-decorations.vercel.app/)
