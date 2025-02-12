from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Any

def run_parallel(tasks: List[Callable[..., Any]], max_workers: int = 5) -> List[Any]:
    """Runs a list of tasks in parallel using ThreadPoolExecutor."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(task) for task in tasks]
        for future in futures:
            results.append(future.result())
    return results
