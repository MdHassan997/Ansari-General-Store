import hmac
import hashlib
import requests
from config import Config

def create_razorpay_order(amount_inr, order_id, currency='INR'):
    try:
        amount_paise = int(float(amount_inr) * 100)
        data = {
            'amount': amount_paise,
            'currency': currency,
            'receipt': str(order_id),
            'payment_capture': 1
        }
        response = requests.post(
            'https://api.razorpay.com/v1/orders',
            json=data,
            auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET)
        )
        result = response.json()
        if 'id' in result:
            return {'success': True, 'order': result}
        else:
            return {'success': False, 'error': str(result)}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def verify_razorpay_payment(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    try:
        key_secret = Config.RAZORPAY_KEY_SECRET.encode('utf-8')
        message = f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8')
        generated_signature = hmac.new(
            key_secret, message, hashlib.sha256
        ).hexdigest()
        return generated_signature == razorpay_signature
    except Exception:
        return False

def get_payment_config():
    return {
        'key_id': Config.RAZORPAY_KEY_ID,
        'currency': Config.CURRENCY,
        'currency_symbol': Config.CURRENCY_SYMBOL,
        'store_name': Config.STORE_NAME
    }
