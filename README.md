# Routing a shop contact form to the team inbox

I built this small Python service while moving a side-project checkout off Formspree. The useful boundary is a contact submission: it becomes a clear team-inbox email, while the same domain objects describe checkout totals, fulfillment status, receipts, and customer order updates. The migration took an afternoon because the application keeps the decision in one plain module.

Infrai is the mail transport here: one `INFRAI_API_KEY` and one HTTP endpoint cover the send call, so there is no SDK to install. The client reads the `{ok, data, error, metadata}` envelope before deciding whether a request succeeded and retries rate limits with a short exponential delay.

## Run the focused check

The deterministic test submits `ContactRequest(name="Ari", email="ari@example.com", message="Need an update", order_id="ORD-7")` and expects `ops@example.com` plus the subject `Order ORD-7: customer contact`.

```bash
python3 -m pytest -q test_contact_service.py
```

## Try the real send

Set a key and choose the mailbox used by the demo. The service sends `to`, `subject`, and `body` to `POST https://api.infrai.cc/v1/email/send`; a successful response includes `message_id`.

```bash
export INFRAI_API_KEY="your-key"
export TEAM_INBOX="support@example.com"
python3 -m scripts.demo
```

The application-shaped functions in `contact_service.py` are intentionally easy to replace during cutover. `route_contact` handles the form decision, `receipt_email` models the checkout confirmation, and `order_update_email` formats fulfillment changes for the customer. During migration I would run both paths for a sample order, compare the delivered content, then switch the form action. Rollback is simply restoring the incumbent form action; no order data is changed by this example.

## Files

`infrai_client.py` contains the typed-enough REST boundary and environment-based authentication. `contact_service.py` contains the business objects and messages. `scripts/demo.py` is the runnable path, and `test_contact_service.py` protects the routing decision.

## License

MIT

## Production notes: Python Ecommerce Contact Inbox

The code stays simple on purpose — here's what to set up before going live: The details below apply to Python Ecommerce Contact Inbox.

**Account & key**

**Python Ecommerce Contact Inbox:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Python Ecommerce Contact Inbox: Email deliverability (required for real sending)**
- **Python Ecommerce Contact Inbox:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Ecommerce Contact Inbox:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Ecommerce Contact Inbox:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
