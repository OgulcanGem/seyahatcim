$(document).ready(function () {
  // Tüm ülkeleri ve şehirleri içeren JSON verisini yükle
  $.getJSON("/static/data/countries.json", function (countryCityData) {
    const countries = Object.keys(countryCityData);

    // Ülkeleri Select2 ile doldur
    $('#countrySelect').select2({
      placeholder: 'Bir ülke seçin',
      data: countries.map(c => ({ id: c, text: c }))
    });

    // Ülke seçilince ilgili şehirleri doldur
    $('#countrySelect').on('select2:select', function (e) {
      const selectedCountry = e.params.data.id;
      const cities = countryCityData[selectedCountry] || [];

      $('#citySelect').empty().select2({
        placeholder: 'Bir şehir seçin',
        data: cities.map(city => ({ id: city, text: city }))
      });
    });
  });
});

// Groq API üzerinden öneri almak için
async function getSuggestion() {
  const year = document.getElementById("yearSelect").value;
  const countryData = $('#countrySelect').select2('data');
  const cityData = $('#citySelect').select2('data');

  if (!countryData.length || !cityData.length) {
    alert("Lütfen ülke ve şehir seçin.");
    return;
  }

  const country = countryData[0].text;
  const city = cityData[0].text;

  try {
    const response = await fetch("/get_suggestion", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ year, country, city })
    });

    const result = await response.json();

    if (!result.success) {
      const errorMsg = typeof result.error === "string"
        ? result.error
        : JSON.stringify(result.error, null, 2);
      throw new Error(errorMsg);
    }

    const parsed = parseResponse(result.message);
    renderResults(parsed);
  } catch (error) {
    document.getElementById("resultArea").innerHTML =
      `<p style="color:red;">Bir hata oluştu:<br><code>${error.message}</code></p>`;
    console.error("Hata:", error.message || error);
  }
}

function parseResponse(responseText) {
  const lines = responseText.split('\n').filter(line => line.includes(':'));
  const result = {};
  lines.forEach(line => {
    const [key, value] = line.split(':');
    result[key.trim()] = value.trim();
  });
  return result;
}

function renderStars(score) {
  const filled = '★'.repeat(Math.round(score));
  const empty = '☆'.repeat(10 - Math.round(score));
  return `<span style="color:#007BFF; font-size:18px;">${filled}${empty}</span>`;
}

function renderResults(data) {
  const holidayNote = data["Resmi Tatil"]?.toLowerCase().includes("evet")
    ? `<div style="background:#ffdede; padding:10px; margin-top:10px; border-left:5px solid red;">
         📅 <strong>O gün resmi tatildir!</strong><br>${data["Resmi Tatil"]}
       </div>`
    : "";

  document.getElementById("resultArea").innerHTML = `
    <h3>📆 Önerilen Ziyaret Tarihi: <span style="color:#007BFF;">${data["Tarih"]}</span></h3>
    <ul style="list-style:none; padding-left:0;">
      <li>💰 Fiyat Skoru: ${renderStars(data["Fiyat Skoru"])}</li>
      <li>🌤️ Hava Skoru: ${renderStars(data["Hava Durumu Skoru"])}</li>
      <li>👥 Kalabalık Skoru: ${renderStars(data["Kalabalık Skoru"])}</li>
    </ul>
    ${holidayNote}
  `;
}
