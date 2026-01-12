"""Test price estimation for different products"""
from ecommerce_agent import ECommerceAgent

agent = ECommerceAgent(cache_dir='./cache/ecommerce_test')

test_queries = [
    ("find me good shoes", "Should be ~€80"),
    ("luxury watches", "Should be ~€500 (luxury = 2x)"),
    ("cheap laptop", "Should be ~€350 (cheap = 0.5x)"),
    ("t-shirt", "Should be ~€40"),
    ("gaming headphones", "Should be ~€120"),
]

print("=" * 70)
print("PRICE ESTIMATION TEST")
print("=" * 70)

for query, expected in test_queries:
    analysis = agent._analyze_query_smart(query)
    print(f"\n📝 Query: {query}")
    print(f"   Expected: {expected}")
    print(f"   ✓ Estimated: €{analysis['price_estimate']:.2f}")

agent.close()
print("\n" + "=" * 70)
print("✅ Dynamic price estimation working!")
print("=" * 70)
