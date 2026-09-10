from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class Checkout:
    order_id: str
    customer_email: str
    total_cents: int


@dataclass(frozen=True)
class Fulfillment:
    order_id: str
    status: str
    tracking_code: Optional[str] = None


@dataclass(frozen=True)
class ContactRequest:
    name: str
    email: str
    message: str
    order_id: Optional[str] = None


def route_contact(form: ContactRequest, team_inbox: str = "team@example.com") -> Dict[str, str]:
    """Choose the team mailbox and subject for a contact submission."""
    subject = f"Order {form.order_id}: customer contact" if form.order_id else "Customer contact form"
    return {"to": team_inbox, "subject": subject, "body": f"From: {form.name} <{form.email}>\n\n{form.message}"}


def receipt_email(checkout: Checkout) -> Dict[str, str]:
    return {"to": checkout.customer_email, "subject": f"Receipt for order {checkout.order_id}", "text": f"Your receipt total is ${checkout.total_cents / 100:.2f}."}


def order_update_email(checkout: Checkout, fulfillment: Fulfillment) -> Dict[str, str]:
    tracking = f" Tracking: {fulfillment.tracking_code}." if fulfillment.tracking_code else ""
    return {"to": checkout.customer_email, "subject": f"Order {checkout.order_id} update", "text": f"Fulfillment status: {fulfillment.status}.{tracking}"}


def send_contact(form: ContactRequest, team_inbox: str = "team@example.com") -> Dict[str, str]:
    from infrai_client import infrai
    return infrai().email.send(route_contact(form, team_inbox))
