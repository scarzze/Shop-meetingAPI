import requests
from collections import Counter
from config import Config

def get_product_suggestions(profile):
    # Get user's wishlist items
    wishlist_items = profile.wishlist_items
    
    # Fetch product details and extract categories
    categories = []
    for item in wishlist_items:
        try:
            response = requests.get(f"{Config.PRODUCT_SERVICE_URL}/products/{item.product_id}")
            if response.status_code == 200:
                product = response.json()
                if 'category' in product:
                    categories.append(product['category'])
        except requests.RequestException:
            continue
    
    # Find most common categories
    if not categories:
        return []
    
    category_counts = Counter(categories)
    top_categories = [category for category, _ in category_counts.most_common(3)]
    
    # Get product suggestions based on top categories
    suggestions = []
    try:
        for category in top_categories:
            response = requests.get(
                f"{Config.PRODUCT_SERVICE_URL}/products",
                params={'category': category, 'limit': 3}
            )
            if response.status_code == 200:
                products = response.json()
                suggestions.extend(products)
    except requests.RequestException:
        pass
    
    return suggestions[:6]  # Return top 6 suggestions