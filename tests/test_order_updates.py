from src.order_update_service import CommerceDocument, OrderUpdateRequest, OrderUpdateService


class DeterministicAi:
    def __init__(self) -> None:
        self.prompt = ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] if "shipped" in text or "left" in text else [0.0, 1.0] for text in texts]

    def complete(self, prompt: str) -> str:
        self.prompt = prompt
        return "ORD-1042 has shipped."


def test_update_uses_relevant_facts_from_the_requested_order() -> None:
    ai = DeterministicAi()
    service = OrderUpdateService(
        ai,
        [
            CommerceDocument("ship-1042", "ORD-1042", "fulfillment", "ORD-1042 left the warehouse."),
            CommerceDocument("pay-1042", "ORD-1042", "checkout", "Payment for ORD-1042 was accepted."),
            CommerceDocument("ship-1043", "ORD-1043", "fulfillment", "ORD-1043 left the warehouse."),
        ],
    )

    result = service.answer(OrderUpdateRequest(order_id="ORD-1042", customer_question="Has it shipped?", result_limit=1))

    assert result.evidence_ids == ["ship-1042"]
    assert "ORD-1042 left the warehouse" in ai.prompt
    assert "ORD-1043" not in ai.prompt
