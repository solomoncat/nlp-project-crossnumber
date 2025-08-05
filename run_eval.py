# run_eval.py

import json
import os
from evaluation import eval as evaluate  # your evaluation function

# === Loaders ===

def load_jsonl(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def clean_answer(answer):
    """
    Convert things like ["'0'", "'1'", "'2'", "'3'"] → [0, 1, 2, 3]
    or if it's already a list of ints, pass through.
    """
    if isinstance(answer, list):
        cleaned = []
        for x in answer:
            if isinstance(x, str):
                # strip whitespace and outer quotes
                s = x.strip().strip("'").strip('"')
                cleaned.append(int(s))
            else:
                cleaned.append(int(x))
        return cleaned
    return answer

# === Main ===

def main():
    # Paths — adjust if needed
    examples_path = "data/examples.jsonl"
    outputs_path  = "model_outputs.jsonl"

    # Load
    examples = load_jsonl(examples_path)
    outputs  = load_jsonl(outputs_path)

    if len(examples) != len(outputs):
        print(f"⚠️  Example/output count mismatch: "
              f"{len(examples)} examples vs {len(outputs)} outputs")
        # proceed with min-length
    total = min(len(examples), len(outputs))

    correct = 0
    for i in range(total):
        ex = examples[i]
        out = outputs[i]

        # Assume your model_outputs.jsonl lines look like:
        # { "index": i, "example": {...}, "answer": [...] }
        # Or just { "answer": [...]} — adapt as needed:
        raw_answer = out.get("answer", out.get("output", None))
        if raw_answer is None:
            print(f"❌ Missing 'answer' field in output #{i}")
            continue

        # Clean it to a list of ints if needed
        cleaned = clean_answer(raw_answer)
        # Re‐serialize as string for evaluate()
        answer_str = str(cleaned)

        # Evaluate
        passed = evaluate(answer_str, ex["solution_structure"])
        status = "✅" if passed else "❌"
        print(f"{status} Example {i+1}/{total}: Answer = {answer_str}")

        if passed:
            correct += 1
        else:
            # optional: print the question/context on failure
            q = ex["question"]
            print("   ↳ Question:", q.replace("\n","  ")[:100], "…")

    # Summary
    accuracy = correct / total * 100 if total else 0
    print(f"\n🎯 Accuracy: {correct}/{total} = {accuracy:.2f}%")

    # Save detailed results if you want
    results = [
        {
            "index": i,
            "answer": clean_answer(outputs[i].get("answer", outputs[i].get("output", None))),
            "correct": bool(evaluate(str(clean_answer(outputs[i].get("answer", outputs[i].get("output", None)))), examples[i]["solution_structure"]))
        }
        for i in range(total)
    ]
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        print("📝 Detailed results written to eval_results.json")

if __name__ == "__main__":
    main()
