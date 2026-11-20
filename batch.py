import csv

def load_tasks_csv(path):
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

def save_results_csv(results, path):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Уравнение", "a", "b", "σ", "Корень", "Статус"])
        for r in results:
            t = r["task"]
            root = r["result"] if r["result"] else "—"
            writer.writerow([t.get("eq"), t.get("a"), t.get("b"),
                             t.get("sigma"), root, r["status"]])