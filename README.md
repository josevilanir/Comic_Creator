# Comic Creator

**Comic Creator** é uma aplicação web full-stack para download e organização de mangás em PDF.

- **Backend**: Flask + SQLite  
- **Frontend**: React + Vite
- **Funcionalidades**: Downloads via URL, biblioteca visual, marcar lidos, gerenciar séries

---

## Setup Rápido

### 1. Dependências do Backend
```bash
python -m pip install -r requirements.txt
```

### 2. Dependências do Frontend
```bash
cd frontend && npm install
```

---

## Rodando a Aplicação

### Backend (Flask)
```bash
python main.py
```
Acessa: `http://localhost:5000`

### Frontend (React + Vite)
```bash
cd frontend && npm run dev
```
Acessa: `http://localhost:5173`

---

## Testes

```bash
python -m pytest Tests/ -q
```

---

## Estrutura

```
backend/               # API Flask
├── comic_creator/    # Módulo principal
│   ├── __init__.py
│   ├── routes.py
│   ├── downloader.py
│   ├── db.py
│   ├── config.py
│   └── utils.py
├── config.py
└── db.py

frontend/              # Cliente React
├── src/
├── package.json
└── vite.config.js

Tests/                 # Testes unitários
└── test_routes.py
```

---

## Configuração

O diretório padrão de mangás é `~/Comics`. Para alterar, edite em `backend/comic_creator/config.py`:

```python
BASE_COMICS = '/seu/caminho/aqui'
```

---

## Funcionalidades

✅ Download de capítulos por URL  
✅ Biblioteca visual com covers  
✅ Marcar capítulos como lido  
✅ Deletar capítulos/séries  
✅ API REST para frontend  
✅ Geração automática de thumbnails  
