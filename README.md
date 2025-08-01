# Comic Creator

**Comic Creator** é uma aplicação web em Flask que auxilia no download e na organização de capítulos de quadrinhos e mangás em formato PDF. O sistema mantém uma biblioteca simples, onde cada série possui sua própria pasta e capa opcional.

## O que a aplicação faz
- Permite baixar capítulos a partir de uma URL base.
- Guarda os capítulos em `~/Comics`, criando uma pasta para cada série.
- Gera miniaturas para visualização rápida dos capítulos.
- Possibilita excluir capítulos ou mangás completos pela interface.

---

## Configuração

1. Tenha o Python 3 instalado em sua máquina.
2. (Opcional) Crie e ative um ambiente virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

   Para executar os testes presentes na pasta `Tests`, é necessário instalar também o pacote `fpdf`.

---

## Variáveis de ambiente

- `SECRET_KEY` – chave usada pelo Flask para assinar sessões. Defina antes de iniciar o servidor:

  ```bash
  export SECRET_KEY="uma_string_secreta"
  ```

O diretório onde os mangás são salvos é `~/Comics` por padrão. Caso deseje alterar, modifique a variável `base_dir` em `app/__init__.py`.

---

## Executando a aplicação

Execute o servidor com o Flask CLI:

```bash
flask --app app run
```

Ou inicie diretamente pelo arquivo principal:

```bash
python main.py
```

O aplicativo ficará disponível em `http://localhost:5000`.

---

## Uso básico

### Baixar capítulos

1. Abra a página inicial.
2. Informe a URL base do mangá e a quantidade de capítulos.
3. Opcionalmente salve URLs para reutilizar depois.
4. Após o download, clique em **Acessar Biblioteca** para visualizar as séries salvas.

### Biblioteca

Na biblioteca cada mangá aparece como um cartão com sua capa (se houver). É possível abrir os capítulos, marcar como lidos, enviar uma nova capa ou remover arquivos.

```
Biblioteca
----------
[Capa] Nome do Mangá          [Ver capítulos]
[Capa] Outro Mangá            [Ver capítulos]
```

Este exemplo resume a aparência geral da página, servindo como referência quando não é possível visualizar capturas de tela.

