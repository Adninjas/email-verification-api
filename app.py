import imaplib
import re
import os  # Adicionado para usar variáveis de ambiente
from flask import Flask, jsonify, request  # Adicionado request para pegar o parâmetro phone

app = Flask(__name__)

@app.route('/get_verification_code', methods=['GET'])
def get_verification_code():
    try:
        # Obtém o parâmetro phone da query string
        phone = request.args.get('phone')
        if not phone:
            return jsonify({'error': 'Parâmetro phone não fornecido'}), 400

        # Conecta ao servidor IMAP
        mail = imaplib.IMAP4_SSL('imap.hostinger.com')
        mail.login('chatgpt@adninjas.pro', 'Keylogger#0!')
        mail.select('inbox')

        # Busca e-mails de noreply@openai.com com o assunto "verification code"
        result, data = mail.search(None, '(FROM "noreply@openai.com" Subject "verification code")')
        if not data[0]:
            mail.logout()
            return jsonify({'error': 'Nenhum e-mail encontrado'}), 404

        # Pega o último e-mail encontrado
        email_id = data[0].split()[-1]
        result, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1].decode('utf-8')

        # Extrai o código de 6 dígitos
        match = re.search(r'\b\d{6}\b', raw_email)
        code = match.group(0) if match else None

        mail.logout()

        if code:
            return jsonify({'code': code})
        else:
            return jsonify({'error': 'Código não encontrado no e-mail'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Usa a porta fornecida pelo Render ou 5000 para desenvolvimento local
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)