#!/usr/bin/env python3
"""Price a direct mail campaign as an hourly rate, first card versus renewal.

Every Door Direct Mail revenue looks like gross dollars per card. The honest
number is margin divided by all the hours the card consumed, selling included.
This tool takes one campaign's cash lines and hour lines and returns the
effective rate for a one-off card and for the same card on renewal, where the
prospecting clock collapses to a short retention round.

Usage:
    python3 directmail_pricer.py --spots 16 --spot-price 150 --postage 550 \
        --printing 312 --fulfillment 75 --processing 70 \
        --sales-hours 45 --design-hours 10 --design-rate 30 --coord-hours 5 \
        --renewal-hours 12

    python3 directmail_pricer.py ... --json
"""
import argparse
import json
import sys


def price(spots, spot_price, postage, printing, fulfillment, processing,
          sales_hours, design_hours, design_rate, coord_hours, renewal_hours):
    """Return the campaign ledger for one card.

    >>> r = price(16, 150, 550, 312, 75, 70, 45, 10, 30, 5, 12)
    >>> r["collected"], r["hard_costs"], r["net_margin"]
    (2400.0, 1007.0, 1093.0)
    >>> r["first_rate"], r["renewal_rate"]
    (18.22, 91.08)
    >>> r["renewal_rate"] > r["first_rate"]
    True
    >>> r2 = price(16, 150, 550, 312, 75, 70, 45, 10, 0, 5, 12)
    >>> r2["design_value"], r2["first_rate"]
    (0.0, 23.22)
    >>> price(2, 150, 112, 150, 25, 6, 45, 10, 30, 5, 12)["first_rate"] < 0
    True
    """
    if spots <= 0:
        raise ValueError("spots must be positive")
    if spot_price < 0 or postage < 0 or printing < 0 or fulfillment < 0 or processing < 0:
        raise ValueError("dollar inputs cannot be negative")
    if sales_hours <= 0 or design_hours <= 0 or coord_hours < 0:
        raise ValueError("first-card hours must be positive")
    if renewal_hours <= 0:
        raise ValueError("renewal_hours must be positive (a renewal is never free)")
    spots, spot_price = float(spots), float(spot_price)
    postage, printing, fulfillment, processing = (
        float(postage), float(printing), float(fulfillment), float(processing))
    sales_hours, design_hours = float(sales_hours), float(design_hours)
    design_rate, coord_hours, renewal_hours = (
        float(design_rate), float(coord_hours), float(renewal_hours))
    collected = spots * spot_price
    hard_costs = postage + printing + fulfillment + processing
    cash_margin = collected - hard_costs
    design_value = design_hours * design_rate
    net_margin = cash_margin - design_value
    first_hours = sales_hours + design_hours + coord_hours
    first_rate = net_margin / first_hours
    renewal_rate = net_margin / renewal_hours
    lift = renewal_rate / first_rate
    saved_hours = sales_hours - renewal_hours
    return {
        "collected": round(collected, 2),
        "hard_costs": round(hard_costs, 2),
        "cash_margin": round(cash_margin, 2),
        "design_value": round(design_value, 2),
        "net_margin": round(net_margin, 2),
        "first_hours": round(first_hours, 1),
        "first_rate": round(first_rate, 2),
        "renewal_rate": round(renewal_rate, 2),
        "retention_lift": round(lift, 2),
        "selling_hours_saved_per_renewal": round(saved_hours, 1),
    }


def main():
    ap = argparse.ArgumentParser(
        description="directmail_pricer: hourly rate for a mail card, first run vs renewal")
    ap.add_argument("--spots", type=float, required=True, help="ad spots sold on the card")
    ap.add_argument("--spot-price", type=float, required=True, help="dollars per spot")
    ap.add_argument("--postage", type=float, required=True, help="total postage cost")
    ap.add_argument("--printing", type=float, required=True, help="total print cost")
    ap.add_argument("--fulfillment", type=float, default=0.0, help="bundling, paperwork, delivery")
    ap.add_argument("--processing", type=float, default=0.0, help="payment processing on ad sales")
    ap.add_argument("--sales-hours", type=float, required=True, help="prospecting, calls, chasing approvals")
    ap.add_argument("--design-hours", type=float, required=True, help="layout hours")
    ap.add_argument("--design-rate", type=float, default=30.0, help="value of one design hour")
    ap.add_argument("--coord-hours", type=float, default=0.0, help="printer coordination and reporting")
    ap.add_argument("--renewal-hours", type=float, required=True, help="hours to renew the same client once")
    ap.add_argument("--json", action="store_true", dest="as_json", help="print JSON instead of a report")
    args = ap.parse_args()
    try:
        r = price(args.spots, args.spot_price, args.postage, args.printing,
                  args.fulfillment, args.processing, args.sales_hours,
                  args.design_hours, args.design_rate, args.coord_hours,
                  args.renewal_hours)
    except ValueError as e:
        print(f"directmail_pricer: {e}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(r, indent=2))
        return 0
    print("directmail_pricer: mail card hourly rate, first card vs renewal")
    print(f"collected: ${r['collected']:,.2f} | hard costs: ${r['hard_costs']:,.2f}")
    print(f"cash margin: ${r['cash_margin']:,.2f} | design value: ${r['design_value']:,.2f}")
    print(f"net margin: ${r['net_margin']:,.2f}")
    print(f"first card: ${r['first_rate']:,.2f}/hr over {r['first_hours']} hours")
    print(f"renewal: ${r['renewal_rate']:,.2f}/hr | retention lift {r['retention_lift']}x")
    print(f"selling hours saved per renewal: {r['selling_hours_saved_per_renewal']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
