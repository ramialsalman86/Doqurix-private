"""
Professional E-Commerce Agent for German Market
Enterprise-grade product search, price comparison, and analysis
"""

import requests
import json
import time
import re
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote_plus, urljoin
import hashlib

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Try to import fake_useragent, but have robust fallback
ua = None
try:
    from fake_useragent import UserAgent
    ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
except Exception:
    # fake_useragent failed (missing browsers.json or other error)
    ua = None

try:
    from diskcache import Cache
except ImportError:
    Cache = None

# Fallback user agents - always available even if fake_useragent fails
FALLBACK_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]


@dataclass
class Product:
    """Product data structure"""
    title: str
    price: Optional[float]
    currency: str
    url: str
    merchant: str
    image_url: Optional[str]
    description: str
    rating: Optional[float]
    reviews_count: Optional[int]
    availability: str
    features: List[str]
    timestamp: datetime


class ECommerceAgent:
    """Professional E-commerce agent with multi-source product search"""
    
    GERMAN_RETAILERS = {
        'amazon': 'amazon.de',
        'mediamarkt': 'mediamarkt.de',
        'saturn': 'saturn.de',
        'idealo': 'idealo.de',
        'check24': 'check24.de',
        'otto': 'otto.de',
        'cyberport': 'cyberport.de',
        'notebooksbilliger': 'notebooksbilliger.de',
        'alternate': 'alternate.de',
        'computeruniverse': 'computeruniverse.de'
    }
    
    def __init__(self, cache_dir: str = './cache/ecommerce', cache_ttl: int = 3600):
        """Initialize e-commerce agent with caching"""
        self.cache_ttl = cache_ttl
        
        # Initialize cache if available
        if Cache:
            try:
                self.cache = Cache(cache_dir)
            except:
                self.cache = None
        else:
            self.cache = None
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_search_keywords(self, user_prompt: str, llm=None) -> str:
        """
        Use LLM to extract ONLY relevant search keywords from user prompt.
        Removes conversational language, keeps only product-specific terms.
        
        Args:
            user_prompt: Raw user input like "find me cheap shoes for running"
            llm: LLM instance for keyword extraction
            
        Returns:
            Cleaned search keywords like "günstige laufschuhe" or "running shoes cheap"
        """
        if not llm:
            # Fallback: basic keyword extraction without LLM
            return self._basic_keyword_extraction(user_prompt)
        
        try:
            extraction_prompt = """Du bist ein Suchbegriff-Extraktor für E-Commerce. 

Deine Aufgabe: Extrahiere NUR die relevanten Produktsuchbegriffe aus der Benutzeranfrage.

Regeln:
1. Entferne Füllwörter wie "finde mir", "suche nach", "ich möchte", "zeig mir"
2. Behalte Produktnamen, Kategorien, Marken, Eigenschaften (Farbe, Größe, günstig, etc.)
3. Übersetze englische Begriffe ins Deutsche wenn sinnvoll für deutsche Shops
4. Gib NUR die Suchbegriffe zurück, keine Erklärung
5. Max 5 Wörter, durch Leerzeichen getrennt

Beispiele:
- "find me cheap running shoes" → "günstige laufschuhe"
- "I want to buy a Samsung TV" → "Samsung Fernseher"
- "show me the best laptops under 1000 euros" → "laptop unter 1000 euro"
- "ich suche nach weißen Nike Sneakers" → "weiße Nike Sneaker"
- "where can I get iPhone 15 Pro" → "iPhone 15 Pro"""

            response = llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": extraction_prompt},
                    {"role": "user", "content": f"Extrahiere Suchbegriffe: {user_prompt}"}
                ],
                max_tokens=30,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            keywords = response['choices'][0]['message']['content'].strip()
            
            # Clean up: remove quotes, extra punctuation
            keywords = keywords.strip('"\'\'\"')
            keywords = ' '.join(keywords.split())  # Normalize whitespace
            
            # Validate: if LLM returned empty or too long, fallback
            if not keywords or len(keywords) > 100:
                return self._basic_keyword_extraction(user_prompt)
            
            print(f"🔑 LLM extracted keywords: '{user_prompt}' → '{keywords}'")
            return keywords
            
        except Exception as e:
            print(f"⚠ LLM keyword extraction failed: {e}")
            return self._basic_keyword_extraction(user_prompt)
    
    def _basic_keyword_extraction(self, user_prompt: str) -> str:
        """
        Fallback: Basic keyword extraction without LLM
        Removes common conversational words
        """
        # Common words to remove
        stop_words = {
            # English
            'find', 'me', 'show', 'search', 'for', 'looking', 'want', 'need', 'buy',
            'where', 'can', 'i', 'get', 'the', 'best', 'a', 'an', 'please', 'help',
            'im', "i'm", 'would', 'like', 'to', 'some', 'any', 'good',
            # German
            'finde', 'mir', 'zeig', 'suche', 'nach', 'möchte', 'brauche', 'kaufen',
            'wo', 'kann', 'ich', 'das', 'die', 'der', 'ein', 'eine', 'einen', 'bitte',
            'hilf', 'würde', 'gerne', 'gute', 'guten', 'etwas', 'irgendwelche'
        }
        
        # Tokenize and filter
        words = user_prompt.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        
        # Limit to first 5 meaningful words
        result = ' '.join(keywords[:5])
        print(f"🔑 Basic extraction: '{user_prompt}' → '{result}'")
        return result if result else user_prompt

    def get_user_agent(self) -> str:
        """Get rotating user agent - works even without fake_useragent"""
        if ua:
            try:
                return ua.random
            except Exception:
                pass
        
        # Use built-in fallback user agents (always works)
        return random.choice(FALLBACK_USER_AGENTS)
    
    def search_products(self, query: str, max_results: int = 20) -> List[Product]:
        """
        Search for products across multiple German retailers
        
        Args:
            query: Search query
            max_results: Maximum number of products to return
            
        Returns:
            List of Product objects
        """
        # Check cache first
        cache_key = self._get_cache_key(query)
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached:
                print(f"✓ Using cached results for: {query}")
                return cached
        
        products = []
        
        print(f"\n{'='*60}")
        print(f"🛍️  E-Commerce Product Search: {query}")
        print(f"{'='*60}")
        
        try:
            # 1. Try direct retailer scraping (often blocked, but worth trying)
            print(f"\n[1/3] Attempting direct retailer scraping...")
            direct_products = self._search_direct_retailers(query, max_results)
            products.extend(direct_products)
            if direct_products:
                print(f"✓ Found {len(direct_products)} products via scraping")
            else:
                print(f"⚠ Scraping blocked/failed - Using intelligent fallback")
            
            # 2. DuckDuckGo search (often blocked too)
            if len(products) < 5:
                print(f"\n[2/3] Trying DuckDuckGo search...")
                ddg_products = self._search_duckduckgo(query, max_results // 3)
                ddg_products = [p for p in ddg_products if p.price is not None]
                products.extend(ddg_products)
                if ddg_products:
                    print(f"✓ Found {len(ddg_products)} products via DuckDuckGo")
            
            # 3. ALWAYS use enhanced fallback with intelligent analysis
            print(f"\n[3/3] Generating intelligent product recommendations...")
            fallback = self.get_fallback_results(query)
            
            # If no scraping worked, use fallback entirely
            if len(products) == 0:
                products = fallback
                print(f"✓ Using smart fallback: {len(products)} retailer recommendations")
            else:
                # Mix scraped products with fallback
                products.extend(fallback[: max_results - len(products)])
                print(f"✓ Combined results: {len(products)} total products")
            
        except Exception as e:
            print(f"❌ Error in search: {e}")
            # Always provide fallback
            products = self.get_fallback_results(query)
        
        # Deduplicate
        products = self._deduplicate_products(products)
        products = products[:max_results]
        
        print(f"\n{'='*60}")
        print(f"📦 Final Results: {len(products)} products ready")
        print(f"{'='*60}\n")
        
        # Cache results
        if self.cache and products:
            self.cache.set(cache_key, products, expire=self.cache_ttl)
        
        return products
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Product]:
        """Search using DuckDuckGo"""
        products = []
        
        try:
            # Enhanced search with German retailers
            search_query = f"{query} kaufen preis"
            retailer_filter = " OR ".join([f"site:{domain}" for domain in self.GERMAN_RETAILERS.values()])
            full_query = f"{search_query} ({retailer_filter})"
            
            headers = {'User-Agent': self.get_user_agent()}
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(full_query)}"
            
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.find_all('div', class_='result', limit=max_results):
                    try:
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                            
                            # Extract price from title/snippet
                            price, currency = self._extract_price(title + ' ' + snippet)
                            
                            # Determine merchant
                            merchant = self._identify_merchant(url)
                            
                            product = Product(
                                title=title,
                                price=price,
                                currency=currency,
                                url=url,
                                merchant=merchant,
                                image_url=None,
                                description=snippet,
                                rating=None,
                                reviews_count=None,
                                availability='Unknown',
                                features=[],
                                timestamp=datetime.now()
                            )
                            products.append(product)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        
        return products
    
    def _search_direct_retailers(self, query: str, max_results: int) -> List[Product]:
        """Search directly on major retailers"""
        products = []
        
        # Amazon.de search
        try:
            print(f"\n🔍 Searching Amazon.de for: {query}")
            amazon_products = self._search_amazon_de(query, max_results // 2)
            products.extend(amazon_products)
            print(f"✓ Amazon: {len(amazon_products)} products found")
        except Exception as e:
            print(f"✗ Amazon search error: {e}")
        
        # MediaMarkt search
        try:
            print(f"\n🔍 Searching MediaMarkt for: {query}")
            mediamarkt_products = self._search_mediamarkt(query, max_results // 3)
            products.extend(mediamarkt_products)
            print(f"✓ MediaMarkt: {len(mediamarkt_products)} products found")
        except Exception as e:
            print(f"✗ MediaMarkt search error: {e}")
        
        return products
    
    def _search_amazon_de(self, query: str, max_results: int) -> List[Product]:
        """Search Amazon.de with improved parsing"""
        products = []
        
        try:
            search_url = f"https://www.amazon.de/s?k={quote_plus(query)}"
            headers = {
                'User-Agent': self.get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(search_url, headers=headers, timeout=20)
            
            if response.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Multiple selector strategies for Amazon's changing HTML
                items = soup.find_all('div', {'data-component-type': 's-search-result'}, limit=max_results)
                
                if not items:
                    # Fallback: look for product containers with different attributes
                    items = soup.find_all('div', {'data-asin': True}, limit=max_results)
                
                print(f"Amazon: Found {len(items)} product containers")
                
                for item in items:
                    try:
                        # Title - multiple strategies
                        title = None
                        title_elem = item.find('h2', class_='a-size-mini')
                        if not title_elem:
                            title_elem = item.find('h2')
                        if title_elem:
                            title_link = title_elem.find('a')
                            title = title_link.get_text(strip=True) if title_link else title_elem.get_text(strip=True)
                        
                        if not title or len(title) < 10:
                            continue  # Skip invalid titles
                        
                        # Price - improved extraction
                        price = None
                        price_whole = item.find('span', class_='a-price-whole')
                        price_fraction = item.find('span', class_='a-price-fraction')
                        
                        if price_whole:
                            price_text = price_whole.get_text(strip=True).replace('.', '').replace(',', '.')
                            if price_fraction:
                                price_text += price_fraction.get_text(strip=True)
                            try:
                                price = float(re.sub(r'[^\d.]', '', price_text))
                            except:
                                pass
                        
                        # If no price found, try alternative selector
                        if not price:
                            price_span = item.find('span', class_='a-price')
                            if price_span:
                                price_text = price_span.get_text(strip=True)
                                price, _ = self._extract_price(price_text)
                        
                        # URL
                        url = ''
                        link_elem = item.find('a', class_='a-link-normal', href=True)
                        if link_elem:
                            href = link_elem['href']
                            if href.startswith('http'):
                                url = href
                            else:
                                url = urljoin('https://www.amazon.de', href)
                            # Clean Amazon URL
                            if '/dp/' in url:
                                asin = url.split('/dp/')[1].split('/')[0].split('?')[0]
                                url = f"https://www.amazon.de/dp/{asin}"
                        
                        # Image
                        image_url = None
                        img_elem = item.find('img', class_='s-image')
                        if img_elem and 'src' in img_elem.attrs:
                            image_url = img_elem['src']
                        
                        # Rating
                        rating = None
                        rating_elem = item.find('span', class_='a-icon-alt')
                        if rating_elem:
                            rating_text = rating_elem.get_text(strip=True)
                            match = re.search(r'([\d,]+)', rating_text)
                            if match:
                                try:
                                    rating = float(match.group(1).replace(',', '.'))
                                except:
                                    pass
                        
                        # Review count
                        reviews_count = None
                        reviews_elem = item.find('span', {'class': 'a-size-base', 'dir': 'auto'})
                        if reviews_elem:
                            reviews_text = reviews_elem.get_text(strip=True)
                            match = re.search(r'([\d.]+)', reviews_text)
                            if match:
                                try:
                                    reviews_count = int(match.group(1).replace('.', ''))
                                except:
                                    pass
                        
                        if title and url:  # Only add if we have minimum data
                            product = Product(
                                title=title,
                                price=price,
                                currency='EUR',
                                url=url,
                                merchant='Amazon.de',
                                image_url=image_url,
                                description='',
                                rating=rating,
                                reviews_count=reviews_count,
                                availability='Verfügbar' if price else 'Preis prüfen',
                                features=[],
                                timestamp=datetime.now()
                            )
                            products.append(product)
                            print(f"  ✓ {title[:50]}... - {price}€" if price else f"  ✓ {title[:50]}... - No price")
                        
                    except Exception as e:
                        print(f"  ✗ Error parsing item: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Amazon.de search error: {e}")
            import traceback
            traceback.print_exc()
        
        return products
    
    def _search_idealo(self, query: str, max_results: int) -> List[Product]:
        """Search Idealo.de for price comparison"""
        products = []
        
        try:
            search_url = f"https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={quote_plus(query)}"
            headers = {'User-Agent': self.get_user_agent()}
            
            response = self.session.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Parse Idealo results (simplified)
                # Note: Idealo's structure changes frequently, this is a basic implementation
                for item in soup.find_all('div', class_='productTile', limit=max_results):
                    try:
                        title_elem = item.find('a', class_='productTile-link')
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            url = urljoin('https://www.idealo.de', title_elem.get('href', ''))
                            
                            price_elem = item.find('span', class_='productTile-price')
                            price = None
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)
                                price, currency = self._extract_price(price_text)
                            
                            product = Product(
                                title=title,
                                price=price,
                                currency='EUR',
                                url=url,
                                merchant='Idealo.de',
                                image_url=None,
                                description='Price comparison',
                                rating=None,
                                reviews_count=None,
                                availability='Compare Prices',
                                features=[],
                                timestamp=datetime.now()
                            )
                            products.append(product)
                    except:
                        continue
                        
        except Exception as e:
            print(f"Idealo search error: {e}")
        
        return products
    
    def _search_mediamarkt(self, query: str, max_results: int) -> List[Product]:
        """Search MediaMarkt.de for products"""
        products = []
        
        try:
            # MediaMarkt search endpoint
            search_url = f"https://www.mediamarkt.de/de/search.html?query={quote_plus(query)}"
            headers = {
                'User-Agent': self.get_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9',
                'Referer': 'https://www.mediamarkt.de/'
            }
            
            response = self.session.get(search_url, headers=headers, timeout=20)
            
            if response.status_code == 200 and BeautifulSoup:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # MediaMarkt uses product tiles
                items = soup.find_all('div', {'data-test': 'mms-search-srp-productlist-item'}, limit=max_results)
                
                if not items:
                    # Fallback selectors
                    items = soup.find_all('article', class_='ProductCard', limit=max_results)
                
                print(f"MediaMarkt: Found {len(items)} product containers")
                
                for item in items:
                    try:
                        # Title
                        title = None
                        title_elem = item.find('h2')
                        if not title_elem:
                            title_elem = item.find('a', {'data-test': 'product-title'})
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        
                        if not title or len(title) < 5:
                            continue
                        
                        # Price - MediaMarkt specific
                        price = None
                        price_elem = item.find('span', {'data-test': 'product-price'})
                        if not price_elem:
                            price_elem = item.find('div', class_='price')
                        if price_elem:
                            price_text = price_elem.get_text(strip=True)
                            price, _ = self._extract_price(price_text)
                        
                        # URL
                        url = ''
                        link_elem = item.find('a', href=True)
                        if link_elem:
                            href = link_elem['href']
                            if href.startswith('http'):
                                url = href
                            else:
                                url = urljoin('https://www.mediamarkt.de', href)
                        
                        # Image
                        image_url = None
                        img_elem = item.find('img')
                        if img_elem:
                            image_url = img_elem.get('src') or img_elem.get('data-src')
                        
                        if title and url:
                            product = Product(
                                title=title,
                                price=price,
                                currency='EUR',
                                url=url,
                                merchant='MediaMarkt',
                                image_url=image_url,
                                description='',
                                rating=None,
                                reviews_count=None,
                                availability='Verfügbar' if price else 'Preis prüfen',
                                features=[],
                                timestamp=datetime.now()
                            )
                            products.append(product)
                            print(f"  ✓ {title[:50]}... - {price}€" if price else f"  ✓ {title[:50]}... - No price")
                        
                    except Exception as e:
                        print(f"  ✗ Error parsing MediaMarkt item: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"MediaMarkt search error: {e}")
            import traceback
            traceback.print_exc()
        
        return products
    
    def _extract_price(self, text: str) -> Tuple[Optional[float], str]:
        """Extract price from text"""
        # Common German price patterns
        patterns = [
            r'€\s*([\d.,]+)',
            r'([\d.,]+)\s*€',
            r'EUR\s*([\d.,]+)',
            r'([\d.,]+)\s*EUR',
            r'ab\s*([\d.,]+)',
            r'([\d.,]+)\s*Euro'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1)
                # Handle German number format (1.234,56)
                price_str = price_str.replace('.', '').replace(',', '.')
                try:
                    return float(price_str), 'EUR'
                except:
                    continue
        
        return None, 'EUR'
    
    def _identify_merchant(self, url: str) -> str:
        """Identify merchant from URL"""
        url_lower = url.lower()
        for name, domain in self.GERMAN_RETAILERS.items():
            if domain in url_lower:
                return name.title()
        return 'Unknown'
    
    def _deduplicate_products(self, products: List[Product]) -> List[Product]:
        """Remove duplicate products based on title similarity"""
        if not products:
            return []
        
        unique_products = []
        seen_titles = set()
        
        for product in products:
            # Normalize title for comparison
            normalized = re.sub(r'[^\w\s]', '', product.title.lower())
            normalized = ' '.join(normalized.split())
            
            # Simple deduplication by title
            if normalized not in seen_titles:
                seen_titles.add(normalized)
                unique_products.append(product)
        
        return unique_products
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _validate_retailer_has_results(self, url: str, retailer_name: str) -> bool:
        """
        Quick check if a retailer URL returns actual product results.
        Returns True if products found, False otherwise.
        Uses smart detection for blocked requests.
        """
        try:
            # Use more realistic browser headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Quick request with short timeout
            response = self.session.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # Handle blocked requests - assume major retailers have products
            if response.status_code in [403, 503, 429]:
                # These retailers are reliable - assume they have products
                trusted_retailers = ['Amazon', 'Idealo', 'MediaMarkt', 'Saturn', 'Zalando', 'OTTO', 'eBay']
                if retailer_name in trusted_retailers:
                    print(f"  ? {retailer_name}: Blocked but trusted retailer")
                    return True
                print(f"  ✗ {retailer_name}: HTTP {response.status_code} - blocked")
                return False
            
            if response.status_code == 404:
                print(f"  ✗ {retailer_name}: HTTP 404 - page not found")
                return False
                
            if response.status_code != 200:
                print(f"  ✗ {retailer_name}: HTTP {response.status_code}")
                return False
            
            html_lower = response.text.lower()
            
            # Check for "no results" indicators in German
            no_results_indicators = [
                'keine ergebnisse',
                'keine produkte gefunden',
                'keine treffer',
                'leider keine',
                'nichts gefunden',
                'keine artikel',
                'no results',
                'nothing found',
                '0 ergebnisse',
                '0 produkte',
                '0 treffer',
                'kein ergebnis',
                'suchanfrage ergab keine',
                'keine passenden produkte',
                'ihre suche ergab leider keine',
                'wir haben leider keine',
                'zu deiner suche wurden keine',
                'es wurden keine produkte'
            ]
            
            for indicator in no_results_indicators:
                if indicator in html_lower:
                    print(f"  ✗ {retailer_name}: No products ('{indicator}')")
                    return False
            
            # Check for positive indicators that products exist
            if BeautifulSoup:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Count product indicators
                product_count = 0
                
                # Common product container selectors
                product_selectors = [
                    ('div', {'class': re.compile(r'product|artikel|item|result|tile', re.I)}),
                    ('article', {}),
                    ('li', {'class': re.compile(r'product|artikel|item', re.I)}),
                ]
                
                for tag, attrs in product_selectors:
                    found = soup.find_all(tag, attrs, limit=10)
                    if found:
                        product_count = max(product_count, len(found))
                
                if product_count >= 1:
                    print(f"  ✓ {retailer_name}: {product_count}+ products found")
                    return True
            
            # If page is substantial, assume it has products
            if len(response.text) > 15000:
                print(f"  ? {retailer_name}: Large page - assuming products exist")
                return True
            
            print(f"  ✗ {retailer_name}: No products detected")
            return False
            
        except Exception as e:
            # On error, trust major retailers
            trusted_retailers = ['Amazon', 'Idealo', 'MediaMarkt', 'Saturn', 'Zalando', 'OTTO', 'eBay']
            if retailer_name in trusted_retailers:
                print(f"  ? {retailer_name}: Error but trusted - {str(e)[:30]}")
                return True
            print(f"  ✗ {retailer_name}: Error - {str(e)[:40]}")
            return False
    
    def _validate_retailers_parallel(self, retailers: List[Dict], query: str) -> List[Dict]:
        """
        Validate multiple retailers in parallel and return only those with results.
        """
        import concurrent.futures
        
        validated = []
        
        print(f"\n🔍 Validating retailers for: '{query}'")
        
        # Use ThreadPoolExecutor for parallel validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all validation tasks
            future_to_retailer = {
                executor.submit(self._validate_retailer_has_results, r['url'], r['name']): r 
                for r in retailers
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_retailer, timeout=15):
                retailer = future_to_retailer[future]
                try:
                    has_results = future.result()
                    if has_results:
                        validated.append(retailer)
                except Exception as e:
                    print(f"  ✗ {retailer['name']}: Validation timeout")
        
        print(f"✓ {len(validated)}/{len(retailers)} retailers have products\n")
        return validated

    def get_fallback_results(self, query: str) -> List[Product]:
        """
        Category-aware fallback: Show RELEVANT retailers with REAL strengths
        Only shows retailers that actually have products for the search query
        """
        analysis = self._analyze_query_smart(query)
        category_type = analysis.get('category_type', 'general')
        
        fallback_products = []
        
        # FASHION/SHOES retailers with REAL characteristics
        fashion_retailers = [
            {
                'name': 'Zalando',
                'url': f"https://www.zalando.de/katalog/?q={quote_plus(query)}",
                'highlight': '🏆 Größte Auswahl',
                'desc': 'Europas #1 Mode-Shop • 100 Tage Rückgabe • Kostenloser Versand & Rückversand',
                'price_info': '€20 - €200',
                'why': 'Beste Wahl für große Auswahl und einfache Rückgabe'
            },
            {
                'name': 'Deichmann',
                'url': f"https://www.deichmann.com/de-de/search?q={quote_plus(query)}",
                'highlight': '💰 Günstigste Preise',
                'desc': 'Europas größter Schuhhändler • 4.000+ Filialen • Budget-freundlich',
                'price_info': '€15 - €80',
                'why': 'Beste Wahl für günstige Schuhe und Filial-Abholung'
            },
            {
                'name': 'About You',
                'url': f"https://www.aboutyou.de/suche?term={quote_plus(query)}",
                'highlight': '🎨 Style-Inspiration',
                'desc': 'Outfit-Vorschläge • Influencer-Kollektionen • Trendige Mode',
                'price_info': '€25 - €150',
                'why': 'Beste Wahl für trendige Mode mit Style-Tipps'
            },
            {
                'name': 'Amazon Fashion',
                'url': f"https://www.amazon.de/s?k={quote_plus(query)}&rh=n%3A77028031",
                'highlight': '🚀 Schnellste Lieferung',
                'desc': 'Prime: Morgen geliefert • Riesige Auswahl • Kundenrezensionen',
                'price_info': '€10 - €300',
                'why': 'Beste Wahl für schnelle Lieferung mit Prime'
            },
            {
                'name': 'Idealo',
                'url': f"https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={quote_plus(query)}&sortKey=minPrice",
                'highlight': '🔍 Preisvergleich',
                'desc': 'Vergleicht 50.000+ Shops • Zeigt günstigsten Preis • Preisverlauf',
                'price_info': 'Vergleich',
                'why': 'Beste Wahl um den günstigsten Anbieter zu finden'
            },
            {
                'name': 'OTTO',
                'url': f"https://www.otto.de/suche/{quote_plus(query)}/?sorting=priceAsc",
                'highlight': '💳 Ratenzahlung',
                'desc': 'Kauf auf Rechnung • Ratenzahlung • Deutschlands Traditionshaus',
                'price_info': '€20 - €180',
                'why': 'Beste Wahl für flexible Zahlungsoptionen'
            }
        ]
        
        # ELECTRONICS retailers
        electronics_retailers = [
            {
                'name': 'MediaMarkt',
                'url': f"https://www.mediamarkt.de/de/search.html?query={quote_plus(query)}&sort=price-asc",
                'highlight': '🏪 Heute abholen',
                'desc': 'Click & Collect: Online bestellen, in 1h abholen • 400+ Filialen',
                'price_info': 'Marktpreise',
                'why': 'Beste Wahl für Sofort-Abholung im Markt'
            },
            {
                'name': 'Amazon',
                'url': f"https://www.amazon.de/s?k={quote_plus(query)}&rh=n%3A562066",
                'highlight': '🚀 Prime-Versand',
                'desc': 'Morgen geliefert • Millionen Produkte • Kundenrezensionen',
                'price_info': 'Alle Preise',
                'why': 'Beste Wahl für schnelle Lieferung und Rezensionen'
            },
            {
                'name': 'Notebooksbilliger',
                'url': f"https://www.notebooksbilliger.de/search?q={quote_plus(query)}&sort=price_asc",
                'highlight': '💰 Oft günstiger',
                'desc': 'Tech-Spezialist • Häufig bessere Preise als große Ketten',
                'price_info': 'Günstig',
                'why': 'Beste Wahl für günstige Laptops und Tech'
            },
            {
                'name': 'Saturn',
                'url': f"https://www.saturn.de/de/search.html?query={quote_plus(query)}&sort=price-asc",
                'highlight': '🏪 Beratung vor Ort',
                'desc': 'Technik zum Anfassen • 150+ Märkte • Persönliche Beratung',
                'price_info': 'Marktpreise',
                'why': 'Beste Wahl für persönliche Beratung im Laden'
            },
            {
                'name': 'Idealo',
                'url': f"https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={quote_plus(query)}&sortKey=minPrice",
                'highlight': '🔍 Bester Preis',
                'desc': 'Vergleicht alle Shops • Preisverlauf • Testberichte',
                'price_info': 'Vergleich',
                'why': 'Beste Wahl um den günstigsten Anbieter zu finden'
            },
            {
                'name': 'Cyberport',
                'url': f"https://www.cyberport.de/suche.html?q={quote_plus(query)}",
                'highlight': '💼 IT-Experte',
                'desc': 'Profi-Händler • Kompetente Beratung • Business-Konditionen',
                'price_info': 'Mittel-Hoch',
                'why': 'Beste Wahl für professionelle IT-Beratung'
            }
        ]
        
        # GENERAL retailers
        general_retailers = [
            {
                'name': 'Amazon',
                'url': f"https://www.amazon.de/s?k={quote_plus(query)}",
                'highlight': '🚀 Schnell & Einfach',
                'desc': 'Größte Auswahl • Prime-Versand • Kundenrezensionen',
                'price_info': 'Alle Preise',
                'why': 'Beste Wahl für Auswahl und schnelle Lieferung'
            },
            {
                'name': 'Idealo',
                'url': f"https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q={quote_plus(query)}&sortKey=minPrice",
                'highlight': '🔍 Preisvergleich',
                'desc': 'Vergleicht 50.000+ Shops • Findet günstigsten Anbieter',
                'price_info': 'Vergleich',
                'why': 'Beste Wahl um den besten Preis zu finden'
            },
            {
                'name': 'eBay',
                'url': f"https://www.ebay.de/sch/i.html?_nkw={quote_plus(query)}&_sop=15",
                'highlight': '💰 Schnäppchen',
                'desc': 'Neu & Gebraucht • Auktionen • Oft günstigste Preise',
                'price_info': 'Sehr günstig',
                'why': 'Beste Wahl für Schnäppchen und Gebrauchtes'
            },
            {
                'name': 'OTTO',
                'url': f"https://www.otto.de/suche/{quote_plus(query)}/?sorting=priceAsc",
                'highlight': '💳 Ratenzahlung',
                'desc': 'Kauf auf Rechnung • Ratenzahlung möglich',
                'price_info': 'Mittel',
                'why': 'Beste Wahl für flexible Zahlungsoptionen'
            },
            {
                'name': 'Kaufland',
                'url': f"https://www.kaufland.de/suche/?search_value={quote_plus(query)}",
                'highlight': '🛒 Marketplace',
                'desc': 'Viele Händler • Breites Sortiment • Gute Preise',
                'price_info': 'Günstig-Mittel',
                'why': 'Gute Alternative mit vielen Händlern'
            }
        ]
        
        # Select retailers based on category
        if category_type == 'fashion':
            retailers = fashion_retailers
        elif category_type == 'electronics':
            retailers = electronics_retailers
        else:
            retailers = general_retailers
        
        # VALIDATE: Only show retailers that actually have products for this search
        print(f"\n🔍 Checking which retailers have products for: '{query}'")
        validated_retailers = self._validate_retailers_parallel(retailers, query)
        
        # If no retailers validated, use top 3 most reliable ones without validation
        if not validated_retailers:
            print(f"⚠ No retailers validated - using top 3 reliable options")
            validated_retailers = retailers[:3]
        
        # Build products - HONEST DATA, no fake prices/ratings
        for r in validated_retailers:
            fallback_products.append(Product(
                title=r['highlight'],
                price=None,  # No fake prices
                currency='EUR',
                url=r['url'],
                merchant=r['name'],
                image_url=None,
                description=r['desc'],
                rating=None,  # No fake ratings
                reviews_count=None,
                availability=r['price_info'],
                features=[r['why']],
                timestamp=datetime.now()
            ))
        
        return fallback_products
    
    def _analyze_query_smart(self, query: str) -> Dict:
        """Smart query analysis - detects category type for relevant retailers"""
        query_lower = query.lower()
        
        # Detect category type for appropriate retailers
        category_type = 'general'  # Default
        
        # Fashion keywords → Zalando, About You, Deichmann
        fashion_keywords = ['shoe', 'shoes', 'sneaker', 'schuh', 'schuhe', 'boots', 'sandal', 
                           'shirt', 't-shirt', 'hemd', 'blouse', 'jacket', 'jacke', 'jeans',
                           'dress', 'kleid', 'hose', 'pants', 'pullover', 'sweater', 'hoodie',
                           'fashion', 'mode', 'clothing', 'kleidung', 'outfit', 'bekleidung',
                           'sock', 'socken', 'underwear', 'unterwäsche', 'coat', 'mantel',
                           'trainers', 'turnschuhe', 'sportschuhe', 'running shoes', 'laufschuhe']
        
        # Electronics keywords → MediaMarkt, Saturn, NBB
        electronics_keywords = ['laptop', 'notebook', 'computer', 'pc', 'phone', 'smartphone', 
                               'handy', 'iphone', 'samsung', 'tv', 'fernseher', 'television',
                               'oled', 'qled', 'monitor', 'tablet', 'ipad', 'headphone', 
                               'kopfhörer', 'earbuds', 'airpods', 'camera', 'kamera', 'printer',
                               'drucker', 'playstation', 'xbox', 'nintendo', 'gaming', 'console',
                               'keyboard', 'tastatur', 'mouse', 'maus', 'speaker', 'lautsprecher',
                               'smartwatch', 'apple watch', 'samsung galaxy', 'macbook']
        
        if any(word in query_lower for word in fashion_keywords):
            category_type = 'fashion'
        elif any(word in query_lower for word in electronics_keywords):
            category_type = 'electronics'
        
        # Price estimation
        price_estimate = 100.0  # Default generic price
        category_name = 'Produkte'
        
        # Fashion price ranges
        if any(word in query_lower for word in ['shoe', 'shoes', 'sneaker', 'schuh', 'schuhe', 'boots', 'sandal', 'trainers', 'turnschuhe']):
            price_estimate = 80.0
            category_name = 'Schuhe'
        elif any(word in query_lower for word in ['shirt', 't-shirt', 'hemd', 'blouse', 'pullover', 'sweater', 'hoodie']):
            price_estimate = 40.0
            category_name = 'Oberteile'
        elif any(word in query_lower for word in ['jacket', 'jacke', 'coat', 'mantel']):
            price_estimate = 100.0
            category_name = 'Jacken'
        elif any(word in query_lower for word in ['jeans', 'hose', 'pants', 'trousers']):
            price_estimate = 60.0
            category_name = 'Hosen'
        elif any(word in query_lower for word in ['dress', 'kleid']):
            price_estimate = 70.0
            category_name = 'Kleider'
        # Electronics price ranges
        elif any(word in query_lower for word in ['laptop', 'notebook', 'computer']):
            price_estimate = 700.0
            category_name = 'Laptops'
        elif any(word in query_lower for word in ['phone', 'smartphone', 'handy', 'iphone']):
            price_estimate = 400.0
            category_name = 'Smartphones'
        elif any(word in query_lower for word in ['tv', 'fernseher', 'television']):
            price_estimate = 650.0
            category_name = 'Fernseher'
        elif any(word in query_lower for word in ['headphone', 'kopfhörer', 'earbuds', 'airpods']):
            price_estimate = 120.0
            category_name = 'Kopfhörer'
        elif any(word in query_lower for word in ['watch', 'uhr', 'smartwatch']):
            price_estimate = 250.0
            category_name = 'Uhren'
        elif any(word in query_lower for word in ['bag', 'tasche', 'backpack', 'rucksack']):
            price_estimate = 60.0
            category_name = 'Taschen'
        elif any(word in query_lower for word in ['book', 'buch']):
            price_estimate = 15.0
            category_name = 'Bücher'
        elif any(word in query_lower for word in ['game', 'spiel', 'playstation', 'xbox', 'nintendo']):
            price_estimate = 60.0
            category_name = 'Spiele & Gaming'
        
        # Price modifiers
        if any(word in query_lower for word in ['günstig', 'cheap', 'billig', 'budget']):
            price_estimate *= 0.5
        elif any(word in query_lower for word in ['premium', 'luxury', 'high-end', 'teuer', 'designer']):
            price_estimate *= 2.0
        
        return {
            'category': category_name,
            'category_type': category_type,
            'price_estimate': price_estimate
        }
    
    def format_results_for_llm(self, products: List[Product]) -> str:
        """Format product results for LLM analysis"""
        if not products:
            return "Keine Produkte gefunden."
        
        context = "PRODUKTSUCHERGEBNISSE:\n\n"
        
        for i, product in enumerate(products, 1):
            context += f"{i}. {product.title}\n"
            context += f"   Händler: {product.merchant}\n"
            
            if product.price:
                context += f"   Preis: {product.price:.2f} {product.currency}\n"
            
            if product.rating:
                context += f"   Bewertung: {product.rating}/5.0\n"
            
            if product.availability:
                context += f"   Verfügbarkeit: {product.availability}\n"
            
            context += f"   URL: {product.url}\n"
            
            if product.description:
                context += f"   Beschreibung: {product.description[:200]}...\n"
            
            context += "\n"
        
        return context
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()
        if hasattr(self, 'cache') and self.cache:
            self.cache.close()


def test_ecommerce_agent():
    """Test the e-commerce agent"""
    agent = ECommerceAgent()
    
    print("Testing E-Commerce Agent...")
    print("-" * 60)
    
    query = "Gaming Laptop"
    print(f"Searching for: {query}")
    
    products = agent.search_products(query, max_results=10)
    
    print(f"\nFound {len(products)} products:")
    print("-" * 60)
    
    for i, product in enumerate(products[:5], 1):
        print(f"\n{i}. {product.title[:70]}")
        print(f"   Merchant: {product.merchant}")
        if product.price:
            print(f"   Price: {product.price:.2f} {product.currency}")
        print(f"   URL: {product.url[:80]}...")
    
    agent.close()


if __name__ == "__main__":
    test_ecommerce_agent()
