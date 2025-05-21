import imaplib
import re
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/get_verification_code', methods=['GET'])
def get_verification_code():
    try:
        mail = imaplib.IMAP4_SSL('imap.hostinger.com')
        mail.login('chatgpt@adninjas.pro', 'Keylogger#0!')
        mail.select('inbox')
        result, data = mail.search(None, '(FROM "noreply@openai.com" SUBJECT "verification code")')
        if not data[0]:
            return jsonify({'error': 'Nenhum e-mail encontrado'}), 404

        email_id = data[0].split()[-1]
        result, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1].decode('utf-8')
        match = re.search(r'\b\d{6}\b', raw_email)
        code = match.group(0) if match else None

        mail.logout()
        if code:
            return jsonify({'code': code})
        else:
            return jsonify({'error': 'Código não encontrado no e-mail'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
