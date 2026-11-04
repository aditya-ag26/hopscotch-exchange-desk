import re

ORDER_ID = re.compile(r"\bHS\d{4}\b", re.IGNORECASE)

TOPIC = re.compile(
    r"\b(order|exchange|return|refund|replace|size|pick\s?up|broke|broken|damaged|torn|defect)",
    re.IGNORECASE,
)

LINK = re.compile(r"https?://", re.IGNORECASE)


def gate(message: str) -> str:
    text = message.strip()
    if len(text) < 10:
        return "rejected: message too short"
    if len(text) > 1500:
        return "rejected: message too long"
    if LINK.search(text):
        return "rejected: contains a link"
    if not ORDER_ID.search(text) and not TOPIC.search(text):
        return "rejected: not an exchange or return request"
    return "accepted"


if __name__ == "__main__":
    print(gate("hi"))
    print(gate("Do you have any Diwali offers on party wear this week?"))
    print(gate("Order HS2291 is too small, see https://bit.ly/x1"))
    print(gate("Order HS2291. The 4-5Y kurta set is too small."))
