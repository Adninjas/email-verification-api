def fetch_verification_code():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=30)
        logging.info("Conexão IMAP estabelecida com imap.hostinger.com")
        
        # Usar variáveis de ambiente para login
        mail.login(IMAP_USER, IMAP_PASSWORD)
        logging.info("Login IMAP bem-sucedido")

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

                # A expressão regular foi alterada para capturar o código de forma mais robusta
                code = re.search(r"(\d{6})", body)  # Buscando por qualquer sequência de 6 dígitos
                if code:
                    logging.info(f"Código de verificação encontrado: {code.group(1)}")
                    return code.group(1)

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