"""Brevo (Sendinblue) email integration."""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from sib_api_v3_sdk import ApiClient, Configuration, SendSmtpEmail, TransactionalEmailsApi
from sib_api_v3_sdk.rest import ApiException

from core.exceptions import BrevoError

logger = logging.getLogger(__name__)


class BrevoClient:
    """Thin wrapper around the official Brevo transactional email API."""

    def __init__(
        self,
        api_key: str | None = None,
        sender_email: str | None = None,
        sender_name: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.BREVO_API_KEY
        self.sender_email = sender_email or settings.BREVO_SENDER_EMAIL
        self.sender_name = sender_name or settings.BREVO_SENDER_NAME
        configuration = Configuration()
        configuration.api_key['api-key'] = self.api_key
        self._api = TransactionalEmailsApi(ApiClient(configuration))

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        *,
        to_name: str | None = None,
        text_content: str | None = None,
    ) -> dict[str, Any]:
        """Send a transactional email via Brevo."""
        if not self.api_key:
            if settings.DEBUG:
                import sys
                sys.stdout.write(
                    f"\n=======================================================\n"
                    f"[SANDBOX EMAIL OUTBOX]\n"
                    f"To: {to_email}\n"
                    f"Subject: {subject}\n"
                    f"Body:\n{_strip_html(html_content)}\n"
                    f"=======================================================\n\n"
                )
                sys.stdout.flush()
                return {'status': 'sent', 'sandbox': True}
            raise BrevoError('BREVO_API_KEY is not configured.')

        recipient = {'email': to_email}
        if to_name:
            recipient['name'] = to_name

        payload = SendSmtpEmail(
            to=[recipient],
            sender={'email': self.sender_email, 'name': self.sender_name},
            subject=subject,
            html_content=html_content,
            text_content=text_content or _strip_html(html_content),
        )

        try:
            response = self._api.send_transac_email(payload)
            return response.to_dict() if hasattr(response, 'to_dict') else {'status': 'sent'}
        except ApiException as exc:
            logger.exception('Brevo send_email failed for %s', to_email)
            raise BrevoError(str(exc)) from exc

    def send_otp_email(self, to_email: str, otp_code: str, *, expiry_minutes: int | None = None) -> dict[str, Any]:
        """Send a one-time password verification email (Phase 0 template stub)."""
        minutes = expiry_minutes if expiry_minutes is not None else settings.OTP_EXPIRY_MINUTES
        subject = 'Your Velora verification code'
        html_content = (
            f'<p>Your Velora verification code is:</p>'
            f'<p style="font-size:24px;font-weight:bold;letter-spacing:4px">{otp_code}</p>'
            f'<p>This code expires in {minutes} minutes. '
            f'If you did not request this, you can ignore this email.</p>'
        )
        return self.send_email(to_email, subject, html_content)


def _strip_html(html: str) -> str:
    """Minimal plain-text fallback for transactional emails."""
    return (
        html.replace('<p>', '')
        .replace('</p>', '\n')
        .replace('<br>', '\n')
        .replace('<br/>', '\n')
        .strip()
    )
