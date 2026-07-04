# mailfold-client

Official Python client SDK for [Mailfold](https://github.com/isi1988/Mailfold) —
a self-hosted webmail/admin backend. This package wraps Mailfold's
machine-to-machine REST API (mail sending, folders, messages, search,
attachments, and flags) behind a small, typed Python client.

This is the **official client SDK** for the
[Mailfold project](https://github.com/isi1988/Mailfold). It has **zero
third-party runtime dependencies** — it only uses Python's standard library
(`urllib.request`, `json`).

## Why an API key instead of SMTP/IMAP?

You can always talk raw SMTP/IMAP to a mailbox — this API exists because it
removes work that protocol pair pushes onto every caller: one credential and
one HTTPS endpoint for both sending and reading (SMTP alone can't read),
never touching the real mailbox password (a leaked key is revoked on its
own, individually), built-in recipient/body-size caps and rate limiting, and
plain HTTPS on port 443 instead of mail ports (587/465/993) that plenty of
networks block outright. See the
[full rationale and capability list](https://github.com/isi1988/Mailfold#why-an-api-instead-of-talking-smtpimap-directly)
in the main project README.

**What this SDK can't do:** attach files when sending, move messages between
folders, create folders, touch calendars/contacts, or get real-time push for
new mail — those need a full webmail session, not an API key. See
["What an API key can and can't do"](https://github.com/isi1988/Mailfold#what-an-api-key-can-and-cant-do)
for the complete list.

## Install

```bash
pip install mailfold-client
```

(Import name is `mailfold`, package name on PyPI is `mailfold-client`.)

## Authentication

Every request is authenticated with a per-mailbox API key issued by your
Mailfold instance — an opaque bearer token that looks like
`mf_live_<kid>_<secret>`. Treat it as an opaque string; never parse it.

## Quickstart

```python
from mailfold import Client, MailfoldAPIError

client = Client(base_url="https://mail.example.com", api_key="mf_live_xxxxxxxxxxxxxxxx_yyyyy")

try:
    # Send a message (from address is always the mailbox bound to the API key)
    result = client.send(
        to=["alice@example.com"],
        cc=["bob@example.com"],
        subject="Hello from mailfold-client",
        text="Plain text body",
        html="<p>HTML body</p>",
    )
    print(result.status)  # "sent"

    # List folders
    for folder in client.folders():
        print(folder.name, folder.attributes)

    # List recent messages in a folder
    headers = client.messages(folder="INBOX", limit=20)
    for msg in headers:
        print(msg.uid, msg.subject, msg.seen)

    # Fetch a single full message
    if headers:
        msg = client.message(folder="INBOX", uid=headers[0].uid)
        print(msg.text, msg.attachments)

        # Download the first attachment, if any
        if msg.attachments:
            att = client.attachment(folder="INBOX", uid=msg.uid, index=0)
            print(att.filename, att.content_type, len(att.data))

    # Search
    results = client.search(folder="INBOX", q="invoice")
    print([m.subject for m in results])

    # Flag a message as seen
    if headers:
        client.set_flag(folder="INBOX", uid=headers[0].uid, flag="seen", set=True)

        # Delete a message
        client.delete_message(folder="INBOX", uid=headers[0].uid)

except MailfoldAPIError as e:
    print(e.status_code, e.message, e.retry_after)
```

## API surface

| Method | Endpoint | Scope |
|---|---|---|
| `client.send(to=, cc=, bcc=, subject=, text=, html=)` | `POST /api/v1/mail/send` | `mail:send` |
| `client.folders()` | `GET /api/v1/mail/folders` | `mail:read` |
| `client.messages(folder=, limit=)` | `GET /api/v1/mail/messages` | `mail:read` |
| `client.message(folder, uid)` | `GET /api/v1/mail/message` | `mail:read` |
| `client.delete_message(folder, uid)` | `DELETE /api/v1/mail/message` | `mail:write` |
| `client.search(folder=, q=)` | `GET /api/v1/mail/search` | `mail:read` |
| `client.attachment(folder, uid, index)` | `GET /api/v1/mail/attachment` | `mail:read` |
| `client.set_flag(folder, uid, flag, set)` | `POST /api/v1/mail/flag` | `mail:write` |

## Error handling

Any non-2xx response raises `mailfold.MailfoldAPIError` with:

- `status_code` — the HTTP status code (400, 401, 403, 413, 429, 502)
- `message` — the server's `"error"` message string
- `retry_after` — the `Retry-After` header value in seconds, when present (429 responses)

A `mailfold.MailfoldConnectionError` is raised if the request cannot reach the
server at all (network failure, DNS, timeout, etc).

## About Mailfold

Mailfold is a self-hosted webmail/admin backend. See the main project at
**https://github.com/isi1988/Mailfold**.

## License

MIT — see [LICENSE](./LICENSE).
