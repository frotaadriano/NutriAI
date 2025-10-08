# Design Guidelines – NutriAI (OpenAI Apps SDK)

Estas diretrizes seguem o padrão do [OpenAI Apps SDK Design Guidelines](https://developers.openai.com/apps-sdk/concepts/design-guidelines), adaptadas ao app **NutriAI**, que analisa alimentos descritos pelo usuário e gera estimativas nutricionais.

---

## 🎯 Propósito
Fornecer respostas **educativas e rápidas** sobre o conteúdo nutricional de alimentos descritos em linguagem natural, mantendo privacidade e simplicidade.

---

## 🧭 Pilares de Design

### 1. **Nativo do ChatGPT**
- Fale no mesmo tom do ChatGPT: direto, educativo e conciso.
- Evite jargão e termos promocionais.
- Estruture respostas em blocos curtos (tabelas, listas e frases breves).

### 2. **Clareza e Segurança**
- Explique limitações (“estimativa educativa; não substitui orientação médica”).
- Nunca colete dados pessoais.
- Políticas de privacidade e disclaimers visíveis.

### 3. **Desempenho e Estabilidade**
- Respostas em até 3 s.
- Componentes leves e responsivos.
- Trate erros e entradas vagas com mensagens educadas.

---

## 💬 Fluxo Conversacional

1. **Entrada**
   - “Descreva o alimento (ex.: ‘tapioca 2 colheres com queijo’).”

2. **Confirmação**
   - “Quer que eu use porção padrão de 100 g?”

3. **Resposta**
   - Tabela nutricional
   - Insights e observações
   - Dica de melhoria
   - Ações: *Comparar*, *Salvar*, *Ajustar porção*

4. **Follow-up**
   - “Quer ver alternativas mais saudáveis?”
   - “Deseja comparar com outro alimento?”

---

## 🧩 Componentes do Apps SDK

| Componente | Função | Observações |
|-------------|--------|-------------|
| `NutritionTable` | Exibe tabela de nutrientes | Responsiva, com markdown |
| `InsightChips` | Destaques visuais (ex.: “alto em sódio”) | Máx. 3 por resposta |
| `ActionsBar` | Botões: Comparar / Salvar / Ajustar | Use ícones compactos |
| `MotivationStrip` | Frase curta de apoio | Opcional, max 1 linha |

---

## ✍️ Estilo e Microcopy
- **Direto e empático:** “Aqui está a estimativa para sua tapioca.”
- **Evite imperativos:** prefira sugestões a ordens.
- **Não prometa precisão:** reforce que é estimativa.

---

## ⚠️ Tratamento de Erros

| Cenário | Resposta |
|----------|-----------|
| Entrada vaga | “Preciso da porção. Uso 100 g como padrão?” |
| Item incomum | “Poucos dados confiáveis; mostrando intervalo estimado.” |
| Falha técnica | “Não consegui gerar agora. Tente reformular (‘banana prata média’).” |

---

## 🔒 Privacidade
- Coleta mínima (texto do alimento apenas).
- Nenhum dado pessoal.
- Tokens seguros via variável de ambiente.
- Política de privacidade hospedada em `/docs/privacy.md`.

---

## ⚙️ Estrutura de Repositório

