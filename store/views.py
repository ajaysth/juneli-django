from django.shortcuts import render, get_object_or_404
from category.models import Category
from .models import Product
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

import numpy as np







# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 2)  # Show 6 products per page
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)  # Show 6 products per page
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()    
        
    context={
        'products': paged_products,
        'product_count': product_count,
        # 'paged_products': paged_products,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product =single_product).exists()
        
    except Exception as e:
        raise e   
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
    } 
    return render(request, 'store/product_detail.html', context)


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    
    if keyword:
        filtered_products = Product.objects.filter(
            Q(product_name__icontains=keyword) | Q(description__icontains=keyword)
        )
        
        if filtered_products.exists():
            combined_texts = [
                f"{product.product_name} {product.description}" for product in filtered_products
            ]
            corpus = combined_texts + [keyword]

            # Use char-level ngrams for partial substring matching
            vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5))
            tfidf_matrix = vectorizer.fit_transform(corpus)

            cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

            matched_indices = np.where(cosine_sim > 0)[0]
            ranked_indices = matched_indices[np.argsort(cosine_sim[matched_indices])[::-1]]

            matched_products = [filtered_products[int(i)] for i in ranked_indices]
        else:
            matched_products = Product.objects.none()
    else:
        matched_products = Product.objects.all()

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