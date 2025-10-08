# 🥗 NutriAI  
**App experimental de análise nutricional com OpenAI Apps SDK**---

## 🤖 **Integração com ChatGPT Apps SDK**

O NutriAI implementa o **protocolo MCP (Model Context Protocol)** e está pronto para ser usado como um conector personalizado no ChatGPT!

### **Como conectar ao ChatGPT:**

1. **Acesse:** [ChatGPT Settings → Connectors](https://chatgpt.com/#settings/Connectors)
2. **Clique em:** "New Connector" 
3. **Configure:**
   - **Name:** `NutriAI`
   - **Description:** `Analisa alimentos descritos em texto e retorna tabela nutricional completa`
   - **MCP Server URL:** `https://nutriai-mcp-server.onrender.com`
   - **Authentication:** `No authentication`
4. **Marque:** "I trust this application" ✓
5. **Clique:** "Create"

### **Como usar no ChatGPT:**
Após conectar, você pode usar comandos como:
- *"Analise uma banana prata de 86g"*
- *"Quantas calorias tem uma tapioca com queijo?"* 
- *"Me dê informações nutricionais de um pão francês com manteiga"*

O ChatGPT automaticamente descobrirá e usará sua ferramenta NutriAI! 🎉

---

## 🧠 Como funciona

**Fluxo de funcionamento:**

1. **ChatGPT Apps SDK** → Detecta intenção nutricional do usuário
2. **Protocolo MCP** → Chama a tool `analyze_food` via JSON-RPC 2.0  
3. **NutriAI Server** → Processa descrição do alimento
4. **OpenAI API** → Gera estimativa nutricional usando GPT-4o-mini
5. **ChatGPT** → Exibe resultado formatado com insights personalizados

**Arquitetura técnica:**
- **Frontend:** React com Vite (para desenvolvimento local)
- **Backend:** FastAPI com protocolo MCP + rate limiting + monitoramento de custos
- **IA:** OpenAI GPT-4o-mini com JSON mode para consistência
- **Deploy:** Render.com com HTTPS automático
- **Segurança:** CORS restrito + API keys opcionais + rate limitingenAI Apps SDK](https://img.shields.io/badge/OpenAI-Apps%20SDK-412991)](https://developers.openai.com/apps-sdk)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  
[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)  
[![Made with React](https://img.shields.io/badge/Frontend-React-61DAFB.svg)](https://react.dev/)

---

## 🌱 Visão geral
O **NutriAI** é um aplicativo educacional que analisa descrições de alimentos e retorna **estimativas nutricionais** (calorias, macronutrientes e insights simples).  
Ele segue as [Design Guidelines do OpenAI Apps SDK](https://developers.openai.com/apps-sdk/concepts/design-guidelines) e usa um **MCP Server** em Python para orquestrar chamadas à API da OpenAI.

> ⚠️ Este projeto é experimental e não substitui orientação médica ou nutricional.

---

## 🧩 Arquitetura

NutriAI/
├── app-ui/ # Front-end React (Apps SDK)
│ └── layout/
│ └── NutritionTable.tsx
├── mcp-server/ # Servidor MCP em Python/FastAPI
│ └── analyze_food/
│ └── schema.json
└── docs/
├── Design-Guidelines.md
└── privacy.md

---

## ⚙️ Instalação e execução local

### 1️⃣ Clonar o repositório
```bash
git clone https://github.com/frotoadriano/NutriAI.git
cd NutriAI

2️⃣ Backend (MCP Server em Python)
cd mcp-server
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Crie um arquivo .env com:
# OPENAI_API_KEY=seu_token_aqui
uvicorn main:app --reload

3️⃣ Frontend (React App)
cd app-ui
npm install
npm run dev

## 🛠️ Problema de compatibilidade: OpenAI SDK & httpx

Se você encontrar o erro:
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```
ao rodar o backend, isso ocorre por incompatibilidade entre versões do pacote `httpx` e o SDK oficial da OpenAI (`openai`).

**Solução:**
Certifique-se de usar a versão exata `httpx==0.27.2` no arquivo `requirements.txt`. Essa versão garante compatibilidade total com o SDK OpenAI (testado com `openai>=1.50.0`).

**Referência:**
O NutriAI utiliza o [OpenAI Python SDK](https://github.com/openai/openai-python) para integração com a API OpenAI. Sempre confira as versões recomendadas na documentação oficial.

```txt
# Exemplo de trecho do requirements.txt
openai==1.51.2
httpx==0.27.2
```

Se precisar atualizar dependências, sempre rode:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
🧠 Como funciona

O usuário descreve um alimento (ex.: “tapioca com queijo”).

O MCP Server envia a descrição para a API da OpenAI.

O modelo gera uma tabela nutricional e insights.

O front-end exibe os dados no formato nativo do ChatGPT Apps SDK.

🎨 Design e UX

Interface leve e responsiva.

Tons neutros e leitura fácil.

Frases curtas e empáticas (“Aqui está a estimativa para sua tapioca.”).

Mensagens de erro claras e educativas.

Mais detalhes em docs/Design-Guidelines.md
.

🔒 Privacidade

O NutriAI não coleta informações pessoais.
Veja a política de privacidade completa
.

---

## �️ **Proteções e Monitoramento**

### **Segurança implementada:**
- ✅ **Rate Limiting:** 5 req/min para MCP tools, 10 req/min para API REST
- ✅ **CORS restrito:** Apenas ChatGPT e origens autorizadas
- ✅ **API Keys opcionais:** Configure via variáveis de ambiente no Render
- ✅ **Monitoramento de custos:** Logs mostram gasto por requisição (~$0.0003 por análise)
- ✅ **Health checks:** Endpoint `/health` para monitoramento

### **Configuração no Render.com:**
```bash
# Variáveis de ambiente recomendadas
OPENAI_API_KEY=sua_chave_openai
API_KEYS=chave_secreta_1,chave_secreta_2  # Opcional mas recomendado  
ALLOWED_ORIGINS=https://chat.openai.com,https://chatgpt.com
```

---

## �📚 Roadmap

- ✅ **Design Guidelines** 
- ✅ **Schema JSON (MCP Server)**
- ✅ **Protocolo MCP compatível com ChatGPT Apps SDK**
- ✅ **Integração OpenAI API** 
- ✅ **Deploy em produção (Render.com)**
- ✅ **Rate limiting e proteções de segurança**
- 🔄 **Validação por imagem** (versão futura)
- 🔄 **Comparação entre alimentos**
- 🔄 **Histórico pessoal de análises**
- 🔄 **Integração com bases de dados nutricionais (USDA)**

🤝 Contribuição

Contribuições são bem-vindas!

Faça um fork.

Crie um branch: git checkout -b feature/nova-funcionalidade.

Commit → Push → Pull Request.

🪪 Licença

Distribuído sob licença MIT.
Veja o arquivo LICENSE
 para mais informações.

🧑‍💻 Autor

Adriano Frota – LinkedIn
 | GitHub
 
---
 

Como testar end-to-end

Backend
cd mcp-server
python -m venv venv 
      venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip

pip install -r requirements.txt
cp .env.example .env  # coloque sua OPENAI_API_KEY
uvicorn main:app --reload


Frontend 
cd app-ui
cp .env.example .env   # VITE_API_BASE=http://localhost:8000
npm i
npm run dev
# abra http://localhost:5173


