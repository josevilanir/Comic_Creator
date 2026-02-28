# tasks/lessons.md

Lições aprendidas em ordem cronológica inversa. Cada entrada tem contexto e regra acionável.

---

## 2026-02-28

### 1. Tailwind v4 + Netlify: native binding do `@tailwindcss/oxide`

**Contexto**: Build no Netlify falhava com erro de módulo nativo (`@tailwindcss/oxide`) porque o `NODE_VERSION` no ambiente de CI diferia da versão usada localmente ao instalar as dependências do lockfile.

**Regra**: Ao usar Tailwind v4 (ou qualquer pacote com bindings nativos), garantir que `NODE_VERSION` no `netlify.toml` bata com a versão de desenvolvimento. Incluir `npm install` explícito no `command` do build — não confiar apenas no cache do Netlify.

```toml
[build]
  command = "npm install && npm run build"
  [build.environment]
    NODE_VERSION = "22"
```

---

### 2. Long press + synthetic click no mobile

**Contexto**: Implementação do menu de ações via long press no `MangaCard`. O mobile dispara um evento `click` sintético ~300ms após o `touchend`, o que fazia o menu abrir e fechar imediatamente na mesma interação.

**Regra**: Usar uma ref `didLongPress` que é setada para `true` quando o long press é ativado e reseta no próximo `click`. O handler de `click` deve verificar e "engolir" o evento se `didLongPress.current === true`.

```js
const didLongPress = useRef(false);

// no touchend / long press callback:
didLongPress.current = true;
setMenuVisible(true);

// no onClick:
if (didLongPress.current) {
  didLongPress.current = false;
  return; // swallow synthetic click
}
```

---

### 3. Detecção de touch device: `matchMedia` vs user-agent

**Contexto**: Precisávamos distinguir desktop (hover) de mobile (long press) no `MangaCard`. User-agent sniffing é frágil e sujeito a falsos positivos.

**Regra**: Usar `window.matchMedia('(hover: none) and (pointer: coarse)')` — detecta capacidade real do dispositivo, não string de UA. Encapsular em hook `useIsTouchDevice` para reutilização.

```js
export function useIsTouchDevice() {
  return useMemo(
    () => window.matchMedia('(hover: none) and (pointer: coarse)').matches,
    []
  );
}
```

---

### 4. Plan mode é obrigatório para tarefas com 3+ arquivos ou decisões arquiteturais

**Contexto**: A sessão inteira (Tailwind, responsividade, long press, Netlify) foi implementada sem plan mode, sem `tasks/todo.md` e sem `tasks/lessons.md` — contrariando o CLAUDE.md.

**Regra**: Sempre entrar em plan mode quando a tarefa envolve 3+ arquivos ou uma decisão arquitetural. Escrever o plano em `tasks/todo.md` antes de implementar. Isso permite elegance check, alinha expectativas com o usuário e preserva o contexto principal.

Sinais de que plan mode é necessário:
- Tarefa toca mais de 2 arquivos
- Há pelo menos uma decisão de design (biblioteca, padrão, estrutura)
- A tarefa inclui mudanças no ambiente de build ou CI
