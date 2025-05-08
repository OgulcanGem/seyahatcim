from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# Groq API anahtarı
GROQ_API_KEY = "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"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_suggestion', methods=['POST'])
def get_suggestion():
    data = request.json
    year = data.get("year")
    country = data.get("country")
    city = data.get("city")

    def call_groq_api(prompt):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API hatası: {response.status_code} - {response.text}"}

    base_prompt = f"""
Kullanıcı {year} yılında {country} ülkesindeki {city} şehrini ziyaret etmek istiyor.
Lütfen AŞAĞIDAKİ ŞEKİLDE CEVAP VER (Aynı format, başka hiçbir şey yazma):

Tarih: YYYY-MM-DD  
Fiyat Skoru: [0-10]  
Hava Durumu Skoru: [0-10]  
Kalabalık Skoru: [0-10]  
Resmi Tatil: (Evet/Hayır ve varsa tatil ismi)
"""

    for _ in range(3):
        result = call_groq_api(base_prompt)
        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]["content"]
            if "Resmi Tatil: Hayır" in message:
                return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": result.get("error", "Bilinmeyen hata.")})

    return jsonify({"success": False, "error": "Uygun bir gün bulunamadı. Lütfen daha sonra tekrar deneyin."})

if __name__ == '__main__':
    app.run(debug=True)
