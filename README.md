# Comic Creator

**Comic Creator** é uma aplicação desenvolvida em Python que permite aos usuários criarem histórias em quadrinhos personalizadas de forma simples e intuitiva.

## O que a aplicação faz
- Permite a criação de histórias com múltiplos quadros.
- Oferece layouts paersonalizáveis para organização dos elementos visuais.
- Possibilita a exportação das histórias em formatos de imagem populares.

A interface é projetada para ser amigável, oferecendo uma experiência criativa e divertida para a criação de histórias.

## Configuração

Algumas opções de execução podem ser definidas por variáveis de ambiente:

- `SECRET_KEY` – chave de segurança utilizada pelo Flask.
- `BASE_COMICS` – pasta onde os capítulos serão armazenados. Por padrão `~/Comics`.
- `THUMBNAIL_DIR` – diretório para as miniaturas geradas, padrão `static/thumbnails`.

Defina essas variáveis antes de iniciar a aplicação caso queira personalizar os caminhos.
