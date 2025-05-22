from flask import Flask, jsonify, request
import imaplib
import email
from email.header import decode_header
import re
import logging
import requests
import os
from urllib.parse import unquote

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Configurações IMAP para o webmail da Hostinger
IMAP_SERVER = "imap.hostinger.com"
IMAP_USER = os.getenv('IMAP_USER', 'chatgpt@adninjas.pro')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD', 'Keylogger#0!')
ZAPI_URL = "https://api.z-api.io/instances/3E17FEA36D1DF06641BB6260F2C0F8BD/token/D3E3CAA2F69A702A8D0278C4/send-text"

def fetch_verification_code():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=30)
        logging.info("Conexão IMAP estabelecida com imap.hostinger.com")
        
        # Usar variáveis de ambiente para login
        mail.login(IMAP_USER, IMAP_PASSWORD)
        logging.info("Login IMAP bem-sucedido")

        # Listar pastas IMAP para depuração
        status, folders = mail.list()
        if status == 'OK':
            logging.info(f"Pastas disponíveis: {folders}")
        else:
            logging.error(f"Erro ao listar pastas: {status}")

        # Selecionar a pasta 'INBOX' (padrão em inglês)
        status, data = mail.select('INBOX')
        if status != 'OK':
            raise Exception(f"Erro ao selecionar 'INBOX': {data}")
        logging.info("Pasta 'INBOX' selecionada com sucesso")

        # Busca por e-mails com "ChatGPT" no assunto
        search_criteria = '(SUBJECT "ChatGPT")'
        status, email_ids = mail.search(None, search_criteria)
        if status != 'OK':
            raise Exception(f"Erro na busca IMAP: {email_ids}")
        email_ids = email_ids[0].split()
        if not email_ids:
            raise Exception("Nenhum e-mail encontrado com o critério 'ChatGPT'")
        logging.info(f"E-mails encontrados: {len(email_ids)}")

        # Pegar o e-mail mais recente
        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        if status != 'OK':
            raise Exception(f"Erro ao buscar e-mail: {msg_data}")

        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_header(msg['subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        logging.info(f"Assunto do e-mail: {subject}")

        # Extrair o código de verificação do corpo do e-mail
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
                logging.info(f"Corpo do e-mail: {body}")
                code = re.search(r'\b\d{6}\b', body)
                if code:
                    logging.info(f"Código de verificação encontrado: {code.group()}")
                    return code.group()
        raise Exception("Nenhum código de verificação encontrado no e-mail")

    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        raise
    finally:
        try:
            mail.logout()
            logging.info("Logout IMAP realizado")
        except:
            pass

def send_whatsapp_code(code, phone):
    try:
        # Limpar espaços ou caracteres invisíveis no número de telefone
        phone = phone.strip()
        logging.info(f"Telefone recebido após limpeza: '{phone}'")  # Log para verificar o conteúdo do phone

        # Verificar se há algum caractere invisível ou extra
        if not phone.isprintable():
            raise Exception(f"Telefone contém caracteres não visíveis ou inválidos: {phone}")

        # Verifica se o número começa com "+" e tem exatamente 14 caracteres (considerando o "+55")
        if not phone.startswith('+') or len(phone) != 14:  # 14 caracteres no total, incluindo "+55"
            raise Exception("Número de telefone inválido. Formato esperado: +55XXXXXXXXXXX ou equivalente.")

        # Certificando-se de que o número começa com o código correto, como +55 para Brasil
        if not phone.startswith("+55"):
            raise Exception("Apenas números brasileiros são aceitos. O número deve começar com +55.")

        # Construir a mensagem a ser enviada
        message = f"Seu código de verificação: {code}"
        
        # Remover qualquer espaço ou caractere não imprimível da mensagem
        message = message.strip()
        if not message.isprintable():
            raise Exception(f"Mensagem contém caracteres não visíveis ou inválidos: {message}")

        # Verifique se o número e a mensagem estão corretamente definidos
        if not message or not phone:
            raise Exception("Parâmetros 'phone' ou 'message' estão vazios.")

        payload = {"phone": phone, "message": message}
        headers = {"Content-Type": "application/json"}

        logging.info(f"Enviando requisição para Z-API com dados: {payload}")

        # Enviar requisição para Z-API
        response = requests.post(ZAPI_URL, json=payload, headers=headers, timeout=10)

        # Verifique se a resposta da Z-API foi bem-sucedida
        if response.status_code == 200:
            logging.info("Mensagem WhatsApp enviada com sucesso via Z-API")
            return True
        else:
            logging.error(f"Erro ao enviar mensagem via Z-API: {response.status_code} - {response.text}")
            raise Exception(f"Erro ao enviar mensagem via Z-API: {response.text}")
    except Exception as e:
        logging.error(f"Erro ao enviar WhatsApp: {str(e)}")
        raise

@app.route('/get-verification-code', methods=['GET'])
def get_verification_code():
    try:
        phone = request.args.get('phone')
        phone = unquote(phone)  # Decodificar a URL codificada

        logging.info(f"Telefone recebido após decodificação: {phone}")

        if not phone:
            raise Exception("Número de telefone não fornecido na requisição")

        # Remover espaços ou caracteres não visíveis do número de telefone
        phone = phone.strip()
        
        # Validar número de telefone
        if not phone.startswith('+') or len(phone) != 14:
            raise Exception("Número de telefone inválido. Formato esperado: +55XXXXXXXXXXX ou equivalente.")

        code = fetch_verification_code()
        send_whatsapp_code(code, phone)

        return jsonify({"status": "success", "code": code}), 200
    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # A linha abaixo ativa o modo debug e hot-reload para reiniciar automaticamente o Flask ao salvar alterações
    port = int(os.environ.get("PORT", 5000))  # Ajuste para usar a variável PORT
    app.run(debug=True, port=port, host="0.0.0.0")
