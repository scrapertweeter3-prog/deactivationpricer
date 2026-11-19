#!/usr/bin/env python3
"""million_daily_pricer.py - turn a revenue headline into units per day, then
take-home. The division the screenshot skips: price a daily target in units,
run the fee-and-tax stack, and price the effective hourly of a part-time month.

Article checks (doctests) pin the rows from "A $1M AI Side Hustle Means
$3,333 a Working Day" on extrahustles.com.

Run:  python3 million_daily_pricer.py --year 1000000 --price 29 --fee 10 --tools 150 --hours 10
      python3 million_daily_pricer.py --json
"""
import argparse, json, sys


def working_days(year: int, days: int = 300) -> float:
    """Revenue per working day. The article's brutal division.

    >>> working_days(1_000_000)
    3333.33
    >>> working_days(2_000, days=30)
    66.67
    """
    return round(year / days, 2)


def units_per_day(target: float, price: float) -> float:
    """Units a day must sell to hit the target.

    >>> units_per_day(3333.33, 29)
    114.94
    >>> units_per_day(3333.33, 6)
    555.56
    >>> units_per_day(3333.33, 10)
    333.33
    """
    return round(target / price, 2)


def billable_hours(target: float, rate: float) -> float:
    """Hours a day at an hourly rate. The capacity wall.

    >>> billable_hours(3333.33, 85)
    39.22
    """
    return round(target / rate, 2)


def take_home(month: float, fee_pct: float = 10.0, tools: float = 150.0,
              se_pct: float = 15.3) -> dict:
    """Fee stack on a gross month: platform fee, tools, self-employment tax.

    The article's worked screenshot: a $5,000 Gumroad month at 10% fee with
    $150 of tools lands near $3,680 before income tax.

    >>> t = take_home(5000, fee_pct=10, tools=150)
    >>> t["after_fee"]
    4500.0
    >>> t["after_tools"]
    4350.0
    >>> t["before_income_tax"]
    3684.45
    """
    after_fee = round(month * (1 - fee_pct / 100), 2)
    after_tools = round(after_fee - tools, 2)
    before_income_tax = round(after_tools * (1 - se_pct / 100), 2)
    return {"gross": round(month, 2), "fee_pct": fee_pct, "tools": tools,
            "after_fee": after_fee, "after_tools": after_tools,
            "se_pct": se_pct, "before_income_tax": before_income_tax}


def part_time_hourly(month: float, hours_week: float) -> float:
    """Effective hourly of a part-time month (4.33 weeks/month).

    >>> part_time_hourly(2000, 5)
    92.38
    >>> part_time_hourly(2000, 10)
    46.19
    >>> part_time_hourly(2000, 15)
    30.79
    """
    return round(month / (hours_week * 4.33), 2)


def main() -> None:
    ap = argparse.ArgumentParser(description="price a revenue headline in units and take-home")
    ap.add_argument("--year", type=float, default=1_000_000, help="headline yearly revenue")
    ap.add_argument("--days", type=int, default=300, help="working days per year")
    ap.add_argument("--price", type=float, default=29, help="price per unit (or billable rate)")
    ap.add_argument("--fee", type=float, default=10.0, help="platform fee percent")
    ap.add_argument("--tools", type=float, default=150.0, help="monthly tool stack dollars")
    ap.add_argument("--hours", type=float, default=10.0, help="part-time hours per week")
    ap.add_argument("--month", type=float, default=None, help="gross monthly revenue for the take-home stack")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args()

    daily = working_days(a.year, a.days)
    upday = units_per_day(daily, a.price)
    stack = take_home(a.month if a.month is not None else a.year / 12,
                      fee_pct=a.fee, tools=a.tools)
    hourly = part_time_hourly(stack["before_income_tax"], a.hours)
    out = {"daily_target": daily, "price": a.price, "units_per_day": upday,
           "take_home": stack, "effective_hourly": hourly}
    if a.json:
        print(json.dumps(out, indent=2))
    else:
        print("million_daily_pricer: headline to units to take-home")
        print(f"daily target: ${daily:,.2f} over {a.days} days")
        print(f"units per day at ${a.price:g}: {upday:,.2f}")
        s = stack
        print(f"month ${s['gross']:,.2f} -> fee {s['fee_pct']:g}% ${s['after_fee']:,.2f}"
              f" -> tools ${s['tools']:,.2f} -> SE {s['se_pct']:g}% ${s['before_income_tax']:,.2f}")
        print(f"effective hourly at {a.hours:g} h/wk: ${hourly:,.2f}")


if __name__ == "__main__":
    main()
