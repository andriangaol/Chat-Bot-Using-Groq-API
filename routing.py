from groq_client import client, ROUTING_MODEL, TOOL_USE_MODEL, GENERAL_MODEL
from tools import calculate
from telegram import Update
from telegram.ext import CallbackContext
import json

def route_query(query: str) -> str:
    """
    Menentukan apakah query membutuhkan alat kalkulasi atau tidak.
    
    Args:
        query (str): Pertanyaan dari pengguna
        
    Returns:
        str: 'calculate' jika membutuhkan alat kalkulasi, 'general' jika tidak
    """
    routing_prompt = f"""
    Berdasarkan pertanyaan pengguna berikut, tentukan apakah perlu menggunakan alat untuk menjawabnya.
    Jika perlu alat kalkulasi, jawab dengan 'ALAT: HITUNG'.
    Jika tidak perlu alat, jawab dengan 'TIDAK PERLU ALAT'.

    Pertanyaan pengguna: {query}

    Respons:
    """
    response = client.chat.completions.create(
        model=ROUTING_MODEL,
        messages=[
            {"role": "system", "content": "Kamu adalah asisten routing. Tentukan apakah alat diperlukan berdasarkan pertanyaan pengguna."},
            {"role": "user", "content": routing_prompt},
        ],
        max_tokens=20
    )
    keputusan_routing = response.choices[0].message.content.strip()
    return "calculate" if "ALAT: HITUNG" in keputusan_routing else "general"

def run_with_tool(query: str) -> str:
    """
    Menggunakan model khusus untuk melakukan kalkulasi.
    
    Args:
        query (str): Pertanyaan dari pengguna yang membutuhkan kalkulasi
        
    Returns:
        str: Hasil kalkulasi dalam bentuk teks
    """
    messages = [
        {"role": "system", "content": "You are a calculator assistant."},
        {"role": "user", "content": query},
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "The expression to evaluate"},
                    },
                    "required": ["expression"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model=TOOL_USE_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096,
    )
    response_message = response.choices[0].message
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_args = json.loads(tool_call.function.arguments)
            function_response = calculate(function_args.get("expression"))
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": "calculate",
                    "content": function_response,
                }
            )
        second_response = client.chat.completions.create(
            model=TOOL_USE_MODEL, messages=messages
        )
        return second_response.choices[0].message.content
    return response_message.content

def run_general(query: str, chat_history: list = None) -> str:
    """
    Menggunakan model umum untuk menjawab pertanyaan.
    
    Args:
        query (str): Pertanyaan dari pengguna
        chat_history (list, optional): Riwayat chat sebelumnya. Defaults to None.
        
    Returns:
        str: Jawaban dari model
    """
    messages = chat_history if chat_history else []
    messages += [
        {"role": "system", "content": "Kamu adalah asisten virtual yang ramah dan membantu. Jawablah dalam Bahasa Indonesia."},
        {"role": "user", "content": query},
    ]
    response = client.chat.completions.create(
        model=GENERAL_MODEL,
        messages=messages
    )
    return response.choices[0].message.content

def process_query(query: str) -> dict:
    """
    Memproses query dan mengarahkannya ke model yang sesuai.
    
    Args:
        query (str): Pertanyaan dari pengguna
        
    Returns:
        dict: Dictionary berisi query asli, rute yang dipilih, dan respons
    """
    route = route_query(query)
    response = run_with_tool(query) if route == "calculate" else run_general(query)
    return {"query": query, "route": route, "response": response}

async def handle_message(update: Update, context: CallbackContext) -> None:
    """
    Menangani pesan masuk dari Telegram.
    
    Args:
        update (Update): Object update dari Telegram
        context (CallbackContext): Context dari Telegram bot
    """
    user_message = update.message.text
    result = process_query(user_message)
    response = result["response"]
    await update.message.reply_text(response)

