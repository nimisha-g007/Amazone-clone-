from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Product


def home(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'store/home.html', {
        'products': products,
        'query': query,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {
        'product': product,
    })


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        if product.stock > 0:
            cart = request.session.get('cart', {})
            key = str(product.id)
            quantity = int(cart.get(key, 0))

            if quantity < product.stock:
                cart[key] = quantity + 1
                request.session['cart'] = cart

    return redirect('cart')


def cart(request):
    cart_data = request.session.get('cart', {})
    items = []
    total = 0

    for product_id, quantity in cart_data.items():
        product = Product.objects.filter(id=product_id).first()

        if product:
            quantity = int(quantity)
            subtotal = product.price * quantity
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })
            total += subtotal

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total,
    })


def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart_data = request.session.get('cart', {})
        cart_data.pop(str(product_id), None)
        request.session['cart'] = cart_data

    return redirect('cart')