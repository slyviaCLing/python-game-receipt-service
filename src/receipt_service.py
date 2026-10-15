from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from .infrai_client import generate_pdf, send_email


@dataclass(frozen=True)
class PlayerAsset:
    asset_id: str
    title: str
    price_cents: int


@dataclass(frozen=True)
class LiveEvent:
    event_id: str
    name: str


@dataclass(frozen=True)
class ModerationItem:
    asset_id: str
    reason: str


@dataclass(frozen=True)
class Order:
    order_id: str
    player_email: str
    assets: List[PlayerAsset]
    event: LiveEvent
    moderation: List[ModerationItem]


def receipt_html(order: Order) -> str:
    rows = "".join(f"<li>{a.title}: ${a.price_cents / 100:.2f}</li>" for a in order.assets)
    return f"<h1>Receipt {order.order_id}</h1><p>Event: {order.event.name}</p><ul>{rows}</ul>"


def deliver_receipt(order: Order) -> Dict[str, Any]:
    html = receipt_html(order)
    pdf = generate_pdf(
        {"html": html, "page_size": "A4", "orientation": "portrait", "store": False},
        f"pdf-{order.order_id}",
    )
    subject = f"Receipt for order {order.order_id}"
    email = send_email(
        {"to": order.player_email, "subject": subject, "html": html},
        f"email-{order.order_id}",
    )
    return {"order_id": order.order_id, "message_id": email.get("message_id"), "pdf": pdf}
