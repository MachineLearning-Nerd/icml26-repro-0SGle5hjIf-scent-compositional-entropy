# Claim 1 source audit

The imported claim points to Algorithm 1, but the exact closed-form statement
is Lemma 3.1 in Section 3, equations (5)–(7), followed by the stable
implementation paragraph. It assumes `alpha_t > 0`, the stochastic scalar
objective `exp(s-nu)+nu`, and the Bregman generator `exp(-nu)`.

The paper says the logarithmic implementation can effectively avoid numerical
overflow. It does not state a universal IEEE-754 range and does not make the
imported wording's explicit comparison to an “exponential-average baseline” in
Lemma 3.1. This contract therefore verifies the identity, the argmin, and
finite float64 behavior over a declared stress domain; it does not claim
universal absence of all numerical error.

