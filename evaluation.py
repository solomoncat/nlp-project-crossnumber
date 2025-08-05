import math

# === Utilities ===

def is_perfect_square(n): return int(n**0.5)**2 == n
def is_triangle(n): return int((8*n + 1)**0.5)**2 == 8*n + 1
def is_prime(n):
    if n <= 1: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(n**0.5)+1, 2):
        if n % i == 0: return False
    return True

def to_base(n, b):
    digits = []
    while n > 0:
        digits.append(str(n % b))
        n //= b
    return ''.join(digits[::-1]) or "0"

def is_palindrome_in_base(n, base):
    digits = to_base(n, base)
    return digits == digits[::-1]

# === Main evaluator ===

def eval(model_output_str, solution_structure):
    try:
        # Parse: "[123,456,789,321]"
        num_str = model_output_str.strip().strip("[]")
        nums = list(map(int, num_str.split(",")))
        if len(nums) != 4:
            return False

        mapping = {"abc": nums[0], "cde": nums[1], "efg": nums[2], "gha": nums[3]}
        abc, cde, efg, gha = nums
        a = abc // 100
        b = (abc // 10) % 10
        c = abc % 10
        d = (cde // 10) % 10
        e = cde % 10
        f = (efg // 10) % 10
        g = efg % 10
        h = (gha // 10) % 10

        letters = [a, b, c, d, e, f, g, h]
        if len(set(letters)) != 8:
            return False

        for rule in solution_structure:
            if rule["type"] == "local_fact":
                val = mapping[rule["applies_to"]]
                fact = rule["fact"]

                if "palindrome" in fact:
                    base = int(fact.split("base")[1])
                    if not is_palindrome_in_base(val, base):
                        return False
                elif fact == "perfect square":
                    if not is_perfect_square(val):
                        return False
                elif fact == "triangle number":
                    if not is_triangle(val):
                        return False
                elif fact == "prime number":
                    if not is_prime(val):
                        return False
                elif "1 above" in fact:
                    label = fact.replace("1 above a ", "")
                    if label == "triangle number" and not is_triangle(val - 1):
                        return False
                    if label == "square" and not is_perfect_square(val - 1):
                        return False
                    if label == "prime number" and not is_prime(val - 1):
                        return False
                elif "1 below" in fact:
                    label = fact.replace("1 below a ", "")
                    if label == "triangle number" and not is_triangle(val + 1):
                        return False
                    if label == "square" and not is_perfect_square(val + 1):
                        return False
                    if label == "prime number" and not is_prime(val + 1):
                        return False

            elif rule["type"] == "global_rule":
                expr = rule["expression"]
                if "≡" in expr:
                    lhs, rhs = expr.split("≡")
                    mod = int(rhs.split("mod")[1])

                    if "+" in lhs:
                        parts = lhs.split("+")
                        lhs_val = sum(mapping[p.strip()] for p in parts)
                    elif "-" in lhs:
                        parts = lhs.split("-")
                        lhs_val = mapping[parts[0].strip()] - mapping[parts[1].strip()]
                    elif "×" in lhs:
                        parts = lhs.split("×")
                        lhs_val = mapping[parts[0].strip()] * mapping[parts[1].strip()]
                    else:
                        return False

                    rhs_key = rhs.split("mod")[0].strip()
                    rhs_val = mapping.get(rhs_key, None)
                    if rhs_val is None:
                        return False

                    if lhs_val % mod != rhs_val % mod:
                        return False

                elif "=" in expr and "²" in expr:
                    expected = int(expr.split("=")[1].strip())
                    vars_squared = [term.strip().replace("²", "") for term in expr.split("=")[0].split("+")]

                    digits = {
                        "a": a, "b": b, "c": c, "d": d,
                        "e": e, "f": f, "g": g, "h": h
                    }

                    try:
                        actual = sum(digits[var]**2 for var in vars_squared)
                    except KeyError:
                        return False

                    if actual != expected:
                        return False

            elif rule["type"] == "structure":
                if rule["rule"] == "overlapping digits":
                    for a_key, b_key, shared in rule["overlap"]:
                        a_str = str(mapping[a_key]).zfill(3)
                        b_str = str(mapping[b_key]).zfill(3)
                        if a_str[-1] != b_str[0]:
                            return False
                elif rule["rule"] == "all digits distinct":
                    if len(set(letters)) != 8:
                        return False

        return True
    except:
        return False

        # Check each rule
        for rule in solution_structure:
            if rule["type"] == "local_fact":
                val = mapping[rule["applies_to"]]
                fact = rule["fact"]
                if "palindrome" in fact:
                    base = int(fact.split("base")[1])
                    if not is_palindrome_in_base(val, base): return False
                elif fact == "perfect square":
                    if not is_perfect_square(val): return False
                elif fact == "triangle number":
                    if not is_triangle(val): return False
                elif fact == "prime number":
                    if not is_prime(val): return False
                elif "1 above" in fact:
                    label = fact.replace("1 above a ", "")
                    if label == "triangle number" and not is_triangle(val - 1): return False
                    if label == "square" and not is_perfect_square(val - 1): return False
                    if label == "prime number" and not is_prime(val - 1): return False
                elif "1 below" in fact:
                    label = fact.replace("1 below a ", "")
                    if label == "triangle number" and not is_triangle(val + 1): return False
                    if label == "square" and not is_perfect_square(val + 1): return False
                    if label == "prime number" and not is_prime(val + 1): return False

            elif rule["type"] == "global_rule":
                expr = rule["expression"]
                inputs = [mapping[x] for x in rule["inputs"]]
                if "≡" in expr:
                    lhs, rhs = expr.split("≡")
                    mod = int(rhs.split("mod")[1])
                    if "+" in lhs:
                        parts = lhs.split("+")
                        lhs_val = sum(mapping[p.strip()] for p in parts)
                    elif "-" in lhs:
                        parts = lhs.split("-")
                        lhs_val = mapping[parts[0].strip()] - mapping[parts[1].strip()]
                    elif "×" in lhs:
                        parts = lhs.split("×")
                        lhs_val = mapping[parts[0].strip()] * mapping[parts[1].strip()]
                    else:
                        return False
                    rhs_val = mapping[rhs.split("mod")[0].strip()]
                    if lhs_val % mod != rhs_val % mod: return False
                elif "=" in expr and "²" in expr:
                    # sum of squares of digits
                    expected = int(expr.split("=")[1].strip())
                    all_digits = set()
                    for val in [mapping[k] for k in ["abc", "cde", "efg", "gha"]]:
                        all_digits.update(int(d) for d in str(val))
                    actual = sum(d**2 for d in all_digits)
                    if actual != expected: return False

            elif rule["type"] == "structure":
                if rule["rule"] == "overlapping digits":
                    for a, b, shared in rule["overlap"]:
                        if str(mapping[a])[-1] != str(mapping[b])[0]:
                            return False
                elif rule["rule"] == "all digits distinct":
                    all_digits = "".join(str(mapping[k]) for k in ["abc", "cde", "efg", "gha"])
                    if len(set(all_digits)) != len(all_digits):
                        return False
        return True
    except Exception:
        return False
