# from django.http import render
from django.shortcuts import render
from store.models import EngagementEvent, Product, ReviewRating
from store.utils import time_decay_weighted_score

# def home(request):
#     products = Product.objects.all().filter(is_available=True).order_by('created_date')
#      # get the review
#     for product in products:
#         reviews = ReviewRating.objects.filter(product_id = product.id, status=True)
#     context={
#         'products': products,
#         'reviews' :reviews
#     }
#     return render(request, 'home.html',context)


def home(request):
    products = Product.objects.filter(is_available=True).order_by('created_date')

    # Trending products calculation
    trending = []
    for product in products:
        events = EngagementEvent.objects.filter(product=product)
        score = time_decay_weighted_score(events)
        trending.append((product, score))
    trending.sort(key=lambda x: x[1], reverse=True)
    trending_products = [p for p, s in trending[:4]]  # Top 5 trending

    # Reviews (optional: you can keep this if you use it in your template)
    reviews = {}
    for product in products:
        reviews[product.id] = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'trending_products': trending_products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)