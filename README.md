# deactivationpricer

One-file Python calculator that prices gig-app deactivation risk into your
real hourly rate. Standard library only.

Gig platforms suspend accounts with a template email and a slow appeal, and a
suspension commonly runs a few weeks while pay stops. The rate the app
advertises never accounts for it. Feed this file your gross rate, weekly
hours and expenses, the weekly chance of a deactivation, and how long a
typical suspension benches you. It prints the sticker rate next to the
risk-adjusted rate, expected suspensions per year, pay weeks lost, and appeal
hours. A `--json` flag gives script-friendly output.

## Usage

    python3 deactivationpricer.py --rate 22 --hours 30 --expenses 40 --risk 1.0 --downtime 6 --appeal-hours 4

    deactivationpricer: gig rate with suspension risk priced in
    sticker rate: $20.67/hr net of expenses
    risk-adjusted: $19.40/hr (drop $1.27)
    expect 0.5 deactivations/year, 3.1 pay weeks lost, 2.1 appeal hours

Machine-readable:

    python3 deactivationpricer.py --rate 18 --hours 25 --expenses 25 --risk 2.0 --downtime 4 --json

Doctest the math:

    python3 -m doctest deactivationpricer.py

## The math

Weekly net is gross rate times billed hours minus weekly expenses. The
sticker rate is that net divided by hours, which is the number most people
bank on. A weekly deactivation probability of r percent produces r/100 * 52
expected suspensions a year; each one costs `--downtime` pay weeks and
`--appeal-hours` of unpaid paperwork. The effective rate spreads both losses
across every hour worked in a year, billed or not. Same inputs, minus the
risk column, reproduces the sticker rate exactly.

## Why

The full write-up behind the method, including the six-week deactivation gap
and the multi-app stack that hedges it, lives on [Extra
Hustles](https://extrahustles.com).

## License

MIT
