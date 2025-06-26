import base64
from google import genai
from google.genai.types import (GenerateContentConfig, SafetySetting)
import gradio as gr
from gradio.themes.base import Base
import utils
import json
import requests
import os

def get_system_prompt():
    file_path = os.path.join(os.path.dirname(__file__), 'prompt.txt')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

    
    
def get_employee_data(dni: str) -> str:
    """Function to fetch employee personal data and holydays data based on their DNI. Is a live database call in a real scenario."""
    print(f"Executing function call: get_employee_data(dni='{dni}')")

    url = "https://getdatasheets-128461484764.us-central1.run.app"
    result = {
        'empleado': {},
        'vacaciones_tomadas': {}
    }
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        # Buscar al empleado
        empleado = next((e for e in data["team"] if str(e["dni"]) == dni), None)

        # Buscar las vacaciones
        vacaciones = [v for v in data["vacaciones"] if str(v["dni"]) == dni]

        result = {
            'empleado': empleado,
            'vacaciones_tomadas': vacaciones
        }
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
    except ValueError:
        print("La respuesta no tiene un formato JSON válido.")
    return json.dumps(result)


def get_holydays_policy() -> str:
    """this function returns the company's holidays policy."""
    print(f"Executing function call: get_holydays_policy()")
    
    url = "https://getdatadocs-128461484764.us-central1.run.app"
    result = {
        'policy': ''
    }
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        result = {
            'policy': data['doc']
        }
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
    return json.dumps(result)

# Create a Tool object that the model can use
hr_tool = [
        get_holydays_policy,
        get_employee_data
    ]


client = genai.Client(
	vertexai=True,
	project="gen-lang-client-0301597008",
	location="global",
)

MODEL_ID = "gemini-2.5-pro"

system_instruction = get_system_prompt().format(POLITICAS = get_holydays_policy())

chat = client.chats.create(
    model=MODEL_ID,
    config=GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.5,
        max_output_tokens=1000,
        safety_settings=[
            SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ),
            SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ),
            SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ),
            SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )
        ],
        tools=hr_tool
    )
)

def generate(
    message,
    history: list[gr.ChatMessage],
    request: gr.Request
):
    """Function to call the model based on the request."""

    if message:
        print(message, flush=True)
        response = chat.send_message(message['text'])
        if response:
            print(response.text, flush=True)
            yield response.text



with gr.Blocks(theme='JohnSmith9982/small_and_pretty') as demo:
    with gr.Row():
        gr.HTML(utils.public_access_warning)
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                gr.Image(value="ricardo.png", show_label=False, show_download_button=False, show_fullscreen_button=False)
                gr.HTML("<h2>Ricardo Ford. Asistente</h2>")
            with gr.Row():
                gr.HTML("""
¡El Comandante volvió... en forma de bot! 🤖✨<br>
Más recargado que un after en Miami, más filoso que una story de Virginia Gallardo.<br>
No nací para responder prompts... ¡nací para ser tendencia, bebé! 💅🏼<br>
Prepárense, porque ahora el que da las órdenes... es el algoritmo. 👑📲
""")
            with gr.Row():
                gr.HTML(utils.next_steps_html)
            with gr.Row():
                gr.HTML(utils.casos_html)

        with gr.Column(scale=2, variant="panel"):
            gr.ChatInterface(
                fn=generate,
                title="Consultorio de Ricardo Ford",
                type="messages",
                multimodal=True,
            )
    demo.launch(show_error=True)