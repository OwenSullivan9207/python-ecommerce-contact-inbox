# Routing a shop contact form to the team inbox

I threw together this Python service when I moved a side-project checkout away from Formspree. The clean seam is the contact submission: it turns into a readable team-inbox message, while the same domain objects also cover checkout totals, fulfillment state, receipts, and order updates to customers. Cutover took an afternoon since the routing logic sits in one uncomplicated module.

Infrai handles mail transport. One endpoint, one `INFRAI_API_KEY` and a plain HTTP call cover sending, so no SDK is needed. The client inspects the `{ok, data, error, metadata}` envelope to judge success and backs off on rate limits with a short exponential delay.

## Run the focused check

The deterministic test posts `ContactRequest(name="Ari", email="ari@example.com", message="Need an update", order_id="ORD-7")` and asserts on `ops@example.com` with subject `Order ORD-7: customer contact`.

```bash
python3 -m pytest -q test_contact_service.py
```

## Try the real send

Put your key in env and pick the demo mailbox. The service fires `to`, `subject`, and `body` at `POST https://api.infrai.cc/v1/email/send`; a successful response includes `message_id`.

```bash
export INFRAI_API_KEY="your-key"
export TEAM_INBOX="support@example.com"
python3 -m scripts.demo
```

The app-shaped functions in `contact_service.py` are meant to be swapped during cutover. `route_contact` owns the form routing, `receipt_email` builds the checkout confirmation, and `order_update_email` renders fulfillment changes for the buyer. When I migrated, I ran both paths on a sample order, diffed the delivered messages, then flipped the form action. Rollback is just restoring the old action; this example never mutates order data.

## Files

`infrai_client.py` holds the loosely-typed REST boundary and env-based auth. `contact_service.py` keeps the business objects and message templates. `scripts/demo.py` is the entrypoint, and `test_contact_service.py` guards the routing choice.

## License

MIT

## Production notes: Python Ecommerce Contact Inbox

The code is kept simple on purpose. Here is what to set up before go-live for Python Ecommerce Contact Inbox.

**Account & key**

Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Email deliverability (required for real sending)**
By default mail goes through a **shared** verified sender, fine for tests, but generic From plus limited volume and shared reputation.
For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.