import time

def benchmark(f, a, b, sigma, methods_dict, n_runs=3):
    results = {}
    for name, method in methods_dict.items():
        times, iters_list, roots = [], [], []
        for _ in range(n_runs):
            t0 = time.perf_counter()
            try:
                out = method(f, a, b, sigma)
                root = out[0]
                hist = out[1] if len(out) > 1 else []
                t1 = time.perf_counter()
                times.append((t1 - t0) * 1000)
                iters_list.append(len(hist))
                roots.append(root)
            except Exception:
                times.append(float("inf"))
                iters_list.append(0)
                roots.append(None)
        valid_times = [t for t in times if t < float("inf")]
        results[name] = {
            "avg_time_ms": sum(valid_times) / len(valid_times) if valid_times else None,
            "min_time_ms": min(valid_times) if valid_times else None,
            "avg_iters": sum(iters_list) / len(iters_list) if iters_list else 0,
            "roots": roots,
            "success": any(r is not None for r in roots),
        }
    return results