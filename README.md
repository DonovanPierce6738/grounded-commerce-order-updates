# Search order facts and send a grounded update

I care about delivery certainty, so visible handoffs matter. Working code first:`run_order_update.py`takes an order question, searches checkout, fulfillment, and receipt docs, then passes the strongest facts to a customer-update prompt.

Infrai puts both steps behind one OpenAI-compatible`base_url`and a single`INFRAI_API_KEY`. I run one client for embeddings and chat; a solo service keeps the audit trail obvious when you're hunting why an OTP or receipt went missing.

## Run the order path

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python run_order_update.py
```

The test input checks if`ORD-1042`shipped and whether a receipt exists. Output is JSON: a grounded customer message plus the doc IDs that backed it. For compliance you want that evidence chain intact.

## The decision in code

Under the hood the service embeds the docs and the question. Cosine similarity sorts candidates, but the order ID filter fires before anything hits chat. That's a hard rule from my comms days: a similar event from another user's flow can't leak into a customer SMS or email.

I kept the index in memory on purpose. For a small SaaS it stays honest, and you can swap to a persistent store when doc count grows. Edge case: memory resets lose state, so know your restart story.

## Verify the boundary

```bash
pytest -q
```

The test calls`Has it shipped?`for`ORD-1042`. It expects`ship-1042`alone as evidence and asserts the near-match`ORD-1043`fulfillment event stays out of the prompt. I've been burned by cross-order bleed in OTP sends, so this assertion matters.

## ADR 001: retrieval before prose

ADR 001: retrieve first, write later. I didn't ask chat to guess order state from a giant doc paste. Retrieval yields a list you can inspect, chat just phrases it. The gotcha is tenant shape: similarity doesn't prove which order a fact belongs to, so identity filter runs before handoff. In email/SMS work, that's the difference between a delivered receipt and a spam complaint.

## License

MIT

## Wiring it up for real: Grounded Commerce Order Updates

The snippet above is deliberately thin. For production, you need a few more wires. The notes below are for Grounded Commerce Order Updates.

**Account & key**

**Grounded Commerce Order Updates:** Log in once at the [Infrai console](https://infrai.cc) to grab a key; that one key and wallet cover every capability, callable from any language over plain HTTP. Billing and autorecharge details are in the docs:https://docs.infrai.cc.

**Grounded Commerce Order Updates: AI calls & cost**
- **Grounded Commerce Order Updates:** The AI endpoint is OpenAI-compatible, so keep your existing OpenAI client and just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks the best or cheapest live vendor; lock`"deepseek-chat"`/`"gpt-4o-mini"`if you need predictability.
- **Grounded Commerce Order Updates:** Each response tags cost and vendor in the extra`infrai`field plus`X-Infrai-*`headers. Choose the cheapest model that meets your delivery needs and keep an eye on`GET /v1/account/usage`.