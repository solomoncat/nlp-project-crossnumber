import os
import math
import random
import json
from datetime import datetime

# === Utilities ===

def is_power_of(base, n):
    val = 1
    while val < n:
        val *= base
    return val == n

def is_perfect_square(n):
    return int(math.sqrt(n))**2 == n

def is_cube(n):
    return round(n ** (1/3))**3 == n

def is_triangle(n):
    return int((8*n + 1)**0.5)**2 == 8*n + 1

def is_prime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for d in range(3, int(n**0.5) + 1, 2):
        if n % d == 0:
            return False
    return True

def generate_fibonacci(limit):
    a, b, fibs = 0, 1, set()
    while b <= limit:
        fibs.add(b)
        a, b = b, a + b
    return fibs

fibonacci = generate_fibonacci(999)

def to_base(n, base):
    digits = []
    while n > 0:
        digits.append(str(n % base))
        n //= base
    return ''.join(digits[::-1]) if digits else "0"

def clue_type(fact):
    if "palindrome" in fact:
        return "palindrome"
    if "power of" in fact:
        return "power"
    if "perfect square" in fact:
        return "square"
    if "perfect cube" in fact:
        return "cube"
    if "triangle" in fact:
        return "triangle"
    if "fibonacci" in fact:
        return "fibonacci"
    if "prime" in fact:
        return "prime"
    return fact

def interesting_facts(n):
    facts = []
    for base in range(2, 14):
        if base != 10 and to_base(n, base) == to_base(n, base)[::-1]:
            facts.append(f"palindrome when converted to base {base}")
    for base in range(6, 11):
        if is_power_of(base, n):
            facts.append(f"power of {base}")
    if is_perfect_square(n):
        facts.append("perfect square")
    if is_cube(n):
        facts.append("perfect cube")
    if is_triangle(n):
        facts.append("triangle number")
    if n in fibonacci:
        facts.append("fibonacci number")
    if is_prime(n):
        facts.append("prime number")

    def add_near(label, check_fn):
        if check_fn(n - 1):
            facts.append(f"1 above a {label}")
        if check_fn(n + 1):
            facts.append(f"1 below a {label}")

    add_near("square", is_perfect_square)
    add_near("cube", is_cube)
    add_near("triangle number", is_triangle)
    add_near("fibonacci number", lambda x: x in fibonacci)
    for base in range(2, 11):
        add_near(f"power of {base}", lambda x, b=base: is_power_of(b, x))
    return facts

def get_global_rule(a, b, c, digits, digit_names, name_a, name_b, name_c):
    moduli = [111, 113, 121, 125, 128, 147, 200, 256, 512, 999]
    for m in moduli:
        if (a + b) % m == c % m:
            return f"{name_a} + {name_b} ≡ {name_c} mod {m}"
        if (a - b) % m == c % m:
            return f"{name_a} - {name_b} ≡ {name_c} mod {m}"
    if (b - a) == (c - b):
        return f"{name_b} - {name_a} = {name_c} - {name_b}"
    for m in moduli:
        if (a * b) % m == c % m:
            return f"{name_a} × {name_b} ≡ {name_c} mod {m}"
    sq_sum = sum(d**2 for d in digits)
    if 10 <= sq_sum <= 194:
        name_str = " + ".join([f"{n}²" for n in digit_names])
        return f"{name_str} = {sq_sum}"
    return None

# === Main Generator ===

def generate_question_sequences(limit=150, filename="data/examples.jsonl"):
    random.seed(817309719)
    os.makedirs("data", exist_ok=True)
    questions = []
    found = 0
    attempts = 0

    while found < limit:
        attempts += 1
        digits = random.sample(range(10), 8)
        a,b,c,d,e,f,g,h = digits
        abc = 100*a + 10*b + c
        cde = 100*c + 10*d + e
        efg = 100*e + 10*f + g
        gha = 100*g + 10*h + a

        facts1 = interesting_facts(abc)
        facts2 = interesting_facts(cde)
        facts3 = interesting_facts(efg)
        facts4 = interesting_facts(gha)

        if not (facts1 and facts2 and facts3 and facts4):
            continue

        first_facts = [facts1[0], facts2[0], facts3[0], facts4[0]]
        clue_types = [clue_type(f) for f in first_facts]
        if len(set(clue_types)) < 4 or clue_types.count("palindrome") > 2:
            continue

        symbolic = None
        checks = []
        candidates = [
            (abc, cde, efg, [a,b,c,d,e,f], ["a", "b", "c", "d", "e", "f"], "abc", "cde", "efg"),
            (cde, efg, gha, [c,d,e,f,g,h], ["c", "d", "e", "f", "g", "h"], "cde", "efg", "gha"),
            (abc, efg, gha, [a,b,c,e,f,g], ["a", "b", "c", "e", "f", "g"], "abc", "efg", "gha"),
            (abc, gha, cde, [a,b,c,g,h,a], ["a", "b", "c", "g", "h", "a"], "abc", "gha", "cde")
        ]

        for a1, b1, c1, dig, name_dig, na, nb, nc in candidates:
            symbolic = get_global_rule(a1, b1, c1, dig, name_dig, na, nb, nc)
            if symbolic:
                checks.append({
                    "type": "global_rule",
                    "expression": symbolic,
                    "inputs": [na, nb, nc]
                })
                break

        if not symbolic:
            continue

        found += 1
        question_text = (
            "The numbers are abc, cde, efg, gha, where each letter is a distinct digit between 0 and 9 (no repeats). "
            "Note that the last digit of the first number is the first digit of the second, and so on, so c, e, g, and a are shared.\n"
            f"1. {first_facts[0]}\n"
            f"2. {first_facts[1]}\n"
            f"3. {first_facts[2]}\n"
            f"4. {first_facts[3]}\n"
            f"Global rule: {symbolic}"
        )

        for label, fact in zip(["abc", "cde", "efg", "gha"], first_facts):
            checks.append({
                "type": "local_fact",
                "fact": fact,
                "applies_to": label
            })

        checks.append({
            "type": "structure",
            "rule": "overlapping digits",
            "overlap": [("abc", "cde", "c"), ("cde", "efg", "e"), ("efg", "gha", "g"), ("gha", "abc", "a")]
        })
        checks.append({
            "type": "structure",
            "rule": "all digits distinct"
        })

        example = {
            "question": question_text,
            "solution_structure": checks,
            "difficulty": "medium",
            "topic": "3x3 non-geometric word problem mathematical reasoning"
        }

        questions.append(example)

    with open(filename, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"✅ Generated {found} questions in {filename} after {attempts} attempts.")

# === Entry Point ===

if __name__ == "__main__":
    generate_question_sequences(limit=10)
