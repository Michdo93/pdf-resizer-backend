import os
import io
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pypdf import PdfReader, PdfWriter, Transformation

app = Flask(__name__)
# Erlaube CORS explizit für deine GitHub Pages Domain
CORS(app, resources={r"/convert": {"origins": "*"}})

# Umrechnung: 1 mm = 2.8346457 Point (PDF-Standardeinheit)
MM_TO_PT = 2.8346457

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Keine Datei hochgeladen"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Ungültiger Dateiname"}), 400

    try:
        # Zielmaße auslesen (in mm) und in Points umrechnen
        target_width_mm = float(request.form.get('width'))
        target_height_mm = float(request.form.get('height'))
        
        target_w = target_width_mm * MM_TO_PT
        target_h = target_height_mm * MM_TO_PT
    except (TypeError, ValueError):
        return jsonify({"error": "Ungültige Breiten- oder Höhenangaben"}), 400

    try:
        # PDF einlesen
        pdf_in = io.BytesIO(file.read())
        reader = PdfReader(pdf_in)
        writer = PdfWriter()

        for page in reader.pages:
            # Aktuelle Dimensionen der Seite holen
            current_w = float(page.mediabox.width)
            current_h = float(page.mediabox.height)

            # Skalierungsfaktoren berechnen (proportional)
            scale_x = target_w / current_w
            scale_y = target_h / current_h
            
            # Um Verzerrungen zu vermeiden, nutzen wir eine proportionale Skalierung (Fit)
            # Falls du eine exakte Dehnung erzwingen willst, nimm scale_x und scale_y separat.
            scale = min(scale_x, scale_y)

            # Transformation erstellen
            transform = Transformation().scale(sx=scale, sy=scale)
            
            # Inhalt transformieren
            page.add_transformation(transform)
            
            # Neue Seitengröße (MediaBox) setzen
            page.mediabox.left = 0
            page.mediabox.bottom = 0
            page.mediabox.right = target_w
            page.mediabox.top = target_h

            writer.add_page(page)

        # Output-Stream vorbereiten
        pdf_out = io.BytesIO()
        writer.write(pdf_out)
        pdf_out.seek(0)

        return send_file(
            pdf_out,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"konvertiert_{file.filename}"
        )

    except Exception as e:
        return jsonify({"error": f"Fehler bei der Verarbeitung: {str(e)}"}), 500

if __name__ == '__main__':
    # Lokal testen
    app.run(port=5000, debug=True)
