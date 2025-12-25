def search_products(query, category=None, min_price=None, max_price=None):
    """Search products in catalog"""
    results = []
    
    # Search logic here
    if query:
        results = filter_by_query(query)
    
    if category:
        results = filter_by_category(results, category)
    
    if min_price or max_price:
        results = filter_by_price(results, min_price, max_price)
    
    return results

def filter_by_query(query):
    """Filter products by search query"""
    # Implementation here
    return []

def filter_by_category(products, category):
    """Filter products by category"""
    return [p for p in products if p.get('category') == category]

def filter_by_price(products, min_price, max_price):
    """Filter products by price range"""
    filtered = []
    for p in products:
        price = p.get('price', 0)
        if min_price and price < min_price:
            continue
        if max_price and price > max_price:
            continue
        filtered.append(p)
    return filtered
