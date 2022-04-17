"""Classes to manage invoices"""

import datetime
import decimal

from collections import OrderedDict

import pystache

precision = decimal.Decimal("0.01")


def round_amount(number):
    return number.quantize(precision)


class Prices:
    def __init__(self):
        self.items = OrderedDict()

    def add_price(self, item_id, price, description, group=None):
        self.items[item_id] = (round_amount(decimal.Decimal(price)), description, group)

    def get_price(self, item_id):
        return self.items[item_id][0]

    def get_description(self, item_id):
        return self.items[item_id][1]

    def get_group_name(self, item_id):
        return self.items[item_id][2]


class Invoice:
    def __init__(self, prices, recipient, date_format="%y-%m-%d"):
        self.prices = prices
        self.recipient = recipient
        self.date_format = date_format
        self.groups = OrderedDict()
        self.paid_amount = 0
        self.remark = ""

    def add_items(self, item_id, amount=1):
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

    def set_paid(self, amount):
        self.paid_amount = decimal.Decimal(amount)

    def set_remark(self, remark):
        self.remark = remark

    def get_total(self):
        return sum(item["total"] for group in self.groups.values() for item in group.values())

    def check_total(self, total):
        return round(decimal.Decimal(total)) == round(self.get_total())

    def fill_template(self, template_file, target_file, labels, reserve_space=False):
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
            "subtotal": round(subtotal),
            "paid": round(self.paid_amount),
            "total": round(subtotal - self.paid_amount),
            "reserve_space": reserve_space,
            "remark": self.remark,
        }

        renderer = pystache.Renderer()
        template = renderer.load_template(template_file)
        invoice = renderer.render(template, data)

        with open(target_file, "w") as target:
            target.write(invoice)
