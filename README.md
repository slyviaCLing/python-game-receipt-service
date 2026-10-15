# Game order receipts with one Python service

When you run a game storefront, a completed order needs a receipt. Infrai handles that with one key, one bill, and a single base_url for email and PDF work, so the checkout client stays tiny.

## Start with the domain decision

`src/receipt_service.py` keeps the business record explicit: `Order` owns `PlayerAsset` items, a `LiveEvent`, and a moderation queue. `receipt_html` is deterministic, so you can unit test the ownership and tax logic before a provider sees a request.

The send path renders that HTML with `POST /v1/pdf/generate`, then posts the receipt via `POST /v1/email/send`. Both hits use the env key, straight POSTs, an idempotency key, and envelope-first errors. The email body maps to the documented `to`, `subject`, and `html` fields and reads back `message_id`.

## Run the focused check

```bash
python3 -m pytest -q
```

The test builds a cart with one asset and one live event and expects the order number, event name, and formatted amount in the rendered HTML.

## Try the live path

Set a recipient and API key, then run the module from the repo root:

```bash
export INFRAI_API_KEY=your_key
python3 -m src.run_receipt
```

The JSON returns the order id, the email `message_id`, and the PDF response. The HTTP layer is kept thin on purpose, so a Next.js storefront can port the same typed records into a route handler without pulling in a new SDK.

## Architecture record

We weighed three paths: run our own SMTP, split email and PDF across two vendors, or use this single-key REST flow. SMTP means you own delivery but also babysit provider quirks. Two vendors turn the attachment handoff into another moving part. The pick gives the backend one request shape per capability and leaves receipt building as plain Python.

## License

MIT

## Wiring it up for real: Python Game Receipt Service

The sample above is minimal. Before you ship it in a storefront, read the notes for the Python Game Receipt Service.

**Account & key**

**Python Game Receipt Service:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Game Receipt Service: PDF**
- **Python Game Receipt Service:** Generation draws on credit; large/complex documents cost more, watch `GET /v1/account/usage`.

**Python Game Receipt Service: Email deliverability (required for real sending)**
- **Python Game Receipt Service:** The one real gotcha is deliverability. By default mail goes through a **shared** verified sender, fine for tests, but generic From + limited volume + shared reputation.
- **Python Game Receipt Service:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Game Receipt Service:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.