from django.shortcuts import redirect, render, get_object_or_404
from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm
from .models import EngagementEvent, Product, ProductGallery, ReviewRating
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
import numpy as np









# Create your views here.
# def store(request, category_slug=None):
#     categories = None
#     products = None
    
#     # Get min and max price from GET parameters
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
    
#     if category_slug is not None:
#         categories = get_object_or_404(Category, slug=category_slug)
#         products = Product.objects.filter(category=categories, is_available=True)
#         paginator = Paginator(products, 2)  # Show 6 products per page
#         page = request.GET.get('page')
#         paged_products = paginator.get_page(page)
        
#         product_count = products.count()
#     else:
#         products = Product.objects.all().filter(is_available=True).order_by('id')
#         paginator = Paginator(products, 6)  # Show 6 products per page
#         page = request.GET.get('page')
#         paged_products = paginator.get_page(page)
#         product_count = products.count()    
        
#     context={
#         'products': paged_products,
#         'product_count': product_count,
#         # 'paged_products': paged_products,
#     }
#     return render(request, 'store/store.html', context)


def store(request, category_slug=None):
    categories = None
    products = None

    # Get min and max price from GET parameters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')

    try:
        if min_price is not None and min_price != '':
            min_price = int(min_price)
            products = products.filter(price__gte=min_price)
        if max_price is not None and max_price != '':
            max_price = int(max_price)
            products = products.filter(price__lte=max_price)
    except ValueError:
        pass  # Ignore invalid input
    
    
    
    # Get sort option from GET parameters
    sort = request.GET.get('sort')
    products = list(products)
    n = len(products)

    # Bubble sort implementation 
    products = list(products)
    n = len(products)
    
    if sort == 'name_asc':
        for i in range(n):
            for j in range(0, n-i-1):
                if products[j].product_name.strip().lower() > products[j+1].product_name.strip().lower():
                    products[j], products[j+1] = products[j+1], products[j]
    elif sort == 'name_desc':
        for i in range(n):
            for j in range(0, n-i-1):
                if products[j].product_name.strip().lower() < products[j+1].product_name.strip().lower():
                    products[j], products[j+1] = products[j+1], products[j]
    elif sort == 'price_asc':
        for i in range(n):
            for j in range(0, n-i-1):
                if products[j].price > products[j+1].price:
                    products[j], products[j+1] = products[j+1], products[j]
    elif sort == 'price_desc':
        for i in range(n):
            for j in range(0, n-i-1):
                if products[j].price < products[j+1].price:
                    products[j], products[j+1] = products[j+1], products[j]
    elif sort == 'date_new':
        for i in range(n):
            for j in range(0, n-i-1):
                if products[j].created_date < products[j+1].created_date:
                    products[j], products[j+1] = products[j+1], products[j]
    elif sort == 'date_old':
        for i in range(n):
            for j in range(0, n-i-1):
                if products[j].created_date > products[j+1].created_date:
                    products[j], products[j+1] = products[j+1], products[j]
                    


    paginator = Paginator(products, 6)  # Show 6 products per page
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    # product_count = products.count()
    product_count = len(products) 

    context = {
        'products': paged_products,
        'product_count': product_count,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'store/store.html', context)




def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product =single_product).exists()
        
    except Exception as e:
        raise e   
    
    # Log engagement event (product view)
    EngagementEvent.objects.create(
        product=single_product,
        user=request.user if request.user.is_authenticated else None,
        event_type='view'
    )
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct=None
    else:
        orderproduct = None
            

        
    # get the review
    reviews = ReviewRating.objects.filter(product_id = single_product.id, status=True)
    
    #get product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct' :orderproduct,
        'reviews' : reviews,
        'product_gallery' : product_gallery
    } 
    return render(request, 'store/product_detail.html', context)


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    
    if keyword:
        # Simple linear search approach - more efficient for smaller datasets
        keyword_lower = keyword.lower()
        matched_products = []
        
        # Get all available products
        all_products = Product.objects.filter(is_available=True)
        
        # Linear search with scoring
        for product in all_products:
            score = 0
            product_name_lower = product.product_name.lower()
            description_lower = product.description.lower() if product.description else ""
            
            # Exact match in product name (highest score)
            if keyword_lower == product_name_lower:
                score = 100
            # Starts with keyword
            elif product_name_lower.startswith(keyword_lower):
                score = 90
            # Contains keyword in product name
            elif keyword_lower in product_name_lower:
                score = 80
            # Contains keyword in description
            elif keyword_lower in description_lower:
                score = 70
            # Partial match (word by word)
            else:
                keyword_words = keyword_lower.split()
                name_words = product_name_lower.split()
                desc_words = description_lower.split()
                
                name_matches = sum(1 for kw in keyword_words if any(kw in nw for nw in name_words))
                desc_matches = sum(1 for kw in keyword_words if any(kw in dw for dw in desc_words))
                
                if name_matches > 0 or desc_matches > 0:
                    score = 50 + (name_matches * 10) + (desc_matches * 5)
            
            if score > 0:
                # Add score as a temporary attribute for sorting
                product.search_score = score
                matched_products.append(product)
        
        # Sort by score descending
        matched_products.sort(key=lambda p: p.search_score, reverse=True)
        
    else:
        matched_products = Product.objects.filter(is_available=True)

    context = {
        'products': matched_products,
        'product_count': len(matched_products),
        'keyword': keyword,
    }
    return render(request, 'store/store.html', context)


def autocomplete(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) | Q(description__icontains=query)
        ).values_list('product_name', flat=True).distinct()[:10]

        suggestions = list(products)

    return JsonResponse(suggestions, safe=False)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            
            
            

