import json

from src.order_update_service import CommerceDocument, InfraiGateway, OrderUpdateRequest, OrderUpdateService


documents = [
    CommerceDocument("checkout-1042", "ORD-1042", "checkout", "Payment was accepted for order ORD-1042."),
    CommerceDocument("fulfillment-1042", "ORD-1042", "fulfillment", "Order ORD-1042 left the warehouse with carrier North Parcel."),
    CommerceDocument("receipt-1042", "ORD-1042", "receipt", "Receipt R-778 was issued for order ORD-1042."),
    CommerceDocument("fulfillment-1043", "ORD-1043", "fulfillment", "Order ORD-1043 is waiting for warehouse pickup."),
]
service = OrderUpdateService(InfraiGateway(), documents)
result = service.answer(
    OrderUpdateRequest(order_id="ORD-1042", customer_question="Has my order shipped, and is there a receipt?")
)
print(json.dumps(result.model_dump(), indent=2))
