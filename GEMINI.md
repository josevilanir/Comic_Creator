# Guia de Boas Práticas — Imersão42 2025

Este arquivo define as boas práticas e padrões arquiteturais que devem ser seguidos em todos os projetos fullstack. Sempre aplique estas diretrizes ao sugerir, revisar ou gerar código.

---

## 1. Componentização (Frontend)

- Divida a interface em componentes pequenos, reutilizáveis e com responsabilidade única.
- Evite "God Components" — componentes grandes que fazem tudo.
- Componentes base (Button, Input, Card) devem ser reutilizados em todo o projeto.
- Componentes devem ser previsíveis e fáceis de testar.
- Prefira composição de componentes menores para formar os maiores.

## 2. Separação de Responsabilidades

- **Frontend:** separe UI, lógica e acesso a dados em camadas distintas.
- **Backend:** separe Controller, Service/UseCase e Repository.
- Componentes de UI não devem conhecer regras de negócio.
- Cada camada do sistema deve ter uma função clara e isolada.

## 3. Modelagem de Banco de Dados

- Modele o banco antes de escrever qualquer código.
- Identifique entidades, atributos e relacionamentos com clareza.
- Use chaves primárias e estrangeiras corretamente.
- Normalize os dados — evite duplicação.
- A modelagem deve refletir as regras reais do negócio.

## 4. Migrations

- Use migrations para versionar a evolução do banco de dados.
- Nunca altere migrations já aplicadas em produção.
- Crie uma migration por mudança relevante.
- Migrations facilitam trabalho em equipe e rollback de alterações.

## 5. Design de APIs

- A API é um contrato claro e previsível — trate-a como tal.
- Use verbos HTTP corretamente: GET, POST, PUT, DELETE.
- Use substantivos no plural nos endpoints (ex: `/users`, `/products`).
- Padronize respostas e erros em toda a API.
- Versione a API desde o início: `/api/v1`.

## 6. Arquitetura Backend em Camadas

```
Request → Controller → Service/UseCase → Repository → Banco
```

- **Controller:** recebe a request e retorna a response.
- **Service/UseCase:** contém a regra de negócio.
- **Repository:** responsável pelo acesso ao banco de dados.
- **Entidades:** representam o domínio do sistema.
- Código desacoplado facilita testes e refatoração.

## 7. Autenticação no Backend

- Use JWT para autenticação stateless.
- O token deve conter apenas informações essenciais.
- Middlewares validam o token e controlam o acesso.
- Diferencie autenticação (quem é) de autorização (o que pode fazer).

## 8. Autenticação no Frontend

- Use Context API para gerenciar o estado global de autenticação.
- Encapsule a lógica de auth em hooks personalizados.
- A UI deve reagir automaticamente ao estado autenticado/deslogado.
- Proteja rotas sensíveis com rotas privadas.

## 9. Data Fetching no Frontend

- Separe as chamadas de API da lógica de UI.
- Use custom hooks para buscar e gerenciar dados.
- Trate sempre os três estados: `loading`, `error` e `success`.
- Cancele requisições quando o componente for desmontado.
- Evite duplicação de lógica de fetch.

## 10. Error Handling

- Trate erros de forma centralizada.
- Nunca exponha erros internos ao usuário final.
- Mensagens de erro devem ser claras e amigáveis.
- O frontend deve reagir corretamente a falhas da API.
- Use logs para debug e monitoramento no backend.

## 11. Código Limpo

- Escreva funções pequenas com nomes claros e descritivos.
- Evite duplicação de código — abstraia quando necessário.
- Prefira early returns para reduzir aninhamento.
- Código deve ser legível antes de ser "inteligente".
- Menos complexidade = menos bugs.

## 12. Background Jobs

- Tarefas pesadas não devem rodar dentro do ciclo request/response.
- Use filas para processamento assíncrono (ex: BullMQ + Redis).
- Workers executam tarefas em segundo plano.
- Ideal para: envio de emails, limpeza de dados, processamento pesado.

## 13. Organização por Domínio

- Agrupe arquivos por contexto de negócio, não por tipo técnico.
- Evite pastas genéricas demais (ex: não coloque tudo em `/utils`).
- Cada domínio possui seus próprios serviços, repositórios e regras.
- Facilita entendimento, manutenção e escalabilidade.

## 14. Estrutura de Projeto

- A estrutura do projeto é uma decisão arquitetural importante.
- Uma boa estrutura orienta novos desenvolvedores naturalmente.
- Mantenha padrão entre projetos diferentes sempre que possível.
- A estrutura serve como base reutilizável para novos sistemas.

---

## Instruções para o Gemini

Ao trabalhar neste projeto, **sempre**:

1. Siga as boas práticas descritas acima ao gerar ou revisar código.
2. Sinalize quando alguma sugestão violar um dos princípios acima.
3. Prefira soluções simples, legíveis e bem separadas por responsabilidade.
4. Ao criar APIs, sempre versione e padronize respostas.
5. Ao criar componentes frontend, sempre pense em reutilização e separação de UI/lógica.
