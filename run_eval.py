import json
from evaluation import eval as evaluate

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def main():
    examples = load_jsonl("data/examples.jsonl")
    outputs = load_jsonl("model_outputs.jsonl")

    if len(examples) != len(outputs):
        print(f"❌ Mismatch: {len(examples)} examples vs {len(outputs)} outputs")
        return

    total = len(examples)
    correct = 0
    results = []

    for i, (ex, out) in enumerate(zip(examples, outputs)):
        answer = out.get("output", "").strip()
        ok = evaluate(answer, ex["solution_structure"])
        results.append({
            "index": i,
            "question": ex["question"],
            "output": answer,
            "correct": ok
        })
        status = "✅" if ok else "❌"
        print(f"{status} Example {i+1}/{total}")

        if not ok:
            print(f"   ↳ Output: {answer}")
            print(f"   ↳ Question: {ex['question'][:80]}...\n")

    acc = correct = sum(r["correct"] for r in results)
    print(f"\n🎯 Accuracy: {correct}/{total} = {acc / total:.2%}")

    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        print("📝 Results saved to eval_results.json")

if __name__ == "__main__":
    main()
