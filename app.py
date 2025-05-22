import imaplib
import email
from email.header import decode_header
import re
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Configurações IMAP
imap_server = "imap.hostinger.com"
imap_user = "chatgpt@adninjas.pro"
imap_password = "Keylogger#0!"

def fetch_verification_code():
    try:
        # Conectar ao servidor IMAP
        mail = imaplib.IMAP4_SSL(imap_server, timeout=30)
        logging.info("Conexão IMAP estabelecida")
        mail.login(imap_user, imap_password)
        logging.info("Login IMAP bem-sucedido")

        # Selecionar a pasta
        status, data = mail.select('Caixa de entrada')
        if status != 'OK':
            raise Exception(f"Erro ao selecionar 'Caixa de entrada': {data}")
        logging.info("Pasta 'Caixa de entrada' selecionada com sucesso")

        # Buscar e-mails com assunto contendo "verification" ou "code" (mais flexível)
        search_criteria = '(SUBJECT "verification" OR SUBJECT "code")'
        status, email_ids = mail.search(None, search_criteria)
        if status != 'OK':
            raise Exception(f"Erro na busca IMAP: {email_ids}")
        email_ids = email_ids[0].split()
        if not email_ids:
            raise Exception("Nenhum e-mail encontrado com os critérios de busca")
        logging.info(f"E-mails encontrados: {len(email_ids)}")

        # Processar o e-mail mais recente
        latest_email_id = email_ids[-1]
        status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
        if status != 'OK':
            raise Exception(f"Erro ao buscar e-mail: {msg_data}")

        # Extrair o conteúdo do e-mail
        msg = email.message_from_bytes(msg_data[0][1])
        subject = decode_header(msg['subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        logging.info(f"Assunto do e-mail: {subject}")

        # Extrair o código (6 dígitos)
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
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
        except:
            pass

# Executar o fluxo
if __name__ == "__main__":
    try:
        code = fetch_verification_code()
        print(f"Código extraído: {code}")
    except Exception as e:
        print(f"Falha: {str(e)}")