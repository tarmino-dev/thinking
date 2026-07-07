"""Generate a note's header image with Cloudflare Workers AI and store it on R2.

A thin module (no service layer): Cloudflare Workers AI renders an image from a
Claude-crafted prompt, the bytes are uploaded to a Cloudflare R2 bucket, and the
object's public URL is returned for the note's ``img_url``. All credentials come
from the environment, so importing this module needs no keys or network access.
"""

import base64
import os
import uuid

import boto3
import requests

from app import ai

# Cloudflare Workers AI model. flux-1-schnell returns JSON with a base64 image.
CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_TIMEOUT = 60

_r2_client = None


def _env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value


def _get_r2_client():
    """Lazily create the S3-compatible client for Cloudflare R2."""
    global _r2_client
    if _r2_client is None:
        account_id = _env("CLOUDFLARE_ACCOUNT_ID")
        _r2_client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=_env("R2_ACCESS_KEY_ID"),
            aws_secret_access_key=_env("R2_SECRET_ACCESS_KEY"),
            region_name="auto",
        )
    return _r2_client


def _generate_bytes(prompt):
    """Render an image with Cloudflare Workers AI; return (data, content_type)."""
    account_id = _env("CLOUDFLARE_ACCOUNT_ID")
    token = _env("CLOUDFLARE_AI_API_TOKEN")
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{CF_MODEL}"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}"},
        json={"prompt": prompt},
        timeout=CF_TIMEOUT,
    )
    response.raise_for_status()
    image_b64 = (response.json().get("result") or {}).get("image")
    if not image_b64:
        raise RuntimeError("Cloudflare Workers AI returned no image")
    return base64.b64decode(image_b64), "image/jpeg"


def _upload(note_id, data, content_type):
    """Upload image bytes to R2 and return the object's public URL."""
    ext = "png" if content_type == "image/png" else "jpg"
    key = f"note-images/{note_id}-{uuid.uuid4().hex}.{ext}"
    _get_r2_client().put_object(
        Bucket=_env("R2_BUCKET"),
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    base = _env("R2_PUBLIC_BASE_URL").rstrip("/")
    return f"{base}/{key}"


def generate_note_image(note):
    """Craft a prompt, render the image, store it, and return its public URL.

    Raises on missing configuration or any provider error; the caller maps that
    to a user-facing flash message.
    """
    prompt = ai.image_prompt_for_note(note)
    data, content_type = _generate_bytes(prompt)
    return _upload(note.id, data, content_type)
