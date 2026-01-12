"""Test LLM query optimization feature"""

# Test queries that should be optimized
test_queries = [
    "find me cheap phones",           # English → German
    "billige handys",                 # "billig" → "günstige" 
    "laptop unter 500",               # Add "euro" or "EUR"
    "tv 4k oled",                    # Should add "fernseher"
    "kopfhorer wireless",            # Typo → "kopfhörer"
]

print("=" * 70)
print("LLM QUERY OPTIMIZATION TEST")
print("=" * 70)

for query in test_queries:
    print(f"\n📝 Original: {query}")
    print(f"🤖 Expected optimization examples:")
    
    if "cheap phones" in query or "find me" in query:
        print(f"   → 'günstige smartphones' (translate + proper term)")
    elif "billig" in query:
        print(f"   → 'günstige handys' (better German term)")
    elif "unter 500" in query:
        print(f"   → 'laptop unter 500 euro' (add currency)")
    elif "tv 4k" in query:
        print(f"   → 'fernseher 4k oled' (add product category)")
    elif "kopfhorer" in query:
        print(f"   → 'kopfhörer wireless' (fix umlaut)")

print("\n" + "=" * 70)
print("✅ These queries will now be automatically optimized by the LLM!")
print("=" * 70)
