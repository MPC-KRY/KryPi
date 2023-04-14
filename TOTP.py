import pyotp
import qrcode_terminal


def totp_generate_qrcode(key, name):
    qr_text = 'otpauth://totp/' + name + '?secret=' + key + '&issuer=KryPy'
    qrcode_terminal.draw(qr_text)


key = "tBMrJrDKlChPJ3pY"
totp = pyotp.TOTP(key)

totp_generate_qrcode(key, "xhynek11")

while True:
    old_TOTP = totp.now()
    print(totp.now())
    while True:
        if old_TOTP != totp.now():
            break