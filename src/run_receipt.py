from __future__ import annotations

import json
import os

from .receipt_service import LiveEvent, Order, PlayerAsset, ModerationItem, deliver_receipt


def main() -> None:
    order = Order(
        order_id="order-2048",
        player_email=os.environ["INFRAI_RECIPIENT_EMAIL"],
        assets=[PlayerAsset("skin-7", "Aurora skin", 1299)],
        event=LiveEvent("season-4", "Season 4 launch"),
        moderation=[ModerationItem("skin-7", "queued for review")],
    )
    print(json.dumps(deliver_receipt(order), indent=2, default=str))


if __name__ == "__main__":
    main()
