import requests
from bs4 import BeautifulSoup
import json
import os

TELEGRAM_TOKEN = os.getenv("8033652394:AAHZ7Uf3laqzsA788vLOkzhdF7q1Jlvfjmo")
CHAT_ID = os.getenv("1060914824")

URL = "https://www.fia.com/documents/championships/fia-formula-one-world-championship-14/season/season-2025-2071"
ARCHIVO_ESTADO = "documentos_previos.json"  # se guardará en el container temporalmente


def obtener_documentos():
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    tarjetas = soup.select(".views-row")

    documentos = []
    for tarjeta in tarjetas:
        titulo = tarjeta.select_one(".title").get_text(strip=True)
        enlace = "https://www.fia.com" + tarjeta.select_one(".title a")["href"]
        fecha = tarjeta.select_one(".date-display-single").get_text(strip=True)

        documentos.append({
            "titulo": titulo,
            "enlace": enlace,
            "fecha": fecha
        })

    return documentos

def cargar_documentos_previos():
    if not os.path.exists(ARCHIVO_ESTADO):
        return []
    with open(ARCHIVO_ESTADO, "r") as f:
        return json.load(f)

def guardar_documentos(documentos):
    with open(ARCHIVO_ESTADO, "w") as f:
        json.dump(documentos, f, indent=2)

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensaje
    }
    requests.post(url, data=data)

def main():
    documentos_actuales = obtener_documentos()
    documentos_previos = cargar_documentos_previos()

    titulos_previos = {doc["titulo"] for doc in documentos_previos}
    nuevos = [doc for doc in documentos_actuales if doc["titulo"] not in titulos_previos]

    if nuevos:
        mensaje = "📄 *Nuevos documentos de la FIA:*\n\n"
        for doc in nuevos:
            mensaje += f"📌 {doc['titulo']} ({doc['fecha']})\n🔗 {doc['enlace']}\n\n"

        enviar_telegram(mensaje)
        print("✅ Enviado por Telegram.")
    else:
        print("📭 No hay nuevos documentos.")

    guardar_documentos(documentos_actuales)

if __name__ == "__main__":
    main()
