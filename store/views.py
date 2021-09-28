from accounts.models import UserProfile
from django.contrib import messages
from .forms import ReviewForm
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, ProductGallery, ReviewRating
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from orders.models import OrderProduct
from django.core.paginator import Paginator

# Create your views here.
def store(request, cslug=None):
    categories = None
    products = None

    if cslug != None:
        categories = get_object_or_404(Category, slug = cslug)
        products = Product.objects.filter(category = categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        counter = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        counter = products.count()
        
    context = {
        'products':paged_products,
        'counter':counter,
    }

    return render(request, 'store/store.html', context)

def product_detail(request, cslug, product_slug):
    try:
        single_product = Product.objects.get(category__slug = cslug, slug = product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    try:
        userprofile = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        userprofile = None
    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery,
        'userprofile':userprofile,
    }
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            counter = products.count()
    context = {
        'products':products,
        'counter':counter,
    }
    return render(request, 'store/store.html', context)

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
                data.review = form.cleaned_data['review']
                data.rating = form.cleaned_data['rating']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                messages.ERROR(request, "Something went wrong!")