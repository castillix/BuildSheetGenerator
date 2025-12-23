import pricing

def check_db(query):
    print(f"\nTesting query: '{query}'")
    candidates = pricing.get_cpu_candidates(query)
    
    if candidates:
        print(f"Found {len(candidates)} candidates:")
        for i, c in enumerate(candidates):
            print(f" {i+1}. {c['name']} (Score: {c['score']})")
    else:
        print("No candidates found.")

# Test with the problematic CPU
check_db("Intel(R) Core(TM) i7-7600U CPU")
check_db("Intel(R) Core(TM) i7-7600U CPU @ 2.80GHz")
check_db("Intel Core i7-7600U") # Exact/Clean
check_db("i7-7600U") # Partial

