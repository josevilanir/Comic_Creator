# tasks/todo.md

## Concluído — Sessão 2026-02-28

- [x] Instalar Tailwind CSS v4 + @tailwindcss/vite no frontend
- [x] Navbar responsiva com hamburger menu (mobile-first)
- [x] Cards de URLs: layout em coluna, URL truncada, botão full-width
- [x] Grid da Biblioteca: grid-cols responsivo (2 → 5 colunas)
- [x] MangaCard: long press no mobile, hover no desktop, SVG icons
- [x] Fix Netlify: NODE_VERSION=22, `npm install` explícito no build command

## Backlog — Known Issues (CLAUDE.md)

- [ ] `pytest.ini` tem `testpaths = tests` (minúsculo) mas o diretório real é `Tests/` — corrigir o pytest.ini para evitar confusão
- [ ] Dois middlewares de auth duplicados (`src/presentation/decorators/auth_required.py` e `src/presentation/middlewares/auth_required.py`) — unificar em um único
- [ ] Rotas legadas `/api/*` (308 redirects em `app.py`) — remover após migração completa dos clientes para `/api/v1`
- [ ] `BaixarCapituloUseCase`: inline TODO sobre o padrão do parâmetro `user_id`
