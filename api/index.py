"""API Serverless per Vercel - Lead Generation con invio email"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


def invia_email_lead(data):
    """Invia email con i dati del lead

    Variabili d'ambiente richieste su Vercel:
    - EMAIL_HOST: smtp.gmail.com (o altro provider)
    - EMAIL_PORT: 587
    - EMAIL_USER: tua-email@gmail.com
    - EMAIL_PASSWORD: password-app (per Gmail usa App Password)
    - EMAIL_TO: email-destinatario@esempio.com (dove ricevere i lead)
    """
    try:
        # Configurazione SMTP da variabili d'ambiente
        smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('EMAIL_PORT', '587'))
        smtp_user = os.getenv('EMAIL_USER')
        smtp_password = os.getenv('EMAIL_PASSWORD')
        email_to = os.getenv('EMAIL_TO')

        if not all([smtp_user, smtp_password, email_to]):
            logger.warning("⚠️ Credenziali email non configurate. Configura le variabili d'ambiente su Vercel.")
            return False

        # Calcola lead score
        lead_score = calcola_lead_score(data)
        priority = calcola_priority_score(data)

        # Crea messaggio email
        msg = MIMEMultipart('alternative')
        marketing_consent = "✅ SÌ" if data.get('marketing_consent') else "❌ NO"
        msg['Subject'] = f"🔥 NUOVO LEAD - Priorità {priority}/10 (Score: {lead_score}/100)"
        msg['From'] = smtp_user
        msg['To'] = email_to

        # Corpo email HTML
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; }}
                .priority-high {{ background: #ff5722; color: white; padding: 10px; font-weight: bold; }}
                .priority-medium {{ background: #ff9800; color: white; padding: 10px; font-weight: bold; }}
                .priority-low {{ background: #2196F3; color: white; padding: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #4CAF50; }}
                .label {{ font-weight: bold; color: #555; }}
                .value {{ color: #000; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 NUOVO LEAD FOTOVOLTAICO</h1>
                <p>Ricevuto il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
            </div>

            <div class="{'priority-high' if priority >= 8 else 'priority-medium' if priority >= 6 else 'priority-low'}">
                ⭐ PRIORITÀ: {priority}/10 | LEAD SCORE: {lead_score}/100
            </div>

            <div class="section">
                <h2>👤 Dati Cliente</h2>
                <p><span class="label">Nome:</span> <span class="value">{data.get('nome', '')} {data.get('cognome', '')}</span></p>
                <p><span class="label">📧 Email:</span> <span class="value">{data.get('email', '')}</span></p>
                <p><span class="label">📱 Telefono:</span> <span class="value">{data.get('telefono', '')}</span></p>
                <p><span class="label">📍 Città:</span> <span class="value">{data.get('citta', '')} ({data.get('provincia', '')}) - {data.get('cap', '')}</span></p>
            </div>

            <div class="section">
                <h2>🏠 Immobile</h2>
                <p><span class="label">Tipo:</span> <span class="value">{data.get('tipo_immobile', 'N/D').upper()}</span></p>
            </div>

            <div class="section">
                <h2>⚡ Consumi Energetici</h2>
                <p><span class="label">Consumo mensile:</span> <span class="value">{data.get('consumo_mensile', 'N/D')} €/mese</span></p>
                <p><span class="label">Consumo annuo:</span> <span class="value">{data.get('consumo_annuo_kwh', 'N/D')} kWh/anno</span></p>
            </div>

            <div class="section">
                <h2>🎯 Interessi</h2>
                <p><span class="label">Batterie accumulo:</span> <span class="value">{'✅ SÌ' if data.get('interesse_batterie') else '❌ NO'}</span></p>
                <p><span class="label">Pompa di calore:</span> <span class="value">{'✅ SÌ' if data.get('interesse_pompa_calore') else '❌ NO'}</span></p>
                <p><span class="label">Tempistica:</span> <span class="value">{data.get('tempistica', 'N/D').upper()}</span></p>
            </div>

            <div class="section">
                <h2>💰 Stime Economiche</h2>
                <p><span class="label">Risparmio stimato:</span> <span class="value">{data.get('risparmio_stimato', 'N/D')} €/anno</span></p>
                <p><span class="label">Costo impianto:</span> <span class="value">{data.get('costo_impianto_stimato', 'N/D')} €</span></p>
                <p><span class="label">ROI:</span> <span class="value">{data.get('roi_anni', 'N/D')} anni</span></p>
            </div>

            <div class="section">
                <h2>📝 Note</h2>
                <p>{data.get('note', 'Nessuna nota')}</p>
            </div>

            <div class="section">
                <h2>🔍 Tracking</h2>
                <p><span class="label">Source:</span> <span class="value">{data.get('source', 'landing_page')}</span></p>
                <p><span class="label">UTM Source:</span> <span class="value">{data.get('utm_source', 'N/D')}</span></p>
                <p><span class="label">UTM Campaign:</span> <span class="value">{data.get('utm_campaign', 'N/D')}</span></p>
            </div>

            <div class="section">
                <h2>📧 Consensi GDPR</h2>
                <p><span class="label">Consenso Marketing:</span> <span class="value">{marketing_consent}</span></p>
                <p style="font-size: 0.9rem; color: #888;">
                    {'✅ Puoi contattarlo per offerte commerciali' if data.get('marketing_consent') else '❌ Contatto SOLO per questo preventivo'}
                </p>
            </div>

            <hr>
            <p style="color: #888; font-size: 12px;">Email automatica dal sistema di lead generation</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, 'html'))

        # Invia email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"✅ Email inviata a {email_to}")
        return True

    except Exception as e:
        logger.error(f"❌ Errore invio email: {e}")
        return False


def calcola_lead_score(data):
    """Calcola il lead score in base ai dati forniti (0-100)"""
    score = 50  # Base

    # Consumo mensile alto = più interessante
    consumo = float(data.get('consumo_mensile', 0))
    if consumo > 200:
        score += 20
    elif consumo > 150:
        score += 15
    elif consumo > 100:
        score += 10
    elif consumo > 50:
        score += 5

    # Tempistica immediata = più interessante
    if data.get('tempistica') == 'immediato':
        score += 15
    elif data.get('tempistica') == '3-mesi':
        score += 10

    # Interesse per batterie/pompe = più valore
    if data.get('interesse_batterie'):
        score += 5
    if data.get('interesse_pompa_calore'):
        score += 5

    # Tipo immobile
    tipo = data.get('tipo_immobile')
    if tipo == 'azienda':
        score += 10  # Aziende = contratti più grandi
    elif tipo == 'casa':
        score += 5

    return min(score, 100)


def calcola_priority_score(data):
    """Calcola priorità di contatto (1-10)"""
    priority = 5  # Base

    # Tempistica urgente
    if data.get('tempistica') == 'immediato':
        priority += 3
    elif data.get('tempistica') == '3-mesi':
        priority += 1

    # Consumo alto
    consumo = float(data.get('consumo_mensile', 0))
    if consumo > 200:
        priority += 2

    return min(priority, 10)


@app.route('/api/richiesta-preventivo', methods=['POST', 'OPTIONS'])
def richiesta_preventivo():
    """Endpoint per ricevere richieste di preventivo"""
    # Gestisci preflight CORS
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        # Log della richiesta
        logger.info(f"📩 Ricevuta richiesta preventivo")

        # Verifica Content-Type
        if not request.is_json:
            logger.error(f"Content-Type non valido: {request.content_type}")
            return jsonify({
                'success': False,
                'error': 'Content-Type deve essere application/json'
            }), 400

        data = request.get_json()

        if not data:
            logger.error("Body vuoto")
            return jsonify({
                'success': False,
                'error': 'Dati mancanti'
            }), 400

        logger.info(f"Dati ricevuti da: {data.get('email', 'N/A')}")

        # Validazione dati obbligatori
        required_fields = ['nome', 'email', 'telefono', 'citta']
        for field in required_fields:
            if not data.get(field):
                logger.error(f"Campo mancante: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Campo obbligatorio mancante: {field}'
                }), 400

        # Genera ID univoco
        lead_id = datetime.now().strftime('%Y%m%d%H%M%S')

        # Invia email con i dati del lead
        email_sent = invia_email_lead(data)

        if email_sent:
            logger.info(f"✅ Lead {lead_id} processato e email inviata")
            return jsonify({
                'success': True,
                'id': lead_id,
                'message': 'Richiesta ricevuta con successo! Ti contatteremo presto.'
            }), 200
        else:
            # Anche se l'email fallisce, confermiamo la ricezione
            logger.warning("⚠️ Lead ricevuto ma email non inviata (controlla configurazione)")
            return jsonify({
                'success': True,
                'id': lead_id,
                'message': 'Richiesta ricevuta con successo!'
            }), 200

    except Exception as e:
        logger.error(f"❌ Errore nel processare la richiesta: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Errore del server: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'landing-page-api',
        'email_configured': bool(os.getenv('EMAIL_USER') and os.getenv('EMAIL_PASSWORD'))
    }), 200


# Handler per Vercel - AGGIORNATO
app = app
