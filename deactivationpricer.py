#!/usr/bin/env python3
"""deactivationpricer: true hourly rate for gig work, deactivation risk included.

One Python file, standard library only. Gig apps deactivate accounts with
little warning, and a suspension commonly runs a few weeks while the appeal
crawls through. The sticker hourly rate never prices that in, so a gig that
looks like $22/hr can really pay $19 once the risk is amortized.

Give it your gross rate, weekly hours, weekly expenses, the weekly chance of
a deactivation, how long a suspension typically benches you, and the hours an
appeal eats. It returns the naive rate next to the risk-adjusted rate, the
expected suspensions per year, and the pay weeks you should expect to lose.

Run it:

    python3 deactivationpricer.py --rate 22 --hours 30 --expenses 40 \
        --risk 1.0 --downtime 6 --appeal-hours 4

Doctest the math:

    python3 -m doctest deactivationpricer.py
"""

import argparse
import json
import sys


def effective_hourly(gross, hours, expenses, risk, downtime, appeal_hours):
    """Risk-adjusted hourly rate for a gig platform.

    gross       $ per billed hour
    hours       billed hours per week
    expenses    weekly out-of-pocket costs (gas, gear, insurance)
    risk        weekly probability of a deactivation, in percent
    downtime    weeks benched per deactivation
    appeal_hours hours spent on appeals per deactivation

    Returns a dict. Naive rate ignores deactivations entirely; the
    effective rate replaces the lost pay weeks and spreads appeal hours
    across every hour worked, billed or not.

    >>> r = effective_hourly(22, 30, 40, 0.0, 6, 4)
    >>> (r["naive_rate"], r["effective_rate"], r["events_per_year"])
    (20.67, 20.67, 0.0)
    >>> effective_hourly(10, 10, 0, 100.0, 2, 0)["effective_rate"]
    0.0
    >>> s = effective_hourly(22, 30, 40, 1.0, 6, 4)
    >>> (s["naive_rate"], s["effective_rate"], s["events_per_year"])
    (20.67, 19.4, 0.52)
    """
    weekly_net = gross * hours - expenses
    naive = weekly_net / hours
    events = (risk / 100.0) * 52.0
    lost_weeks = events * downtime
    earning_weeks = max(0.0, 52.0 - lost_weeks)
    annual_net = weekly_net * earning_weeks
    appeal_total = events * appeal_hours
    total_hours = hours * 52.0 + appeal_total
    effective = annual_net / total_hours
    return {
        "weekly_net": round(weekly_net, 2),
        "naive_rate": round(naive, 2),
        "effective_rate": round(effective, 2),
        "events_per_year": round(events, 2),
        "lost_weeks_per_year": round(lost_weeks, 1),
        "appeal_hours_per_year": round(appeal_total, 1),
    }


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Price gig-platform deactivation risk into your real hourly rate."
    )
    p.add_argument("--rate", type=float, required=True, help="gross $ per hour")
    p.add_argument("--hours", type=float, required=True, help="billed hours per week")
    p.add_argument("--expenses", type=float, default=0.0, help="weekly expenses in $")
    p.add_argument("--risk", type=float, default=1.0,
                   help="weekly deactivation probability in percent (default 1.0)")
    p.add_argument("--downtime", type=float, default=6.0,
                   help="weeks benched per deactivation (default 6)")
    p.add_argument("--appeal-hours", dest="appeal_hours", type=float, default=4.0,
                   help="hours per appeal (default 4)")
    p.add_argument("--json", action="store_true", dest="as_json",
                   help="machine-readable output")
    args = p.parse_args(argv)

    r = effective_hourly(args.rate, args.hours, args.expenses, args.risk,
                         args.downtime, args.appeal_hours)
    if args.as_json:
        print(json.dumps(r, indent=2))
        return 0

    drop = r["naive_rate"] - r["effective_rate"]
    print("deactivationpricer: gig rate with suspension risk priced in")
    print("sticker rate: ${:.2f}/hr net of expenses".format(r["naive_rate"]))
    print("risk-adjusted: ${:.2f}/hr (drop ${:.2f})".format(r["effective_rate"], drop))
    print("expect {:.1f} deactivations/year, {:.1f} pay weeks lost, {:.1f} appeal hours".format(
        r["events_per_year"], r["lost_weeks_per_year"], r["appeal_hours_per_year"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
