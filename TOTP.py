import qrcode_terminal


def totp_generate_qrcode(key, name):
    qr_text = 'otpauth://totp/' + name + '?secret=' + key + '&issuer=KryPy'
    qrcode_terminal.draw(qr_text)
