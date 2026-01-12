"""Test the improved e-commerce agent"""
from ecommerce_agent import ECommerceAgent

def test_search():
    print("=" * 70)
    print("TESTING E-COMMERCE AGENT - IMPROVED VERSION")
    print("=" * 70)
    
    agent = ECommerceAgent(cache_dir='./cache/ecommerce_test')
    
    # Test query for smartphones
    query = "günstige smartphones"
    print(f"\n📱 Test Query: {query}\n")
    
    products = agent.search_products(query, max_results=10)
    
    print("\n" + "=" * 70)
    print(f"RESULTS SUMMARY: {len(products)} products found")
    print("=" * 70)
    
    if products:
        print("\n📦 PRODUCT DETAILS:\n")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.title}")
            print(f"   💰 Price: {product.price:.2f} EUR" if product.price else "   💰 Price: Not available")
            print(f"   🏪 Merchant: {product.merchant}")
            print(f"   ⭐ Rating: {product.rating}" if product.rating else "   ⭐ Rating: N/A")
            print(f"   🔗 {product.url[:80]}...")
            print()
    else:
        print("\n❌ No products found!")
        print("\nUsing fallback results:")
        fallback = agent.get_fallback_results(query)
        for i, product in enumerate(fallback, 1):
            print(f"{i}. {product.title}")
            print(f"   🔗 {product.url}")
            print()
    
    agent.close()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_search()
