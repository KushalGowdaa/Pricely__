from django.shortcuts import render

# Create your views here.

# products/views.py
import requests
from django.http import JsonResponse
import os

API_KEY = os.environ.get('KEY')

def fetch_amazon_data(query):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    params = {"query": query,
              "country":'IN'}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

def fetch_flipkart_data(query):
    url = "https://real-time-flipkart-api.p.rapidapi.com/product-search"
    params = {"q": query}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "real-time-flipkart-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# def fetch_ebay_data(query):
#     url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}"
#     headers = {
#         'Authorization': 'Bearer your_ebay_oauth_token',
#         'Content-Type': 'application/json',
#     }
#     response = requests.get(url, headers=headers)
#     return response.json()

def safe_float_conversion(value):
    try:
        # Remove currency symbols and commas, then convert to float
        cleaned_value = value.replace('₹', '').replace(',', '').strip()
        return float(cleaned_value)  # Convert to float
    except (ValueError, TypeError):
        return None

def compare_prices(request):
    query = request.GET.get('query')
    
    if query:
        # Fetch product data from each platform
        amazon_data = fetch_amazon_data(query)
        flipkart_data = fetch_flipkart_data(query)


        amzn_product_url = amazon_data['data']['products'][0]['product_url']
        amzn_product_image = amazon_data['data']['products'][0]['product_photo']
        flipkart_product_url = flipkart_data['products'][0]['url']
        flipkart_img = flipkart_data['products'][0]['images'][0]
        amazon_product_title = amazon_data['data']['products'][0]['product_title']

        flipkart_product_title = flipkart_data['products'][0]['title']

        # Extract the first product's price from each platform
        comparison = {
            'amazon': safe_float_conversion(amazon_data['data']['products'][0]['product_price'])  if amazon_data.get('data') and amazon_data['data'].get('products') else None,
            'flipkart': flipkart_data['products'][0]['price'] if flipkart_data.get('products') else None,
        }
        
        min_site = min(comparison, key=lambda k: comparison[k] if comparison[k] is not None else float('inf'))
        min_price = comparison[min_site]
        
        # savings_percentage = None
        savings_message = None
        if comparison['amazon'] is not None and comparison['flipkart'] is not None:
            if min_site == 'amazon':
                flipkart_price = comparison['flipkart']
                savings_percentage = round(((flipkart_price - min_price) / flipkart_price) * 100, 2)
                savings_message = f'You will save {savings_percentage}% on Amazon compared to Flipkart'
            else : 
                amazon_price = comparison['amazon']
                savings_percentage = round(((amazon_price - min_price) / amazon_price) * 100, 2)
                savings_message = f'You will save {savings_percentage}% on Flipkart compared to Amazon'

        return JsonResponse({
            'comparison': comparison,
            'message': savings_message,
            'minPrice': min_price,
            'minSite': min_site,
            'savings': savings_percentage,
            'amzn_product_title': amazon_product_title,
            'flipkart_product_title': flipkart_product_title,
            'amzn_product_url': amzn_product_url,
            'amzn_product_image': amzn_product_image,
            'flipkart_product_url': flipkart_product_url,
            'flipkart_image': flipkart_img
        })
    
    return JsonResponse({'error': 'Please provide a search query.'}, status=400)

def get_suggestions(request):
    query = request.GET.get('query', '')
    if not query :
        return JsonResponse({'error no query is provided.'}, status = 400)

    headers = {
        "x-rapidapi-key": os.environ.get('AMZN_API_KEY'),
        "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com"  
    } 

    url = f"https://real-time-flipkart-api.p.rapidapi.com/product-search"
    params = {
        "query": query,
        "country": "IN"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        products = data.get('products', [])
        suggestions = [
            {
                'title': product['product_title'],
                'image': product['product_photo']
            } for product in products [:5]
        ]
        return JsonResponse({"suggestions": suggestions}, status = 200)
    return JsonResponse({"Error could not find the product"}, status = 500)
