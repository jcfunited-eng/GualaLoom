"""
GUALALOOM-HANDOFF-WC-2026-06-04-MATHLOOM-KRIMELACK
File: gualaloom_mathloom_v1.py
Module: gualaloom.math.mathloom
Purpose: Balanced ternary arithmetic by digit constraint (Approach 1 per ArcLoom Master Spec v5.0 Ch.14).
Approach 3 (global settle) deferred to FPGA validation per spec.
Validated standalone: 6561 additions, 961 multiplications, 610 divisions — 0 failures.
Public API:
    int_to_bt(n)       -> list of {-1,0,+1}, low-order first
    bt_to_int(d)       -> int
    bt_add(a, b)       -> (digits, carry_chain)
    bt_sub(a, b)       -> (digits, carry_chain)
    bt_mul(a, b)       -> digits
    bt_div(a, b)       -> (quotient_digits, remainder_digits)
    bt_neg(a)          -> digits
    settle_demo(a, b)  -> trace dict
"""

import numpy as np


def int_to_bt(n):
    if n == 0: return [0]
    out = []; neg = n < 0; x = abs(n)
    while x > 0:
        r = x % 3; x //= 3
        if r == 2: r = -1; x += 1
        out.append(r)
    return [-d for d in out] if neg else out


def bt_to_int(d):
    return sum(int(x) * (3 ** i) for i, x in enumerate(d))


def bt_add(a_digits, b_digits):
    n = max(len(a_digits), len(b_digits))
    a = list(a_digits) + [0] * (n - len(a_digits))
    b = list(b_digits) + [0] * (n - len(b_digits))
    c = 0
    s = []
    chain = [c]
    for i in range(n):
        total = a[i] + b[i] + c
        s_i = total; c_next = 0
        while s_i > 1: s_i -= 3; c_next += 1
        while s_i < -1: s_i += 3; c_next -= 1
        s.append(s_i); c = c_next; chain.append(c)
    if c != 0: s.append(c)
    while len(s) > 1 and s[-1] == 0: s.pop()
    return s, chain


def bt_neg(a): return [-d for d in a]
def bt_sub(a, b): return bt_add(a, bt_neg(b))


def bt_mul(a, b):
    res = [0]
    for i, bi in enumerate(b):
        if bi == 0: continue
        partial = [0] * i + [d * bi for d in a]
        res, _ = bt_add(res, partial)
    while len(res) > 1 and res[-1] == 0: res.pop()
    return res


def bt_div(a, b):
    a_int = bt_to_int(a); b_int = bt_to_int(b)
    if b_int == 0:
        raise ZeroDivisionError("division by zero")
    q_int, r_int = divmod(a_int, b_int)
    return int_to_bt(q_int), int_to_bt(r_int)


def settle_demo(a, b):
    s, ch = bt_add(a, b)
    return {"a": a, "b": b, "s": s, "a_int": bt_to_int(a), "b_int": bt_to_int(b),
            "s_int": bt_to_int(s), "carries": ch}


if __name__ == "__main__":
    print("MathLoom validation")
    print("=" * 60)
    fail = 0; n = 0
    for x in range(-40, 41):
        for y in range(-40, 41):
            s, _ = bt_add(int_to_bt(x), int_to_bt(y))
            if bt_to_int(s) != x + y: fail += 1
            n += 1
    print(f"addition: {n} tests, {fail} failures")

    fail = 0; n = 0
    for x in range(-15, 16):
        for y in range(-15, 16):
            r = bt_mul(int_to_bt(x), int_to_bt(y))
            if bt_to_int(r) != x * y: fail += 1
            n += 1
    print(f"multiplication: {n} tests, {fail} failures")

    fail = 0; n = 0
    for x in range(-30, 31):
        for y in [-7, -3, -2, -1, 1, 2, 3, 5, 7, 11]:
            q, r = bt_div(int_to_bt(x), int_to_bt(y))
            if bt_to_int(q) * y + bt_to_int(r) != x: fail += 1
            n += 1
    print(f"division: {n} tests, {fail} failures")

    print()
    print("Sample settling traces (a + b -> s with carry chain):")
    for x, y in [(1, 1), (2, 2), (5, 3), (10, 10), (27, 27), (-13, 8), (100, 11)]:
        d = settle_demo(int_to_bt(x), int_to_bt(y))
        print(f"  {x:>4} + {y:>4} = {d['s_int']:>5}   "
              f"a={d['a']} b={d['b']} s={d['s']} c={d['carries']}")
