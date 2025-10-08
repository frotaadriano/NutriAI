from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import os, json, time
from dotenv import load_dotenv
from openai import OpenAI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

load_dotenv()  # carrega .env local
api_key = os.getenv("OPENAI_API_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []

print(f"🔑 OPENAI_API_KEY carregada: {'✅' if api_key else '❌'}")
print(f"🔑 Chave (primeiros 3 chars): {api_key[:3] if api_key else 'NENHUMA'}...")
print(f"🛡️ API Keys configuradas: {len(API_KEYS)} chaves")
print(f"🌐 Origins permitidas: {ALLOWED_ORIGINS}")

client = OpenAI(api_key=api_key)

# Função para verificar API key
def verify_api_key(request: Request) -> bool:
    if not API_KEYS:  # Se não tiver API keys configuradas, permite acesso
        return True
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header.replace("Bearer ", "")
    return token in API_KEYS

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="NutriAI MCP Server")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Servir arquivos estáticos para .well-known
try:
    app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")
except:
    print("⚠️ Diretório .well-known não encontrado, mas continuando...")

print(f"🚀 NutriAI MCP Server inicializado com rate limiting!")

# CORS: libere o Vite (5173) e o host do Apps SDK se precisar
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["https://chat.openai.com", "https://chatgpt.com"],  # Adiciona ChatGPT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeFoodInput(BaseModel):
    food_description: str
    portion_grams: Optional[float] = None

class Nutrient(BaseModel):
    name: str
    per100g: float
    portion: float

class AnalyzeFoodOutput(BaseModel):
    nutrients: List[Nutrient]
    insights: List[str]
    advice: str
    disclaimer: str

# Classes para protocolo MCP (Model Context Protocol)
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    method: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str, int]
    result: Dict[str, Any] = None
    error: Dict[str, Any] = None

SYSTEM_PROMPT = """Você é um assistente de nutrição educativo.
Retorne SEMPRE JSON válido com:
{
  "nutrients": [{"name":"...","per100g":n,"portion":n}, ...],
  "insights": ["..."],
  "advice": "...",
  "disclaimer": "Estimativa educativa; não substitui orientação médica."
}
- Use valores estimados coerentes por 100g.
- Se portion_grams não vier, assuma 100g.
- Máximo 3 insights curtos.
- Nada de texto fora do JSON.
"""

@app.post("/analyze", response_model=AnalyzeFoodOutput)
@limiter.limit("10/minute")  # 10 requests por minuto por IP
def analyze(request: Request, payload: AnalyzeFoodInput):
    print(f"\n🍎 RECEBIDO: {payload.food_description}")
    
    portion = payload.portion_grams if (payload.portion_grams or 0) > 0 else 100.0
    print(f"📏 PORÇÃO: {portion}g")
    
    user_prompt = (
        f"Alimento: {payload.food_description}\n"
        f"Porção (g): {portion}\n"
        "Gere os campos solicitados, mantendo números simples."
    )
    
    print(f"\n📝 PROMPT DO USUÁRIO:")
    print(user_prompt)
    print(f"\n🤖 ENVIANDO PARA OpenAI...")

    resp = client.chat.completions.create(
        model="gpt-5-nano-2025-08-07",
        temperature=1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    print(f"\n📊 TOKENS USADOS:")
    print(f"  - Input: {resp.usage.prompt_tokens}")
    print(f"  - Output: {resp.usage.completion_tokens}")
    print(f"  - Total: {resp.usage.total_tokens}")
    
    # Log de custo aproximado (GPT-4o-mini: $0.00015/1K input, $0.0006/1K output)
    input_cost = (resp.usage.prompt_tokens / 1000) * 0.00015
    output_cost = (resp.usage.completion_tokens / 1000) * 0.0006
    total_cost = input_cost + output_cost
    print(f"💰 CUSTO APROXIMADO: ${total_cost:.6f}")
    
    content = resp.choices[0].message.content
    print(f"\n💬 RESPOSTA DA OpenAI:")
    print(content)
    
    try:
        parsed_response = json.loads(content)
        print(f"\n✅ JSON VÁLIDO - Processando...")
        return AnalyzeFoodOutput(**parsed_response)
    except json.JSONDecodeError as e:
        print(f"\n❌ ERRO JSON: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERRO DE VALIDAÇÃO: {e}")
        raise

# Endpoint para Apps SDK - Tool MCP
@app.post("/tools/analyze_food")
@limiter.limit("5/minute")  # 5 requests por minuto por IP para tools
async def analyze_food_tool(request: Request):
    """Tool endpoint para integração com ChatGPT Apps SDK"""
    # Verificar API key se configurada
    if API_KEYS and not verify_api_key(request):
        raise HTTPException(status_code=401, detail="API key inválida ou ausente")
    
    data = await request.json()
    print(f"\n🛠️ TOOL CHAMADA pelo Apps SDK: {data}")
    
    # Converte dados da tool para formato da função
    payload = AnalyzeFoodInput(
        food_description=data.get("food_description", ""),
        portion_grams=data.get("portion_grams")
    )
    
    # Chama a função de análise existente
    result = analyze(payload)
    return result.dict()

# Endpoint de saúde
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "rate_limits": "5/min para tools, 10/min para análises",
        "auth": "API key opcional" if API_KEYS else "público"
    }

# Endpoint MCP protocolo JSON-RPC (esperado pelo ChatGPT Apps SDK)
@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Endpoint MCP compatível com ChatGPT Apps SDK usando protocolo JSON-RPC 2.0"""
    print(f"\n🔌 MCP REQUEST: {request.method} (id: {request.id})")
    
    if request.method == "initialize":
        print("🚀 ChatGPT solicitando inicialização do MCP...")
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "NutriAI",
                    "version": "1.0.0"
                }
            }
        )
    
    elif request.method == "tools/list":
        print("📋 ChatGPT solicitando lista de tools...")
        return MCPResponse(
            id=request.id,
            result={
                "tools": [
                    {
                        "name": "analyze_food",
                        "description": "Analisa alimento e retorna estimativa nutricional completa com calorias, macronutrientes e insights personalizados",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "food_description": {
                                    "type": "string",
                                    "description": "Descrição do alimento (ex: 'tapioca 2 colheres com queijo', 'banana prata média')"
                                },
                                "portion_grams": {
                                    "type": "number", 
                                    "description": "Porção em gramas (opcional, padrão: 100g)",
                                    "default": 100.0
                                }
                            },
                            "required": ["food_description"]
                        }
                    }
                ]
            }
        )
    
    elif request.method == "tools/call":
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        print(f"🛠️ ChatGPT chamando tool: {tool_name} com argumentos: {arguments}")
        
        if tool_name == "analyze_food":
            try:
                # Usa sua função existente de análise!
                payload = AnalyzeFoodInput(
                    food_description=arguments.get("food_description", ""),
                    portion_grams=arguments.get("portion_grams")
                )
                
                # Chama sua função analyze() existente sem o request (problema do rate limiter)
                print(f"\n🍎 ANÁLISE MCP: {payload.food_description}")
                
                portion = payload.portion_grams if (payload.portion_grams or 0) > 0 else 100.0
                user_prompt = (
                    f"Alimento: {payload.food_description}\n"
                    f"Porção (g): {portion}\n"
                    "Gere os campos solicitados, mantendo números simples."
                )
                
                print(f"🤖 ENVIANDO PARA OpenAI via MCP...")
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                
                print(f"📊 TOKENS (MCP): {resp.usage.total_tokens}")
                content = resp.choices[0].message.content
                parsed_response = json.loads(content)
                result = AnalyzeFoodOutput(**parsed_response)
                
                # Formata resposta para o ChatGPT
                formatted_response = f"""
🥗 **Análise Nutricional: {payload.food_description}**
📏 **Porção**: {portion}g

🔢 **Informações Nutricionais**:
"""
                for nutrient in result.nutrients:
                    formatted_response += f"• **{nutrient.name}**: {nutrient.portion:.1f} (por {portion}g) | {nutrient.per100g:.1f} (por 100g)\n"
                
                formatted_response += f"\n💡 **Insights**:\n"
                for insight in result.insights:
                    formatted_response += f"• {insight}\n"
                
                formatted_response += f"\n💬 **Dica**: {result.advice}\n"
                formatted_response += f"\n⚠️ {result.disclaimer}"
                
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": formatted_response
                            }
                        ]
                    }
                )
                
            except Exception as e:
                print(f"❌ ERRO na análise MCP: {e}")
                return MCPResponse(
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": f"Erro interno: {str(e)}"
                    }
                )
        
        else:
            return MCPResponse(
                id=request.id,
                error={
                    "code": -32601,
                    "message": f"Tool não encontrada: {tool_name}"
                }
            )
    
    else:
        return MCPResponse(
            id=request.id,
            error={
                "code": -32601,
                "message": f"Método não suportado: {request.method}"
            }
        )

# Endpoint MCP info (GET para debug)
@app.get("/mcp")
def mcp_info():
    """Informações do servidor MCP (para debug)"""
    return {
        "server": "NutriAI MCP Server",
        "version": "1.0.0", 
        "description": "Assistente de análise nutricional",
        "protocol": "JSON-RPC 2.0",
        "note": "Use POST para chamadas MCP reais"
    }

# Endpoint de configuração do Apps SDK (o que o ChatGPT procura)
@app.get("/.well-known/openai_hosted_app")
@app.get("/openai_hosted_app")  # Rota alternativa
def openai_hosted_app():
    """Configuração para o ChatGPT Apps SDK"""
    return {
        "name_for_model": "nutriai",
        "name_for_human": "NutriAI - Análise Nutricional", 
        "description_for_model": "Analisa alimentos e fornece estimativas nutricionais detalhadas incluindo calorias, macronutrientes, insights e dicas personalizadas. Use quando o usuário perguntar sobre informações nutricionais de alimentos.",
        "description_for_human": "Assistente que analisa qualquer alimento e fornece informações nutricionais completas.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi", 
            "url": "https://nutriai-mcp-server.onrender.com/openapi.json"
        },
        "contact_email": "contato@exemplo.com",
        "privacy_policy_url": "https://github.com/frotaadriano/NutriAI/blob/main/README.md"
    }

# Endpoint de metadata para Apps SDK
@app.get("/tools/metadata")
def get_tools_metadata():
    """Metadata das tools para o Apps SDK descobrir"""
    return {
        "tools": [
            {
                "name": "analyze_food",
                "description": "Analisa alimento e retorna estimativa nutricional completa com calorias, macronutrientes e insights personalizados.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "food_description": {
                            "type": "string", 
                            "description": "Descrição do alimento (ex: 'tapioca 2 colheres com queijo')"
                        },
                        "portion_grams": {
                            "type": "number",
                            "description": "Porção em gramas (opcional, padrão: 100g)",
                            "default": 100.0
                        }
                    },
                    "required": ["food_description"]
                },
                "examples": [
                    {
                        "food_description": "tapioca 2 colheres com queijo",
                        "portion_grams": 120
                    },
                    {
                        "food_description": "banana prata média", 
                        "portion_grams": 86
                    },
                    {
                        "food_description": "pão francês com manteiga"
                    }
                ]
            }
        ]
    }

# Endpoint raiz para verificação
@app.get("/")
def root():
    """Endpoint raiz com informações básicas"""
    return {
        "app": "NutriAI MCP Server",
        "status": "online",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp", 
            "tools_metadata": "/tools/metadata",
            "analyze_food": "/tools/analyze_food",
            "apps_config": "/.well-known/openai_hosted_app"
        }
    }
