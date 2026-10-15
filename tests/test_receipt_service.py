from src.receipt_service import LiveEvent, Order, PlayerAsset, ModerationItem, receipt_html


def test_receipt_contains_order_and_live_event():
    order = Order("o-1", "player@example.com", [PlayerAsset("a", "Sky sword", 500)], LiveEvent("e", "Raid night"), [ModerationItem("a", "review")])
    html = receipt_html(order)
    assert "Receipt o-1" in html
    assert "Raid night" in html
    assert "Sky sword: $5.00" in html
