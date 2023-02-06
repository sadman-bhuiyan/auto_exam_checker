from pyzbar.pyzbar import decode
import json

def read_barcode(image,mark):
    qr_code_data = json.loads(decode(image)[0].data.decode("utf-8").strip().rstrip().replace("\n", "").replace(',}', '}'))
    qr_code_data['mark'] = mark
    return qr_code_data
