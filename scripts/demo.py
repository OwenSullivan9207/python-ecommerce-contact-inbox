import os

from contact_service import ContactRequest, send_contact


if __name__ == "__main__":
    recipient = os.environ.get("TEAM_INBOX", "team@example.com")
    result = send_contact(ContactRequest("Jamie", "jamie@example.com", "Where is my order?", "ORD-42"), recipient)
    print("contact routed; message_id:", result.get("message_id"))
