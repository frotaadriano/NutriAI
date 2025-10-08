# apps/tools.py - Configuração para Apps SDK
"""
Este arquivo contém as configurações das tools para integração com ChatGPT Apps SDK.
O server principal (main.py) já implementa os endpoints necessários.
"""

# Metadata completa do app para o Apps SDK
APP_METADATA = {
    "name": "NutriAI",
    "description": "Assistente de análise nutricional que estima calorias, macronutrientes e fornece insights personalizados sobre alimentos.",
    "version": "1.0.0",
    "categories": ["health", "nutrition", "wellness"],
    "author": "Adriano Frota",
    "website": "https://github.com/frotaadriano/NutriAI",
    "tools": [
        {
            "name": "analyze_food",
            "description": "Analisa qualquer descrição de alimento e retorna estimativa nutricional detalhada com calorias, macronutrientes, insights e dicas personalizadas.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "food_description": {
                        "type": "string",
                        "description": "Descrição detalhada do alimento, incluindo preparo e quantidade (ex: 'tapioca 2 colheres com queijo', 'banana prata média', 'pão francês com manteiga')"
                    },
                    "portion_grams": {
                        "type": "number",
                        "description": "Peso da porção em gramas (opcional). Se não informado, usa 100g como padrão.",
                        "minimum": 1,
                        "maximum": 2000,
                        "default": 100.0
                    }
                },
                "required": ["food_description"]
            },
            "examples": [
                {
                    "description": "Análise de tapioca com queijo",
                    "input": {
                        "food_description": "tapioca 2 colheres com queijo coalho",
                        "portion_grams": 120
                    }
                },
                {
                    "description": "Análise de fruta",
                    "input": {
                        "food_description": "banana prata média",
                        "portion_grams": 86
                    }
                },
                {
                    "description": "Análise sem especificar peso",
                    "input": {
                        "food_description": "pão francês com manteiga"
                    }
                }
            ]
        }
    ],
    "discovery_prompts": [
        "Analise esse alimento para mim",
        "Quantas calorias tem essa comida?",
        "Me dê informações nutricionais sobre...",
        "Qual o valor nutricional de...",
        "É saudável comer...?"
    ],
    "privacy_policy": "O NutriAI não coleta informações pessoais. Todas as análises são processadas em tempo real via API OpenAI.",
    "terms_of_service": "Ferramenta educativa. Não substitui orientação médica ou nutricional profissional."
}