"""
WhatsApp Business API webhook — placeholder for future implementation.

This module provides the webhook endpoints needed to integrate with
the WhatsApp Business API (Meta Cloud API). The verification endpoint
is functional; the message handler is a stub for future development.
"""

from fastapi import APIRouter, Query, HTTPException, Request

from src.config import WHATSAPP_VERIFY_TOKEN

router = APIRouter()


@router.get("/api/webhook/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """Verification endpoint for WhatsApp webhook setup."""
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/api/webhook/whatsapp")
async def receive_whatsapp_message(request: Request):
    """
    Receives incoming WhatsApp messages.

    TODO: Implement message parsing, agent response, and reply via
    WhatsApp Business API.
    """
    body = await request.json()
    # Future: parse message, call agent_chain.chat(), send reply
    return {"status": "received"}
