"""Classes to manage invoices"""

import datetime
import decimal
from collections import OrderedDict
from pathlib import Path
from typing import TypedDict

import pystache  # type: ignore [import-untyped]

precision = decimal.Decimal("0.01")


def round_amount(number: float | decimal.Decimal) -> decimal.Decimal:
    return decimal.Decimal(number).quantize(precision)


class Prices:
    def __init__(self) -> None:
        self.items: dict[str, tuple[decimal.Decimal, str, str | None]] = OrderedDict()

    def add_price(self, item_id: str, price: float, description: str, group: str | None = None) -> None:
        self.items[item_id] = (round_amount(price), description, group)

    def get_price(self, item_id: str) -> decimal.Decimal:
        return self.items[item_id][0]

    def get_description(self, item_id: str) -> str:
        return self.items[item_id][1]

    def get_group_name(self, item_id: str) -> str | None:
        return self.items[item_id][2]


class Group(TypedDict):
    description: str
    price: decimal.Decimal
    amount: int
    total: decimal.Decimal


class Invoice:
    def __init__(self, prices: Prices, recipient: str, date_format: str = "%y-%m-%d") -> None:
        self.prices = prices
        self.recipient = recipient
        self.date_format = date_format
        self.groups: dict[str | None, dict[str, Group]] = OrderedDict()
        self.paid_amount = decimal.Decimal(0)
        self.remark = ""

    def add_items(self, item_id: str, amount: int = 1) -> None:
        if not amount:
            return

        group = self.prices.get_group_name(item_id)
        if group not in self.groups:
            self.groups[group] = {}

        price = self.prices.get_price(item_id)
        if item_id in self.groups[group]:
            self.groups[group][item_id]["amount"] += amount
            self.groups[group][item_id]["total"] += round(price * amount)
        else:
            self.groups[group][item_id] = {
                "description": self.prices.get_description(item_id),
                "price": price,
                "amount": amount,
                "total": price * amount,
            }

    def set_paid(self, amount: float) -> None:
        self.paid_amount = round_amount(amount)

    def set_remark(self, remark: str) -> None:
        self.remark = remark

    def get_total(self) -> decimal.Decimal:
        return round_amount(sum(item["total"] for group in self.groups.values() for item in group.values()))

    def check_total(self, total: float) -> bool:
        return round_amount(total) == self.get_total()

    def fill_template(
        self,
        template_file: Path,
        target_file: Path,
        labels: dict[str, str],
        *,
        reserve_space: bool = False,
    ) -> None:
        subtotal = self.get_total()
        data = {
            "date": datetime.date.today().strftime(self.date_format),
            "recipient": self.recipient,
            "labels": labels,
            "groups": [
                {
                    "group_name": group,
                    "items": [
                        self.groups[group][item_id] for item_id in self.prices.items if item_id in self.groups[group]
                    ],
                }
                for group in self.groups
            ],
            "subtotal": subtotal,
            "paid": self.paid_amount,
            "total": subtotal - self.paid_amount,
            "reserve_space": reserve_space,
            "remark": self.remark,
        }

        renderer = pystache.Renderer()
        template = renderer.load_template(template_file)
        invoice = renderer.render(template, data)

        with Path(target_file).open("w", encoding="utf-8") as target:
            target.write(invoice)
