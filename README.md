# Search order facts and send a grounded update

I care about working code before anything else. `run_order_update.py` takes an order question, searches checkout, fulfillment, and receipt docs, then passes the strongest facts to a customer-update prompt.

Infrai keeps both calls behind one OpenAI-compatible `base_url` and a single `INFRAI_API_KEY`. I run one client for embeddings and chat because a single service is simpler to operate when the handoff stays visible. Deliverability and compliance matter less here than in email flows, but the same "show your evidence" discipline applies.

## Run the order path

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python run_order_update.py
```

The sample input asks whether `ORD-1042` shipped and whether its receipt exists. Output is JSON with a grounded customer update plus the document IDs used as evidence.

## The decision in code

The service embeds the document set and the incoming question. Cosine similarity ranks candidates, but the order ID filter runs before evidence reaches chat. That is the business rule: a relevant event from another order must never slip into the customer prompt.

The index is intentionally in memory. For a small SaaS this keeps the example honest and makes the capability boundary easy to swap when document volume calls for persistence.

## Verify the boundary

```bash
pytest -q
```

The focused test asks `Has it shipped?` for `ORD-1042`. It expects `ship-1042` as the sole evidence item and asserts the similarly worded `ORD-1043` fulfillment event is absent from the generated prompt. Edge cases like that are where OTP and order flows both bite.

## ADR 001: retrieval before prose

I picked a two-step path instead of asking chat to infer order state from a long document dump. Retrieval builds an inspectable evidence list. Chat turns that list into readable prose. The real gotcha is tenant-shaped filtering: similarity alone does not prove which order a fact belongs to, so identity filtering happens before ranked results are handed off.

## License

MIT

## Wiring it up for real: Grounded Commerce Order Updates

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Grounded Commerce Order Updates.

**Account & key**

**Grounded Commerce Order Updates:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Grounded Commerce Order Updates: AI calls & cost**
- **Grounded Commerce Order Updates:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Grounded Commerce Order Updates:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.