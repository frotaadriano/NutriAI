from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # carrega .env local
api_key = os.getenv("OPENAI_API_KEY")
print(f"🔑 OPENAI_API_KEY carregada: {'✅' if api_key else '❌'}")
print(f"🔑 Chave (primeiros 3 chars): {api_key[:3] if api_key else 'NENHUMA'}...")

client = OpenAI(api_key=api_key)

app = FastAPI(title="NutriAI MCP Server")
print(f"🚀 NutriAI MCP Server inicializado!")

# CORS: libere o Vite (5173) e o host do Apps SDK se precisar
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
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
def analyze(payload: AnalyzeFoodInput):
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
        model="gpt-4o-mini",
        temperature=0.2,
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
