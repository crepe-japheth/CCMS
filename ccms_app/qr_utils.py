import io

import qrcode
from qrcode.constants import ERROR_CORRECT_M


def generate_qr_png(tracking_number):
    """Return QR code PNG bytes encoding the tracking number."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(tracking_number)
    qr.make(fit=True)
    image = qr.make_image(fill_color='#1e2a4a', back_color='white')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()
