@app.route('/get-verification-code', methods=['GET'])
def get_verification_code():
    try:
        phone = request.args.get('phone')
        phone = unquote(phone)  # Decodificar a URL codificada

        logging.info(f"Telefone recebido após decodificação: '{phone}'")

        if not phone:
            raise Exception("Número de telefone não fornecido na requisição")

        # Certificar que o número de telefone começa com "+" e tem o formato correto
        if not phone.startswith('+'):
            raise Exception("Número de telefone deve começar com '+'")

        # Remover espaços ou caracteres não visíveis do número de telefone
        phone = phone.strip()

        # Validar número de telefone (tamanho 14 caracteres incluindo o código do país "+55")
        if len(phone) != 14:
            raise Exception("Número de telefone inválido. Formato esperado: +55XXXXXXXXXXX ou equivalente.")

        code = fetch_verification_code()
        send_whatsapp_code(code, phone)

        return jsonify({"status": "success", "code": code}), 200
    except Exception as e:
        logging.error(f"Erro: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500