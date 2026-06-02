"""Cloudinary upload helpers."""

from __future__ import annotations

import logging
from typing import Any

import cloudinary
import cloudinary.uploader
from django.conf import settings

from core.exceptions import CloudinaryError

logger = logging.getLogger(__name__)


def _ensure_configured() -> None:
    if not settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'):
        try:
            from pathlib import Path
            import environ
            env_file = Path(settings.BASE_DIR) / '.env'
            if env_file.exists():
                env = environ.Env()
                env.read_env(env_file, overwrite=True)
                cloud_name = env.str('CLOUDINARY_CLOUD_NAME', default='')
                if cloud_name:
                    settings.CLOUDINARY_STORAGE['CLOUD_NAME'] = cloud_name
                    settings.CLOUDINARY_STORAGE['API_KEY'] = str(env('CLOUDINARY_API_KEY', default=''))
                    settings.CLOUDINARY_STORAGE['API_SECRET'] = env('CLOUDINARY_API_SECRET', default='')
        except Exception:
            pass

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', ''),
        api_key=settings.CLOUDINARY_STORAGE.get('API_KEY', ''),
        api_secret=settings.CLOUDINARY_STORAGE.get('API_SECRET', ''),
        secure=True,
    )


def upload_image(
    file_obj,
    *,
    folder: str = 'velora',
    public_id: str | None = None,
) -> dict[str, Any]:
    """
    Upload an image to Cloudinary.

    Returns a dict with at least ``url`` and ``public_id``.
    """
    _ensure_configured()
    if not settings.CLOUDINARY_STORAGE.get('CLOUD_NAME'):
        raise CloudinaryError('Cloudinary is not configured.')

    options: dict[str, Any] = {'folder': folder, 'resource_type': 'image'}
    if public_id:
        options['public_id'] = public_id

    try:
        result = cloudinary.uploader.upload(file_obj, **options)
        return {
            'url': result.get('secure_url') or result.get('url', ''),
            'public_id': result.get('public_id', ''),
            'width': result.get('width'),
            'height': result.get('height'),
            'format': result.get('format'),
        }
    except Exception as exc:
        logger.exception('Cloudinary upload failed')
        raise CloudinaryError(str(exc)) from exc


def delete_image(public_id: str) -> dict[str, Any]:
    """Delete an image from Cloudinary by public_id."""
    if not public_id:
        raise CloudinaryError('public_id is required for delete.')

    _ensure_configured()
    try:
        return cloudinary.uploader.destroy(public_id, resource_type='image')
    except Exception as exc:
        logger.exception('Cloudinary delete failed for %s', public_id)
        raise CloudinaryError(str(exc)) from exc
