# Comic Creator - Sistema de Gerenciamento de Mangás

Sistema completo para download e gerenciamento de mangás/quadrinhos seguindo Clean Architecture.

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <seu-repo>
cd comic_creator
```

### 2. Crie ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente (opcional)
```bash
export SECRET_KEY="sua-chave-secreta"
export BASE_COMICS="/caminho/customizado/Comics"
```

### 5. Execute a aplicação
```bash
python main.py
```

Acesse: http://localhost:5000

## 📁 Estrutura do Projeto
```
comic_creator/
├── src/
│   ├── domain/          # Entidades e regras de negócio
│   ├── application/     # Casos de uso
│   ├── infrastructure/  # Implementações técnicas
│   └── presentation/    # Controllers e rotas
├── config/              # Configurações
├── templates/           # Templates HTML
├── static/              # CSS, JS, imagens
└── main.py             # Entry point
```

## ✨ Funcionalidades

- ✅ Download de capítulos por URL
- ✅ Validação inteligente de imagens
- ✅ Geração automática de PDFs
- ✅ Thumbnails automáticos
- ✅ Biblioteca organizada
- ✅ Upload de capas personalizadas
- ✅ Exclusão de mangás/capítulos
- ✅ URLs predefinidas para download rápido

## 🏗️ Arquitetura

Projeto segue **Clean Architecture** com:

- **Domain Layer**: Entidades puras, sem dependências externas
- **Application Layer**: Casos de uso orquestrando a lógica
- **Infrastructure Layer**: Implementações de repositórios e services
- **Presentation Layer**: Controllers Flask

## 📝 Licença

MIT License