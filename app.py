from flask import Flask, jsonify
import imaplib
import email
import re
from datetime import datetime, timedelta
import ssl

app = Flask(__name__)

# Coloque suas informações aqui
EMAIL_ADDRESS = "chatgpt@adninjas.pro"  
EMAIL_PASSWORD = "Keylogger#0!"           
IMAP_SERVER = "imap.hostinger.com"
IMAP_PORT = 993

def fetch_verification_code():
    try:
        # Conectar ao e-mail
        context = ssl.create_default_context()
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        # Buscar e-mails recentes (últimas 24 horas)
        since_date = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        result, data = mail.search(None, '(FROM "noreply@openai.com")')

        if not data[0]:
            return {"error": "Nenhum e-mail encontrado"}

        # Pegar o último e-mail
        latest_email_id = data[0].split()[-1]
        result, data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Pegar o corpo do e-mail
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # Encontrar o código de 6 dígitos
        code_match = re.search(r"\b\d{6}\b", body)
        if not code_match:
            return {"error": "Código não encontrado"}
        
        code = code_match.group(0)
        return {"code": code}

    except Exception as e:
        return {"error": str(e)}
    finally:
        mail.logout()

@app.route("/get-verification-code", methods=["GET"])
def get_verification_code():
    result = fetch_verification_code()
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)