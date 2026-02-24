# 📖 Comic Creator

**Comic Creator** é uma solução completa para download, organização e leitura de mangás e quadrinhos. Com um backend robusto em Python e um frontend moderno em React, você pode gerenciar sua coleção local com facilidade.

## 🚀 Guia Rápido de Instalação

### Pré-requisitos
- **Python 3.10+**
- **Node.js 18+** e npm

---

### 1. Preparar o Backend
Na raiz do projeto:
```bash
# Criar e ativar ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor (Porta 5000)
python main.py
```

### 2. Preparar o Frontend
Em um novo terminal, entre na pasta `frontend`:
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar em modo desenvolvimento
npm run dev
```
O frontend ficará disponível em `http://localhost:5173`.

---

## 🛠️ Como usar

1.  **Downloads**: Cole a URL base do capítulo de um mangá compatível. Você pode baixar um capítulo único ou um intervalo (ex: cap 1 ao 50).
2.  **Biblioteca**: Veja todos os seus mangás baixados. Cada um tem sua capa e lista de capítulos.
3.  **Leitor**: Clique em um capítulo para abrir o leitor integrado.
4.  **Gerenciamento**: Você pode trocar a capa de qualquer mangá fazendo o upload de uma imagem local e excluir títulos indesejados.

---

## 📂 Organização de Arquivos
- **Caminho padrão**: Os mangás são salvos em `~/Comics` (na sua pasta de usuário).
- **Estrutura**: Cada mangá tem sua própria pasta contendo os capítulos em formato PDF.
- **Configurações**: Para mudar o local de salvamento ou outras opções, veja `config/settings.py`.

---

## 🧪 Testes
Para garantir a estabilidade do sistema, você pode rodar a suíte de testes:
```bash
# Backend
pytest

# Ou use os scripts automatizados
./run_tests.sh
```

---
*Desenvolvido seguindo os padrões de Clean Architecture e as boas práticas da Imersão42.*
