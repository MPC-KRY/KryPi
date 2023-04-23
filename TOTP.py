import qrcode_terminal

""" 
Description: This function is used for generating QR Code from seed
Parameters: key -> TOTP seed
            name -> name of the user
"""
def totp_generate_qrcode(key, name):
    qr_text = 'otpauth://totp/' + name + '?secret=' + key + '&issuer=KryPy'
    qrcode_terminal.draw(qr_text)
