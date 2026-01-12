"""Debug test to see what HTML we're actually getting"""
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()

# Test Amazon
print("=" * 70)
print("TESTING AMAZON.DE HTML STRUCTURE")
print("=" * 70)

url = "https://www.amazon.de/s?k=smartphone"
headers = {
    'User-Agent': ua.random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
    'DNT': '1',
}

print(f"\n🔍 Fetching: {url}")
print(f"User-Agent: {headers['User-Agent'][:60]}...")

try:
    response = requests.get(url, headers=headers, timeout=20)
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Content Length: {len(response.text)} bytes")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find ANY product-like divs
        print("\n" + "=" * 70)
        print("Looking for product containers...")
        print("=" * 70)
        
        # Try various selectors
        selectors = [
            ('data-component-type', 's-search-result'),
            ('data-asin', True),
            ('class', 'sg-col-inner'),
            ('class', 's-result-item'),
        ]
        
        for attr_name, attr_value in selectors:
            if attr_value is True:
                items = soup.find_all('div', attrs={attr_name: True})
            else:
                items = soup.find_all('div', {attr_name: attr_value})
            
            print(f"\n{attr_name}={attr_value}: Found {len(items)} elements")
            
            if items and len(items) > 0:
                # Show first item structure
                print(f"\n📦 First item HTML (first 500 chars):")
                print(str(items[0])[:500])
                print("...")
                
                # Try to find title
                title = items[0].find('h2')
                if title:
                    print(f"\n✓ Title found: {title.get_text(strip=True)[:80]}")
                else:
                    print("\n✗ No <h2> title found")
                
                # Try to find price
                price = items[0].find('span', class_='a-price-whole')
                if price:
                    print(f"✓ Price found: {price.get_text(strip=True)}")
                else:
                    print("✗ No price with class 'a-price-whole'")
                    # Try alternative
                    price_alt = items[0].find('span', class_='a-price')
                    if price_alt:
                        print(f"✓ Alternative price found: {price_alt.get_text(strip=True)}")
        
        # Check if we're being blocked
        if 'robot' in response.text.lower() or 'captcha' in response.text.lower():
            print("\n❌ WARNING: Possible bot detection / CAPTCHA!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
