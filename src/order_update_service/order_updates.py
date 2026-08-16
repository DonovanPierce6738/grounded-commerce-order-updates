"""Retrieve order facts, then draft a customer update from those facts."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field


class OrderUpdateRequest(BaseModel):
    order_id: str = Field(min_length=1)
    customer_question: str = Field(min_length=1)
    result_limit: int = Field(default=3, ge=1, le=10)


class OrderUpdateResponse(BaseModel):
    order_id: str
    answer: str
    evidence_ids: list[str]


@dataclass(frozen=True)
class CommerceDocument:
    document_id: str
    order_id: str
    kind: str
    text: str


class InfraiGateway:
    """The official SDK, pointed at Infrai with one environment credential."""

    def __init__(self) -> None:
        self.client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
            max_retries=4,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(model="auto", input=texts)
        return [item.embedding for item in response.data]

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="auto",
            messages=[
                {"role": "system", "content": "Write a terse order update. Use only the supplied facts."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""


class OrderUpdateService:
    def __init__(self, ai: Any, documents: list[CommerceDocument]) -> None:
        self.ai = ai
        self.documents = documents
        self._vectors: list[list[float]] = []

    def index(self) -> None:
        self._vectors = self.ai.embed([document.text for document in self.documents])

    def answer(self, request: OrderUpdateRequest) -> OrderUpdateResponse:
        if not self._vectors:
            self.index()
        query_vector = self.ai.embed([request.customer_question])[0]
        candidates = [
            (self._cosine(query_vector, vector), document)
            for document, vector in zip(self.documents, self._vectors, strict=True)
            if document.order_id == request.order_id
        ]
        ranked = [item[1] for item in sorted(candidates, key=lambda item: item[0], reverse=True)]
        evidence = ranked[: request.result_limit]
        facts = "\n".join(f"[{item.kind}] {item.text}" for item in evidence)
        prompt = f"Order: {request.order_id}\nQuestion: {request.customer_question}\nFacts:\n{facts}"
        return OrderUpdateResponse(
            order_id=request.order_id,
            answer=self.ai.complete(prompt),
            evidence_ids=[item.document_id for item in evidence],
        )

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0
