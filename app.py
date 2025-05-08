from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# ✅ Groq API anahtarını buraya yapıştır
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

    prompt = f"""
Kullanıcı {year} yılında {country} ülkesindeki {city} şehrini ziyaret etmek istiyor.
Lütfen AŞAĞIDAKİ ŞEKİLDE CEVAP VER (Aynı format, başka hiçbir şey yazma):

Tarih: YYYY-MM-DD  
Fiyat Skoru: [0-10]  
Hava Durumu Skoru: [0-10]  
Kalabalık Skoru: [0-10]  
Resmi Tatil: (Evet/Hayır ve varsa tatil ismi)
"""

    try:
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

        # HTTP 200 kontrolü
        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"Groq API hatası: {response.status_code} - {response.text}"
            })

        result = response.json()

        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]["content"]
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({
                "success": False,
                "error": "Groq API yanıtında 'choices' bulunamadı."
            })

    except Exception as e:
        return jsonify({"success": False, "error": f"Sunucu hatası: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)