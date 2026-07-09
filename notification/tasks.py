import logging

import requests
from celery import shared_task
from django.conf import settings

from .validators import normalize_rwandan_phone

logger = logging.getLogger(__name__)

EVENT_LABELS = {
    'registered': 'registered',
    'arrived': 'arrived at the destination branch',
    'delivered': 'delivered to the receiver',
}


def _build_tracking_url(tracking_number, tracking_url):
    if not tracking_url:
        return tracking_number
    return f"{tracking_url.rstrip('/')}/track/{tracking_number}/"


def _build_message(event, tracking_number, tracking_url):
    action = EVENT_LABELS.get(event, event)
    target_url = _build_tracking_url(tracking_number, tracking_url)
    return (
        f"Your package {tracking_number} has been {action}. "
        f"Track it here: {target_url}"
    )


def _send_sms_request(phone_number, message):
    gateway_url = getattr(settings, 'SMS_GATEWAY_URL', '')
    api_key = getattr(settings, 'SMS_GATEWAY_API_KEY', '')

    if not gateway_url or not api_key:
        logger.warning('SMS gateway not configured: missing URL or API key.')
        return None

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    payload = {
        'phoneNumber': phone_number,
        'message': message,
    }

    logger.info('Sending SMS request to gateway %s for phone %s.', gateway_url, phone_number)
    response = requests.post(gateway_url, headers=headers, json=payload, timeout=15)
    logger.info('SMS Gateway Response: %s - %s', response.status_code, response.text)
    response.raise_for_status()
    logger.info('Sent SMS to %s for package event.', phone_number)
    return response


@shared_task(bind=True, autoretry_for=(requests.exceptions.RequestException,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_package_event_sms(self, event, sender_phone, receiver_phone, tracking_number, tracking_url):
    logger.info(
        'send_package_event_sms called: event=%s sender_phone=%s receiver_phone=%s tracking_number=%s',
        event,
        sender_phone,
        receiver_phone,
        tracking_number,
    )
    message = _build_message(event, tracking_number, tracking_url)

    for role, phone in [('sender', sender_phone), ('receiver', receiver_phone)]:
        normalized_phone = normalize_rwandan_phone(phone)
        if not normalized_phone:
            logger.warning('Skipping SMS for invalid %s phone number: %s', role, phone)
            continue

        try:
            _send_sms_request(normalized_phone, message)
        except requests.exceptions.RequestException as exc:
            logger.exception('SMS send failed for %s phone %s.', role, normalized_phone)
            raise self.retry(exc=exc)
