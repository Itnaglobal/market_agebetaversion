from django.http.response import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Avg, Max, Min
from django.contrib import messages
from .models import *
import time
import os, uuid
from .forms import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from sslcommerz_lib import SSLCOMMERZ
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import date
from datetime import datetime
import string
import random
from ChatApp.models import *
from django.core.mail import send_mail
from decimal import Decimal
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth import get_user_model
from .decorators import has_selleraccount
import uuid



def get_landing_page(request):
    main_logo = MainLogo.objects.all()
    print(main_logo)
    user_session = request.session.get("user", None)
    print(f"{user_session}")
    premium_offers = Offer.objects.filter(is_premium=True)

    if (user_session is None):
        landing_slider = LandingSlider.objects.all().order_by('-id')
        services = Services.objects.all()
        cats = Category.objects.all()

        args = {
            'landing_slider': landing_slider,
            'services': services,
            'cats': cats,
            'main_logo': main_logo,
            "premium_offers": premium_offers
        }
        return render(request, 'landingview/landingPage.html', args)
    else:
        return redirect("buying_view")


# landing Service Wise Offer Page 
# @login_required(login_url='user_login')
def service_wise_offers(request, slug):
    main_logo = MainLogo.objects.all().last()
    service = Services.objects.all()
    offers = Offer.objects.filter(slug=slug)
    cats = Category.objects.all().order_by("-id")[:7]
    args = {
        'service': service,
        'offers': offers,
        'cats': cats,
        'main_logo': main_logo
    }

    return render(request, 'landingview/service_wise_offers.html', args)


@login_required(login_url='user_login')
@has_selleraccount
def view_all_category(request):
    main_logo = MainLogo.objects.all().last()
    cats = Category.objects.all()

    args = {
        'cats': cats,
        'main_logo': main_logo
    }

    return render(request, 'landingview/categories.html', args)


@login_required(login_url='user_login')
@has_selleraccount
def buying_view(request):
    main_logo = MainLogo.objects.all().last()
    offers = Offer.objects.all().order_by('-click')
    cats = Category.objects.all().order_by("-id")[:7]
    all_cats = Category.objects.all()

    # for item in cats:
    #     print(item)
    #     print(len(item.subcategory.all()))

    pop_offers = Offer.objects.filter(is_popular=True)
    pop_web_offers = Offer.objects.filter(pop_web=True)
    pro_offers = Offer.objects.filter(is_pro=True)

    premium_offers = Offer.objects.filter(is_premium=True)

    args = {
        'offers': offers,
        'pop_offers': pop_offers,
        'cats': cats,
        "all_cats": all_cats,
        'pop_web_offers': pop_web_offers,
        "pro_offers": pro_offers,
        'main_logo': main_logo,
        "premium_offers": premium_offers,
    }
    return render(request, 'buyingview/buying_view.html', args)

@login_required(login_url='user_login')
# @has_selleraccount
def offer_details(request, id, slug):
    main_logo = MainLogo.objects.all().last()
    cats = Category.objects.all()
    offers = Offer.objects.filter(id=id, slug=slug).first()
    print("OFFER:", offers)
    print("OFFER PACKAGE:", offers.offermanager_set.all())

    cart_session = request.session.get("cart", None)

    def get_ip(request):
        address = request.META.get('HTTP_X_FORWARDED_FOR')
        if address:
            ip = address.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    ip = get_ip(request)

    print(ip)

    u = DummyUser(user=ip)

    result = DummyUser.objects.filter(Q(user__icontains=ip))

    if result is None:
        u.save()
    c = DummyUser.objects.all().count()
    related_offers = Offer.objects.all()

    # ISSUE ##

    # print(packages)

    args = {
        'offers': offers,
        'c': c,
        'related_offers': related_offers,
        'cats': cats,
        "cart_session": cart_session,
        'main_logo': main_logo
    }
    return render(request, 'buyingview/offers_details.html', args)


def user_registration(request):
    user_session = request.session.get("user", None)
    # if (user_session is None):
    form = UserRegistration()
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            request.session["new_user"] = True
            current_site = get_current_site(request)
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            mail_subject = "Account Verification Link"
            message = render_to_string("accountview/verify.html", {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[send_mail])
            email.send()

            messages.success(request, "Email Sent Please verify your account")
            messages.info(request, "Please Activate Your Account ASAP")

            return redirect('user_login')
    args = {
            'form': form,
            # 'user': user,
        }
    return render(request, 'accountview/registration.html', args)
    # else:
    #     return redirect("buying_view")



# User Registration Function
UserModel = get_user_model()
def activate_account(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        # user = UserModel._default_manager.get(pk=uid)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account is now activated or verified")
        return redirect("user_login")
    else:
        # messages.warning(request, "Invalid Activaton Link Please Try again later")
        # return redirect("user_registration")
        return HttpResponse("Activation Link is invalid")


def user_login(request):
    user_session = request.session.get("user", None)
    new_user = request.session.get("new_user", None)

    if (user_session is None):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Creating user session
                user_session = username
                request.session["user"] = user_session
                login(request, user)
                # print("USER SESSION:")
                # print(request.session.get("user"))
                if new_user is not None:
                    return redirect("extended-user")
                return redirect('buying_view')
            else:
                messages.error(request, "Incorrect username or password!")

        return render(request, 'accountview/login.html')
    else:
        return redirect("buying_view")


def logoutview(request):
    logout(request)
    return redirect('get_landing_page')


@login_required(login_url='user_login')
@has_selleraccount
def seller_profile(request):
    return render(request, 'accountview/seller.html')

# Category Wise Page


@login_required(login_url='user_login')
def buyingViewcategoryWisePage(requrest, offer_id):
    category = Category.objects.all()
    cat_wise_offer = Offer.objects.filter(category_id=offer_id)
    args = {
        "category": category,
        "cat_wise_offer": cat_wise_offer
    }
    return render(requrest, "ladingview/service_wise_offers.html", args)


# Order page
@login_required(login_url='user_login')
@has_selleraccount
def manageOrder(request):
    orders = Checkout.objects.filter(seller=request.user).filter(paid=True).order_by("-id")
    active_orders, late_orders, delivered_orders, completed_orders, cancelled_orders, review_orders = [], [], [], [], [], []

    for order in orders:
        if order.is_complete:
            completed_orders.append(order)
        if order.on_review and order.order_status == "ON REVIEW":
            review_orders.append(order)
        if order.order_status == "ACTIVE":
            active_orders.append(order)
        elif order.order_status == "LATE":
            late_orders.append(order)
        elif order.order_status == "DELIVERED":
            delivered_orders.append(order)
        elif order.order_status == "CANCELLED":
            cancelled_orders.append(order)

    # print(review_orders)
    # print(cancelled_orders)

    args = {
        "active_orders": active_orders,
        "late_orders": late_orders,
        "delivered_orders": delivered_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "review_orders": review_orders
    }

    return render(request, "wasekPart/manage_order.html", args)


# @login_required(login_url='user_login')
# @has_selleraccount
# def get_notificationOffer(request):
#     msg_len = 0
#     chatrooms = ChatRoom.objects.filter(sellers=request.user).order_by("-id")
    
#     for room in chatrooms:
#         msg = Message.objects.filter(chatroom=room)
#         msg_len += len(msg)
        
#     data = {
#         "msg_len": msg_len
#     }
#     return JsonResponse(data, safe=False)

# offers page
@login_required(login_url='user_login')
@has_selleraccount
def manageOffers(request):
    offers = Offer.objects.filter(user=request.user).order_by("-id")
    active_offers, pending_approvals, required_modifications, denieds, pauseds = [], [], [], [], []

    for offer in offers:
        if offer.offer_status == "ACTIVE":
            active_offers.append(offer)
        elif offer.offer_status == "PENDING APPROVAL":
            pending_approvals.append(offer)
        elif offer.offer_status == "REQUIRED MODIFICATION":
            required_modifications.append(offer)
        elif offer.offer_status == "DENIED":
            denieds.append(offer)
        elif offer.offer_status == "PAUSED":
            pauseds.append(offer)

    args = {
        "offers": offers,
        "active_offers": active_offers,
        "pending_approvals": pending_approvals,
        "required_modifications": required_modifications,
        "denieds": denieds,
        "pauseds": pauseds,
    }
    return render(request, "wasekPart/manage_offers.html", args)
    

@login_required(login_url='user_login')
@has_selleraccount
def pausedOffer(request, id):
    if request.method == "POST":
        offer_id = request.POST.get("offer_id", None)
        # print(f"{offer_id}")

        if offer_id is not None:
            try:
                offer_id = int(offer_id)
            except:
                return redirect("manage-offers")
            else:
                try:
                    offer = Offer.objects.get(id=offer_id)
                    offer.offer_status = "PAUSED"
                    offer.save()
                    return redirect("manage-offers")
                except:
                    return redirect("manage-offers")
        else:
            return redirect("manage-offers")
        

@login_required(login_url='user_login')
@has_selleraccount
def deleteOffer(request, id):
    if request.method == "POST":
        delete_id = request.POST.get("delete_id", None)
        # print(f"{delete_id}")

        if delete_id is not None:
            try:
                offer_id = int(delete_id)
            except:
                return redirect("manage-offers")
            else:
                try:
                    offer = Offer.objects.get(id=offer_id)
                    offer.delete()
                    return redirect("manage-offers")
                except:
                    return redirect("manage-offers")
        else:
            return redirect("manage-offers")
# Chat inbox


@login_required(login_url='user_login')
@has_selleraccount
def chatInbox(request):
    all_rooms = ChatRoom.objects.filter(sellers=request.user)
    

    # print("HELLLLLLLLLLLLLLLLLLLLLLLOOOOOOOOOOOOO" + str(all_rooms))
    args = {
        "all_rooms": all_rooms
    }
    return render(request, "wasekPart/chat_inbox.html", args)


# Buyer Chat
@login_required(login_url='user_login')
@has_selleraccount
def buyer_chat_messages(request):
    chatroom = ChatRoom.objects.filter(buyer=request.user)
    print(chatroom)
    args = {
        'chatroom': chatroom
    }
    return render(request, "buyingview/buyer_chat.html", args)



# Seller Dashboard


@login_required(login_url='user_login')
@has_selleraccount
def seller_dashboard(request):
    msgs = Message.objects.filter(receiver=request.user)
    
    users = User.objects.all()
    active_orders, completed_orders, cancelled_orders = [], [], []
    count_active = Checkout.objects.filter(order_status="ACTIVE").filter(user=request.user).count()
    orders = Checkout.objects.filter(seller=request.user).filter(paid=True).order_by("-id")
    categories = Category.objects.all()
    # Reviews
    # review = ReviewSeller.objects.filter(seller=request.user)
    review_count = ReviewSeller.objects.filter(seller=request.user).count()
    
    # chatrooms = ChatRoom.objects.all()
    chatrooms = ChatRoom.objects.filter(Q(buyer=request.user) | Q(sellers=request.user)).order_by("-id")[:10]

    for order in orders:
        if order.is_complete:
            completed_orders.append(order)
        elif order.order_status == "ACTIVE":
            active_orders.append(order)
        elif order.order_status == "CANCELLED" and order.is_cancel:
            cancelled_orders.append(order)

    args = {
        "msg_len": len(msgs),
        'users': users,
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "count_active": count_active,
        "chatrooms": chatrooms,
        "all_cats": categories,
        "review_count": review_count,
       
    }

    return render(request, 'sellingview/seller_dashboard.html', args)


# Settings Page
@login_required(login_url='user_login')
@has_selleraccount
def settings_page(request):
    return render(request, 'sellingview/settings.html')

# Security Page

def examView(request):
    return render(request, "azimpart/exam.html")
    
def preExamSubmission(request):
    return render(request, "azimpart/pre_exam_submit.html")


@login_required(login_url='user_login')
@has_selleraccount
def security_page(request):
    return render(request, 'sellingview/security.html')

# Notification Page


@login_required(login_url='user_login')
@has_selleraccount
def notifications_page(request):
    return render(request, 'sellingview/notifications.html')

# Support Page


@login_required(login_url='user_login')
@has_selleraccount
def support_page(request):
    return render(request, 'azimpart/help-support.html')

# Azim Contact Page


@login_required(login_url='user_login')
@has_selleraccount
def azim_contact_page(request):
    return render(request, 'sellingview/contacts.html')


# seller Dashboard End
@login_required(login_url='user_login')
@has_selleraccount
def add_to_cart(request):
    cart = request.session.get('cart')
    remove = request.POST.get('remove')
    package_id = request.POST.get('package_id')

    if request.method == "POST":
        if cart:
            quantity = cart.get(package_id)
            if quantity:
                cart[package_id] = quantity + 1
            else:
                cart[package_id] = 1
        else:
            cart = {}
            cart[package_id] = 1
        request.session['cart'] = cart

        return redirect('cartView')


def map_function(request, package_id):
    cart = request.session.get('cart', None)
    package_id = str(package_id.id)

    if package_id in cart:
        return package_id.price * cart[package_id]


def get_cart_products(request):
    ids = list(request.session.get('cart').keys())
    cart_products = OfferManager.get_offer(ids)
    package_prices = list(map(map_function, cart_products))
    print(package_prices)
    total = sum(package_prices)

    args = {'cart_products': cart_products, 'total': total}
    return render(request, 'buyingview/cart.html', args)


@login_required(login_url='user_login')

def cartView(request):
    cart = request.session.get('cart', None)

    if request.method == "POST":
        cart = {}
        del request.session["cart"]
        return redirect("buying_view")

    # print(request.session.get("cart"))
    if not cart:
        request.session['cart'] = {}
    ids = list(request.session.get('cart').keys())
    cart_products = OfferManager.get_offer(ids)
    if cart is not None:
        if len(cart) > 1:
            cart_first_item = str(list(cart.keys())[0])
            cart_first_item_val = list(cart.values())[0]
            request.session['cart'] = {}
            request.session["cart"] = {cart_first_item: cart_first_item_val}
            ids = list(request.session.get('cart').keys())
            cart_products = OfferManager.get_offer(ids)
    # print(request.session.get("cart"))
    context = {
        'cart_products': cart_products,
    }

    return render(request, 'buyingview/cart.html', context)


def create_checkout_random_slug(str_len):
    rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))
    checkout = Checkout.objects.filter(slug=rand_slug)
    if checkout.exists():
        create_offer_random_slug(str_len)
    return rand_slug

@login_required(login_url='user_login')

def checkout(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    ids = list(request.session.get('cart').keys())
    cart_products = OfferManager.get_offer(ids)
    user = request.user
    print("EMAIL: " + user.email)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        due_date = request.POST.get('due_date')
        user = request.user
        # seller work

        packages = OfferManager.get_offer(list(cart.keys()))

        for package in packages:
            slug = create_checkout_random_slug(20)
            checkout = Checkout(
                slug=slug,
                first_name=first_name,
                last_name=last_name,
                address=address,
                due_date=due_date,
                user=user,
                package=package,
                price=package.price,
                quantity=cart.get(str(package.id)),
                seller = package.offer.user
            )
            
            # checkout.order_status = ""
            
            checkout.save()
   
            send_mail(
                'Subject here',
                'USERNAME: ' + checkout.user.username + '\n'\
                'Thank you for ordering from Marketage. ' + '\n'\
                'Your order' + 'is now active. ' + '\n' \
                'You can review your order status at any time by visiting Your Account https://marketage.io/test. \n'\

                'Your Order Id: ' + 'Marketage#' + str(checkout.id) + '\n' +
                 'Package Name: ' + str(checkout.package) + '\n' \
                 'Price: ' + str(checkout.price) + '\n' \
                 'Quantity: ' + str(checkout.quantity) + '\n' \
                 'Grand Total: ' + str(checkout.grand_total) + '\n'\
                 '\n'\
                 'We hope you enjoyed your shopping experience with us and that you will visit us again soon.' \
                 '\n'\
                 '\n'\
                 'Copyright © 2021 Itna Global Ltd. All rights reserved.'\
                 'IGL located at 2 Frederick Street, Kings Cross, London, United Kingdom, WC1X 0ND'\
                 '\n'
                 'Bangladesh Office Itna Global Limited, House 24, Road,1, Nikunja2, Dhaka 1229, Khilkhet, Phone  +8809613662222 Email itnaglobal@gmail.com',
                 
                
                'noreply@marketagemail.io',
                [checkout.user.email],
                # ['itna.sakib@gmail.com'],
                fail_silently=False,
            )
            request.session['cart'] = {}
            return redirect('BuyerOrders')

    args = {
        'cart_products': cart_products
    }
    return render(request, 'buyingview/checkout.html', args)


# buyer order page views
@login_required(login_url='user_login')

def get_buyer_orders_url(request):
    order_id = []
    seller_submit = set()

    orders = Checkout.objects.filter(user=request.user).order_by('-id')
    # onoing_projects = Checkout.objects.filter()
    premium_orders = PremiumOfferPackageCheckout.objects.filter(user=request.user)
    for order in orders:
        order_id.append(order.id)

    for item in SellerSubmit.objects.all().order_by("-id"):
        # print(item.checkout.id)
        if item.checkout.id in order_id:
            try:
                x = SellerSubmit.objects.filter(checkout=item.checkout.id).last()
            except:
                return redirect("BuyerOrders")
            else:
                seller_submit.add(x)

    print(order_id)
    print(seller_submit)

    args = {
        'orders': orders,
        "seller_submit": seller_submit,
        "premium_orders": premium_orders,
    }
    return render(request, 'buyingview/buying_orders.html', args)



# category wise Page Buying View
@login_required(login_url='user_login')
@has_selleraccount
def category_wise_offers(request, slug):
    cats = Category.objects.all()
    category = Category.objects.all()
    catwise_offers = Offer.objects.filter(category__slug = slug)
    
    # Category Wise Subcategory
    subcategory = Subcategory.objects.filter(parent_market__slug = slug)
    print(subcategory)
    all_offers = Offer.objects.all()
    # sub_cats = Subcategory.objects.all()

    args = {
        'catwise_offers': catwise_offers,
        'category': category,
        "all_offers": all_offers,
        'cats': cats,
        'subcategory': subcategory,
        }

    return render(request, 'landingview/service_wise_offers.html', args)


@login_required(login_url='user_login')
@has_selleraccount
def subcategory_wise_offers(request, slug):
    cats = Category.objects.all().order_by("-id")[:7]
    subcategory = Subcategory.objects.all()
    subcat = get_object_or_404(Subcategory, slug=slug)

    sub_offers = Offer.objects.filter(sub_category__slug = slug)

    args = {
        "subcat": subcat,
        "subcategory": subcategory,
        "sub_offers": sub_offers,
        "cats": cats
    }
    return render(request, "landingview/subcategory_offer.html", args)

@login_required(login_url='user_login')
@has_selleraccount
def added_post_request(request):
    if request.method == 'POST':
        user = request.user
        postrequest_title = request.POST.get("title")
        description = request.POST.get("description")
        attachment  = request.FILES.get("file_upload", None)
        category = request.POST.get("category")
        del_time = request.POST.get("del_time")
        price = request.POST.get("price")
        post_status = "ACTIVE"

        print("delivery time", del_time)
        print(user, postrequest_title, description, attachment, category, del_time, price)
        
        try:
            category = Category.objects.get(title=category)
            delivery_time = DeliveryTime.objects.get(title=del_time)
        except:
            return redirect("post_a_request")
        else:
            BuyerPostRequest.objects.create(user=user, postrequest_title=postrequest_title,
                                            description=description, attachment=attachment,
                                            category=category, delivery_time=delivery_time,
                                            budget=price, post_status=post_status)

            return redirect("buyer-posts")
    else:
        return redirect("post_a_request")

@login_required(login_url='user_login')
@has_selleraccount
def post_a_request(request):
    categories = Category.objects.all()
    delivery_time = DeliveryTime.objects.all()

    args = {
        'categories': categories,
        'delivery_time': delivery_time,
    }
    return render(request, 'buyingview/post_request.html', args)


def get_become_a_seller_page(request):
    return render(request, 'landingview/become_a_seller.html')
    

# Order Details Page & SSLCOMMERZ
@login_required(login_url='user_login')
@has_selleraccount
def get_order_details_url(request, id, slug, *args, **kwargs):
    try:
        order = Checkout.objects.get(pk=id, slug=slug)
    # for sslcommerz
    except Checkout.DoesNotExist:
        return redirect("BuyerOrders")
    else:
        if request.method == "POST":
            settings = {
                'store_id': 'testbox', 'store_pass': 'qwerty', 'issandbox': True
            }
            user = request.user
            order = Checkout.objects.get(pk=id)
            print(order)
            first_name = order.first_name
            last_name = order.last_name
            address = order.address
            email = order.user.email
            phone_number = order.user.selleraccount.contact_no
            country = order.user.selleraccount.country
            city = order.user.selleraccount.city
            package_category = order.package.offer.category
            quantity = order.quantity
            total = order.grand_total
            transaction_id = order.id
    
            # Checkout.objects.filter(pk=kwargs['id'])
            Checkout.objects.filter(pk=id)
    
            sslcommerz = SSLCOMMERZ(settings)
            post_body = {}
            post_body['total_amount'] = total
            post_body['currency'] = "BDT"
            post_body['tran_id'] = transaction_id
            # post_body['tran_id'] = transaction_id
            post_body['success_url'] = "https://marketage.io/betaversion/success/"
            post_body['fail_url'] = "https://marketage.io/betaversion/failed/"
            post_body['cancel_url'] = "https://marketage.io/betaversion/cancel/"
            post_body['emi_option'] = 0
            post_body['cus_name'] = first_name
            post_body['cus_email'] = email
            post_body['cus_add1'] = address
            post_body['cus_phone'] = phone_number
            post_body['cus_city'] = city
            post_body['cus_country'] = country
            post_body['shipping_method'] = "NO"
            post_body['multi_card_name'] = ""
            post_body['num_of_item'] = quantity
            post_body['product_name'] = order.package
            post_body['product_category'] = package_category
            post_body['product_profile'] = "general"
            print(post_body)
            response = sslcommerz.createSession(post_body)
            print(response)
            return redirect(response['GatewayPageURL'])

    args = {
        'order': order
    }

    return render(request, 'buyingview/order_details.html', args)


@csrf_exempt
def successView(request):
    if request.POST.get('status') == "VALID":
        tran_id = request.POST['tran_id']
        # print("TRAIN ID:", tran_id)
        order = Checkout.objects.get(id=tran_id)
        # print("ORDER:", order)
        order.paid = True
        order.save()
        
    return render(request, "responseview/success.html")


@login_required(login_url='user_login')
@has_selleraccount
@csrf_exempt
def failedView(request):
    return render(request, "responseview/failed.html")


@login_required(login_url='user_login')
@has_selleraccount
@csrf_exempt
def cancelledView(request):
    return render(request, "responseview/cancel.html")

@login_required(login_url='user_login')
def extendedUserView(request):
    form = ExtendedUserForm()
    user_session = request.session.get("user", None)

    if user_session is not None:
        seller_account = SellerAccount.objects.filter(user=request.user)
        
        if seller_account.exists():
            return redirect("buying_view")
        if request.method == "POST":
            # email = request.POST.get("email")
            contact_no = request.POST.get("contact_no")
            profile_picture = request.FILES.get("profile_picture")
            country_id = request.POST.get("country")
            city_id = request.POST.get("city")
            # print(request.user, email, contact_no, profile_picture, country_id, city_id)
            try:
                country = Country.objects.get(id=country_id)
                city = City.objects.get(id=city_id)
            except:
                return redirect("extended-user")
            else:
                SellerAccount.objects.create(user=request.user,
                                             contact_no=contact_no, profile_picture=profile_picture,
                                             country=country, city=city)
                return redirect('buying_view')
    else:
        return redirect("user_registration")

    args = {
        'form': form,
    }
    return render(request, "wasekPart/extendedForm.html", args)


@login_required(login_url='user_login')
@has_selleraccount
def sellerSubmitView(request, pk):
    # print(pk)
    if request.method == "POST":
        file_field = request.FILES.get("file_field")
        try:
            checkout = Checkout.objects.get(id=pk)
            # print(f"{checkout}")
            # print(file_field)
        except:
            return redirect("manage-order")
        else:
            SellerSubmit.objects.create(
                checkout=checkout, file_field=file_field)

            checkout.order_status = "DELIVERED"
            checkout.save()
            return redirect("manage-order")

    args = {
        "checkout_id": pk,
    }
    return render(request, "wasekPart/sellerSubmit.html", args)



# Testing Purpose

def all_test_orders(request):
    orders = Checkout.objects.filter(is_complete=True)

    args = {
        "orders": orders
    }

    return render(request, "testpart/order_test.html", args)


# Review Sellers

def reviewSellerForm(request, username):
    seller = User.objects.get(username=username)

    if request.method == 'POST':
        pass

    args = {
        "seller": seller
    }
    return render(request, "testpart/test2.html", args)





# Rating Sellers


# Top Offers


## Footer Part ---------- >>>>>

def aboutusView(request):
    return render(request, "azimpart/aboutus.html")

def privacypolicyView(request):
    return render(request, "azimpart/privacy-policy.html")

@login_required(login_url='user_login')
@has_selleraccount
def helpSupportView(request):
    support_category = SupportCategoryModel.objects.all()
    # print("SUPPORTTTT" + str(support_category))
    # print("18231298312938172938127")

    if request.method=='POST':
        user = request.user
        email = request.POST.get('email')
        subject = request.POST.get('subject')    
        attachment = request.FILES.get('attachment')
        image_attachment = request.FILES.get('image_attachment')
        description = request.POST.get('description')

        subject = SupportCategoryModel.objects.get(title=subject)

        saved = SupportModel(
            user = user,
            email = email,
            subject = subject,
            attachment = attachment,
            image_attachment = image_attachment,
            description = description,
            support_ticket = uuid.uuid4().hex[:6].upper()
        )
        # print(saved)
        saved.support_status = "PENDING"
        saved.save()
        send_mail(
                'SUPPORT TICKET CREATED',
                'USERNAME: ' + saved.user.username + '\n'\
                'You Support ticket has been created successfully' + '\n' \
                    'You Ticket No.' + saved.support_ticket + '\n' \
                'For getting reply you will have to wait 24 hours at least'+'\n' \
                 'Copyright © 2021 Itna Global Ltd. All rights reserved.'\
                 'IGL located at 2 Frederick Street, Kings Cross, London, United Kingdom, WC1X 0ND'\
                 '\n'
                 'Bangladesh Office Itna Global Limited, House 24, Road,1, Nikunja2, Dhaka 1229, Khilkhet, Phone  +8809613662222 Email itnaglobal@gmail.com',
                 
                
                'noreply@marketagemail.com',
                [email],
                fail_silently=False,
            )
        return redirect('buying_view')
    args = {
        'support_category': support_category
    }
    return render(request, "azimpart/help-support.html", args)


def trustSafetyView(request):
    return render(request, "azimpart/trust-safety.html")

def termOfservicesView(request):
    return render(request, "azimpart/term-services.html")


## Footer Aprt ENd ------->>>


def create_offer_random_slug(str_len):
    rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))
    offer = Offer.objects.filter(slug=rand_slug)
    if offer.exists():
        create_offer_random_slug(str_len)
    return rand_slug


def create_offer_random_slug(str_len):
    rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))
    offer = Offer.objects.filter(slug=rand_slug)
    if offer.exists():
        create_offer_random_slug(str_len)
    return rand_slug


@login_required(login_url='user_login')
@has_selleraccount
def createOfferView(request):
    offer = Offer.objects.filter(user=request.user)
    
    if (len(offer) > 7):
        return redirect("manage-offers")
        
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    child_cats = ChildSubcategory.objects.all()
    services = Services.objects.all()
    deliveries = DeliveryTime.objects.all()
    revisions = Revision.objects.all()
    num_of_pages = NumberOfPage.objects.all()

    if request.method == "POST":
        # Creating random slug
        slug = create_offer_random_slug(20)

        offer_title = request.POST.get("offer_title")
        seo_title = request.POST.get("seo_title")
        category = request.POST.get("category")
        service = request.POST.get("service")
        basic_shortDesc = request.POST.get("basic_shortDesc")
        standard_shortDesc = request.POST.get("standard_shortDesc")
        premium_shortDesc = request.POST.get("premium_shortDesc")
        delivery_time_basic = request.POST.get("delivery_time_basic")
        delivery_time_standard = request.POST.get("delivery_time_standard")
        delivery_time_premium = request.POST.get("delivery_time_premium")
        num_pages_basic = request.POST.get("num_pages_basic")
        num_pages_standard = request.POST.get("num_pages_standard")
        num_pages_premium = request.POST.get("num_pages_premium")
        is_responsive_basic = request.POST.get("is_responsive_basic")
        is_responsive_standard = request.POST.get("is_responsive_standard")
        is_responsive_premium = request.POST.get("is_responsive_premium")
        revision_basic = request.POST.get("revision_basic")
        revision_standard = request.POST.get("revision_standard")
        revision_premium = request.POST.get("revision_premium")
        price_basic = request.POST.get("price_basic")
        price_standard = request.POST.get("price_standard")
        price_premium = request.POST.get("price_premium")
        content = request.POST.get("content")
        main_image = request.FILES.get("offer_main_image")
        uploaded_photo = request.FILES.getlist("uploaded_photo")
        uploaded_video = request.FILES.get("uploaded_video")
        document = request.FILES.get("document")
        child_cat = request.POST.get("child_cat")
        subcategory = request.POST.get("subcategory")
        
        try:
            category = Category.objects.get(title=category)
            subcategory = Subcategory.objects.get(sub_title=subcategory)
            child_cat = ChildSubcategory.objects.get(child_title=child_cat)
            service = Services.objects.get(title=service)
        except:
            return redirect("create-offer")
        else:
        # Creating offer object

        # if main_image and uploaded_video and document:
        #     offer = Offer(slug=slug, user=request.user, offer_title=offer_title, seo_title=seo_title, 
        #                 image=main_image, offer_video=uploaded_video, document=document, 
        #                 service=service, category=category, description=content)
        #     offer.save()
            if main_image:
                offer = Offer(slug=slug, user=request.user, offer_title=offer_title, seo_title=seo_title, image=main_image,
                    service=service, child_subcategory=child_cat, category=category, sub_category=subcategory, description=content)
                if uploaded_video:
                    offer.offer_video = uploaded_video
                if document:
                    offer.document = document
                    
                offer.save()
            
            if len(uploaded_photo) > 0:
                for item in uploaded_photo[:3]:
                    image_obj = ExtraImage(image=item)
                    image_obj.save()
                    offer.extra_images.add(image_obj.id)
    
            if basic_shortDesc is not None:
                try:
                    dt_basic = DeliveryTime.objects.get(title=delivery_time_basic)
                    re_basic = Revision.objects.get(title=revision_basic)
                    num_page_basic = NumberOfPage.objects.get(title=num_pages_basic)
                except:
                    offer.delete()
                    return redirect("create-offer")
                # print(num_page_basic)
                else:
                    if is_responsive_basic == "on":
                        is_responsive_basic = True
                    else:
                        is_responsive_basic = False
    
    
                    # Saving Package
                    package = Package(title="Basic", delivery_time=dt_basic, package_desc=basic_shortDesc, 
                                    revision_basic=re_basic, num_of_pages_for_basic=num_page_basic, is_responsive_basic=is_responsive_basic,
                                    )
                    package.save()
                    OfferManager.objects.create(offer=offer, package=package, price=price_basic)
    
            if standard_shortDesc is not None:
                try:
                    dt_standard = DeliveryTime.objects.get(title=delivery_time_standard)
                    re_standard = Revision.objects.get(title=revision_standard)
                    num_page_standard = NumberOfPage.objects.get(title=num_pages_standard)
                # print(num_page_standard)
                except:
                    offer.delete()
                    return redirect("create-offer")
                else:
                    if is_responsive_standard == "on":
                        is_responsive_standard = True
                    else:
                        is_responsive_standard = False
    
                    package = Package(title="Standard", delivery_time=dt_standard, package_desc=standard_shortDesc, 
                                    revision_standard=re_standard, num_of_pages_for_standard=num_page_standard, is_responsive_standard=is_responsive_standard,
                                    )
                    package.save()
                    OfferManager.objects.create(offer=offer, package=package, price=price_standard)
    
            if premium_shortDesc is not None:
                try:
                    dt_premium = DeliveryTime.objects.get(title=delivery_time_premium)
                    re_premium = Revision.objects.get(title=revision_premium)
                    num_page_premium = NumberOfPage.objects.get(title=num_pages_premium)
                # print(num_page_premium)
                except:
                    offer.delete()
                    return redirect("create-offer")
                else:
                    if is_responsive_premium == "on":
                        is_responsive_premium = True
                    else:
                        is_responsive_premium = False
    
                    # Creating package object
                    package = Package(title="Premium", delivery_time=dt_premium, package_desc=premium_shortDesc, 
                                    revision_premium=re_premium, num_of_pages_for_premium=num_page_premium, is_responsive_premium=is_responsive_premium,
                                    )
                    package.save()
                    # Creating offer manager object
                    OfferManager.objects.create(offer=offer, package=package, price=price_premium)
    
            return redirect("manage-offers")
    args = {
        "categories": categories,
        "subcategories": subcategories,
        "child_cats": child_cats,
        "services": services,
        "deliveries": deliveries,
        "revisions": revisions,
        "num_of_pages": num_of_pages,
    }
    return render(request, "sellingview/create_offer.html", args)

@login_required(login_url='user_login')
@has_selleraccount
def edit_offer(request, id):
    basic_package, standard_package, premium_package = None, None, None
    basic_deliveries, standard_deliveries, premium_deliveries = None, None, None
    basic_num_pages, standard_num_pages, premium_num_pages = None, None, None
    basic_revisions, standard_revisions, premium_revisions = None, None, None
    basic_price, standard_price, premium_price = None, None, None
    document = None, 
    offer_first_img, offer_second_img, offer_third_img = None, None, None

    try:
        offer = Offer.objects.get(id=id)
    except Offer.DoesNotExist:
        return redirect("manage-offers")
    else:
        categories = Category.objects.exclude(title=offer.category.title)
        subcategories = Subcategory.objects.exclude(sub_title=offer.sub_category.sub_title)
        child_cats = ChildSubcategory.objects.exclude(child_title=offer.child_subcategory.child_title)
        services = Services.objects.exclude(title=offer.service.title)
        offermanager = OfferManager.objects.filter(offer=offer)
        document = str(offer.document).split("/")[-1]
        if len(offer.extra_images.all()) > 0:
            for i, item in enumerate(offer.extra_images.all()):
                if i == 0:
                    offer_first_img = item
                elif i == 1:
                    offer_second_img = item
                elif i == 2:
                    offer_third_img = item

        # print(document)

        if offermanager.exists():
            for i, item, in enumerate(offermanager):
                # Basic package
                if i == 0:
                    basic_package = item.package
                    basic_deliveries = DeliveryTime.objects.exclude(title=basic_package.delivery_time.title)
                    basic_num_pages = NumberOfPage.objects.exclude(title=basic_package.num_of_pages_for_basic.title)
                    basic_revisions = Revision.objects.exclude(title=basic_package.revision_basic.title)
                    basic_price = item.price
                # Standard package
                elif i == 1:
                    standard_package = item.package
                    standard_deliveries = DeliveryTime.objects.exclude(title=standard_package.delivery_time.title)
                    standard_num_pages = NumberOfPage.objects.exclude(title=standard_package.num_of_pages_for_standard.title)
                    standard_revisions = Revision.objects.exclude(title=standard_package.revision_standard.title)
                    standard_price = item.price
                # Premium package
                elif i == 2:
                    premium_package = item.package
                    premium_deliveries = DeliveryTime.objects.exclude(title=premium_package.delivery_time.title)
                    premium_num_pages = NumberOfPage.objects.exclude(title=premium_package.num_of_pages_for_premium.title)
                    premium_revisions = Revision.objects.exclude(title=premium_package.revision_premium.title)
                    premium_price = item.price
    
        # print(basic_package, standard_package, premium_package)

        if request.method == "POST":
            main_image_id = request.POST.get("main_image_id", None)
            extra_image_id1 = request.POST.get("extra_image_id1", None)
            extra_image_id2 = request.POST.get("extra_image_id2", None)
            extra_image_id3 = request.POST.get("extra_image_id3", None)
            offer_video_id = request.POST.get("offer_video_id", None)
            offer_document_id = request.POST.get("offer_document_id", None)
            offer_title = request.POST.get("offer_title")
            seo_title = request.POST.get("seo_title")
            category = request.POST.get("category")
            subcategory = request.POST.get("subcatgory")
            child_subcat = request.POST.get("child_subcat")
            service = request.POST.get("service")
            basic_shortDesc = request.POST.get("basic_shortDesc")
            standard_shortDesc = request.POST.get("standard_shortDesc")
            premium_shortDesc = request.POST.get("premium_shortDesc")
            delivery_time_basic = request.POST.get("delivery_time_basic")
            delivery_time_standard = request.POST.get("delivery_time_standard")
            delivery_time_premium = request.POST.get("delivery_time_premium")
            num_page_basic = request.POST.get("num_pages_basic")
            num_page_standard = request.POST.get("num_pages_standard")
            num_page_premium = request.POST.get("num_pages_premium")
            basic_responsive = request.POST.get("is_responsive_basic")
            standard_responsive = request.POST.get("is_responsive_standard")
            premium_responsive = request.POST.get("is_responsive_premium")
            revision_basic = request.POST.get("revision_basic")
            revision_standard = request.POST.get("revision_standard")
            revision_premium = request.POST.get("revision_premimum")
            price_basic = request.POST.get("price_basic")
            price_standard = request.POST.get("price_standard")
            price_premium = request.POST.get("price_premium")
            content = request.POST.get("content")
            offer_mainImage = request.FILES.get("offer_main_image")
            offer_extraImages = request.FILES.getlist("offer_extraImages")
            offer_video = request.FILES.get("offer_video")
            offer_document = request.FILES.get("offer_document")

            # print("OFFER EXTRA IMAGES:")
            # print(offer_extraImages)

            # Deleting offer main image
            if main_image_id:
                offer.image = None
                offer.offer_status = "PAUSED"

            # Deleting an extra image from offer
            if extra_image_id1:
                offer.extra_images.remove(int(offer_first_img.id))
                # offer.offer_status = "PAUSED"
            elif extra_image_id2:
                offer.extra_images.remove(int(offer_second_img.id))
                # offer.offer_status = "PAUSED"
            elif extra_image_id3:
                offer.extra_images.remove(int(offer_third_img.id))
                # offer.offer_status = "PAUSED"

            # Deleting offer video
            if offer_video_id:
                offer.offer_video = None
                # offer.offer_status = "PAUSED"

            # Deleting offer document
            if offer_document_id:
                offer.document = None
                # offer.offer_status = "PAUSED"
            
            try:
                service = Services.objects.get(title=service)
                category = Category.objects.get(title=category)
                subcategory = Subcategory.objects.get(sub_title=subcategory)
                child_subcat = ChildSubcategory.objects.get(child_title=child_subcat)
            except:
                return redirect(f"/betaversion/edit_offer/{offer.id}/")
            else:
                offer.offer_title = offer_title
                offer.seo_title = seo_title
    
                if offer_mainImage:
                    offer.image = offer_mainImage
                if offer_video:
                    offer.offer_video = offer_video
                if offer_document:
                    offer.document = offer_document
    
                print("OFFER EXTRA IMAGE LENGTH:", len(offer.extra_images.all()))
    
                # if offer.image != None and offer.offer_video != None and offer.document != None and len(offer.extra_images.all()) > 0:
                #     offer.offer_status = "ACTIVE"
                    
                if offer.image != None:
                    offer.offer_status = "ACTIVE"
    
                offer.service = service
                offer.category = category
                offer.sub_category = subcategory
                offer.child_subcategory = child_subcat
                offer.description = content
    
                offer.save()
                
                if main_image_id or extra_image_id1 or extra_image_id2 or extra_image_id3 or offer_video_id or offer_document_id:
                    return redirect(f"/betaversion/edit_offer/{offer.id}/")
                
                # Adding offer extra images
                if offer_extraImages:
                    for item in offer_extraImages[:3-len(offer.extra_images.all())]:
                        image_obj = ExtraImage(image=item)
                        image_obj.save()
                        offer.extra_images.add(image_obj.id)
                
                for i, item, in enumerate(offermanager):
                    # Basic package
                    if i == 0:
                        item.package.package_desc = basic_shortDesc
                        revision_basic = Revision.objects.get(title=revision_basic)
                        delivery_time_basic = DeliveryTime.objects.get(title=delivery_time_basic)
                        item.package.revision_basic = revision_basic
                        item.package.delivery_time = delivery_time_basic
                        num_page_basic = NumberOfPage.objects.get(title=num_page_basic)
                        item.package.num_of_pages_for_basic = num_page_basic
                        
                        if basic_responsive == "on":
                            is_basic_responsive = True
                        else:
                            is_basic_responsive = False
    
                        item.package.is_responsive_basic = is_basic_responsive
                        item.price = price_basic
                        item.package.save()
                        item.save()
                    # Standard package
                    elif i == 1:
                        item.package.package_desc = standard_shortDesc
                        revision_standard = Revision.objects.get(title=revision_standard)
                        delivery_time_standard = DeliveryTime.objects.get(title=delivery_time_standard)
                        item.package.revision_standard = revision_standard
                        item.package.delivery_time = delivery_time_standard
                        num_page_standard = NumberOfPage.objects.get(title=num_page_standard)
                        item.package.num_of_pages_for_standard = num_page_standard
                        
                        if standard_responsive == "on":
                            is_standard_responsive = True
                        else:
                            is_standard_responsive = False
    
                        item.package.is_responsive_standard = is_standard_responsive
                        item.price = price_standard
                        item.package.save()
                        item.save()
                    # Premium package
                    elif i == 2:
                        item.package.package_desc = premium_shortDesc
                        revision_premium = Revision.objects.get(title=revision_premium)
                        delivery_time_premium = DeliveryTime.objects.get(title=delivery_time_premium)
                        item.package.revision_premium = revision_premium
                        item.package.delivery_time = delivery_time_premium
                        num_page_premium = NumberOfPage.objects.get(title=num_page_premium)
                        item.package.num_of_pages_for_premium = num_page_premium
                        
                        if premium_responsive == "on":
                            is_premium_responsive = True
                        else:
                            is_premium_responsive = False
    
                        item.package.is_responsive_premium = is_premium_responsive
                        item.price = price_premium
                        item.package.save()
                        item.save()
    
                # return redirect(f"/betaversion/edit_offer/{offer.id}/")
                return redirect("manage-offers")

    args = {
        "offer": offer,
        "categories": categories,
        "subcategories": subcategories,
        "child_cats": child_cats,
        "services": services,
        "basic_package": basic_package,
        "standard_package": standard_package,
        "premium_package": premium_package,
        "basic_deliveries": basic_deliveries,
        "standard_deliveries": standard_deliveries,
        "premium_deliveries": premium_deliveries,
        "basic_num_pages": basic_num_pages,
        "standard_num_pages": standard_num_pages,
        "premium_num_pages": premium_num_pages,
        "basic_revisions": basic_revisions,
        "standard_revisions": standard_revisions,
        "premium_revisions": premium_revisions,
        "basic_price": basic_price,
        "standard_price": standard_price,
        "premium_price": premium_price,
        "document": document,
        "offer_first_img": offer_first_img,
        "offer_second_img": offer_second_img,
        "offer_third_img": offer_third_img,
    }
    return render(request, 'azimpart/edit_offer.html', args)


@login_required(login_url='user_login')
@has_selleraccount
def seller_order_details(request, id):
    order = Checkout.objects.get(pk=id)
    today_date = date.today()
    duration = str(order.due_date - today_date).split(",")[0]

    print(duration)
    print(type(duration))
    
    args = {
        'order': order,
        "duration": duration,
    }
    return render(request, 'sellingview/seller_order_details.html', args)



 ###################### 1 ALGO HERE #############################################
def buyerOfferFormView(request, pk):
    seller_submit = None
    try:
        order = Checkout.objects.get(id=pk)
        seller_submit = SellerSubmit.objects.filter(checkout=order)
        if seller_submit.exists():
            seller_submit = seller_submit.last()
    except:
        messages.error(request, "Error while submitting!")
    else:
        if request.method == "POST":
            order_status = request.POST.get("order_status")

            l = Checkout.objects.filter(is_complete=True).filter(
                 seller=request.user).count()
            print(l)
            cancel_amount = Checkout.objects.filter(is_cancel=True).filter(
                seller=request.user
            ).count()

            calc = order.total * 20 / 100
            amount = order.total - calc
            print("MY AMOUNT" + str(amount))
            
            # print("AAAAAAAAAAAAAAA" + str(amount))
            # Wallet add system web hooks
            seller_wallet = order.seller.selleraccount.wallet
            # print(str(seller_wallet))
            if order_status == "complete" and l < 15:
                order.order_status = "COMPLETED"
                order.is_complete = True
                order.is_cancel = False
                order.on_review = False
                order.seller.selleraccount.wallet += amount
                order.seller.selleraccount.save()
                # print("User Balance Now: " + str(order.seller.selleraccount.wallet))
                # print("BALANCEEEEEEEEEEE" + str(order.seller.selleraccount.wallet))
                order.save()
                return redirect("BuyerOrders")

            elif order_status == "complete" and l > 15:
                order.order_status = "COMPLETED"
                order.is_complete = True
                order.is_cancel = False
                order.on_review = False
                order.seller.selleraccount.level = 1
                order.seller.selleraccount.is_new = False
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "complete" and l > 25:
                order.order_status = "COMPLETED"
                order.is_complete = True
                order.is_cancel = False
                order.on_review = False
                order.seller.selleraccount.level += 1
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "complete" and l > 35:
                order.order_status = "COMPLETED"
                order.order_status = True
                order.is_cancel = False
                order.on_review = False
                order.seller.selleraccount.level += 1
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "complete" and l > 50:
                order.order_status = "COMPLETED"
                order.order_status = True
                order.is_cancel = False
                order.on_review = False
                order.seller.selleraccount.level += 1
                order.seller.selleraccount.is_professional = True
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")

            # Leveling Down ALgorithm
            
            elif order_status == "cancel" and cancel_amount < 5:
                order.order_status = "CANCELLED"
                order.is_cancel = True
                order.is_complete = False
                order.is_review = False
                order.seller.selleraccount.level -= 1
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "cancel" and cancel_amount > 5:
                order.order_status = "CANCELLED"
                order.is_cancel = True
                order.is_complete = False
                order.is_review = False
                order.seller.selleraccount.level -= 1
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "cancel" and cancel_amount > 8:
                order.order_status == "CANCELLED"
                order.is_cancel = True
                order.is_complete = False
                order.is_review = False
                order.seller.selleraccount.level -= 1
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "cancel" and cancel_amount > 15:
                order.order_status == "CANCELLED"
                order.is_cancel = True
                order.is_complete = False
                order.is_review = False
                order.seller.selleraccount.level -= 1
                order.seller.selleraccount.save()
                order.save()
                return redirect("BuyerOrders")
            
            elif order_status == "review":
                order.order_status = "ON REVIEW"
                order.on_review = True
                order.is_complete = False
                order.is_cancel = False
                order.save()
                return redirect("BuyerOrders")
            else:
                messages.error(request, "Error while submitting!")
    # seller_submit = SellerSubmit.objects.get(checkout=order)
    args = {
        "seller_submit": seller_submit,
        "order": order
    }
    return render(request, "wasekPart/buyer_gigForm.html", args)
################################################## ALGO PART ENDS HERE ###############################################################





@login_required(login_url='user_login')
@has_selleraccount
def buyerDashboardFormView(request):
    orders = Checkout.objects.filter(
        user=request.user, order_status="DELIVERED", is_complete=False).order_by("-id")

    args = {
        "orders": orders,
    }

    return render(request, "wasekPart/buyer_dashboard.html", args)

# Download Function
@login_required(login_url='user_login')
@has_selleraccount
def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, "rb") as fh:
            response = HttpResponse(
                fh.read(), content_type="application/file_field")
            response["Content-Disposition"] = "inline;filename=" + \
                os.path.basename(file_path)
            return response
    raise Http404

def searchPageView(request):
    # query = request.GET.get("search")

    # results = Services.objects.filter(title__icontains = query)


    # args = {
    #     "results": results
    # }
    return render(request, "buyingview/search-box-Result.html")


@login_required(login_url='user_login')
@has_selleraccount
def buyer_requestView(request):
    submitted_offer, active_posts = [], None

    if request.user:
        active_post_requests = BuyerPostRequest.objects.filter(post_status="ACTIVE").order_by("-id").exclude(user=request.user)
        send_offer_requests = SendOfferModel.objects.filter(seller=request.user).order_by("-id")

        for x in active_post_requests:
            for y in send_offer_requests:
                print(x.postrequest_title, y.buyer_post_request)
                if str(x.postrequest_title) == str(y.buyer_post_request):
                    submitted_offer.append(x.postrequest_title)
        
        print("SUBMITTED OFFER:", submitted_offer)
        if len(submitted_offer) > 0:
            for item in submitted_offer:
                active_post_requests = active_post_requests.exclude(postrequest_title=item)
    else:
        return redirect("user_login")

    args = {
        "active_post_requests": active_post_requests,
        "send_offer_requests": send_offer_requests,
    }
    return render(request, "azimpart/buyer_request.html", args)


def my_contacts_page(request):
    return render(request, "azimpart/my_contacts.html")



# User Details
@login_required(login_url='user_login')
@has_selleraccount
def account_detailsView(request, user_id):
    offers = Offer.objects.filter(user=request.user)
    user_details = User.objects.get(pk=user_id)
    
    if request.method == "POST":
        profile_pic = request.FILES.get("profile_image")
        seller_account = get_object_or_404(SellerAccount, user=request.user)
        if profile_pic:
            seller_account.profile_picture = profile_pic
            seller_account.save()
    
    args = {
        'user_details': user_details,
        'offers': offers
    }

    return render(request, 'sellingview/account.html', args)





@login_required(login_url='user_login')
@has_selleraccount
def earnings(request, id):
    user = request.user
    if user is not None:
        seller_details = User.objects.get(pk=id)

        orders_by_seller = Checkout.objects.filter(
            Q(seller = request.user) & Q(is_complete=True)
        ).order_by('-created_at')
        
        withdraw_methods = WithDrawPaymentMethod.objects.all()

        balance = seller_details.selleraccount.wallet
        if balance > 0 and request.method == 'POST':
            amount = request.POST.get('amount')
            method = request.POST.get('method')
            user = seller_details

            withdraw = WithDrawModel(
                amount=amount,
                user=user,
                method=WithDrawPaymentMethod.objects.get(method_name=method),
                on_review=True,
                stat="ON REVIEW"
            )

            withdraw.save()
            print(withdraw)
            return redirect(f"/earnings/{seller_details.id}")

    # user = seller_details

    args = {
        'seller_details': seller_details,
        'orders_by_seller': orders_by_seller,
        'withdraw_methods': withdraw_methods,
    }
    return render(request, 'azimpart/earnings.html', args)



def createSellerSendOfferRandomSlug(str_len):
    rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))
    send_offer = SendOfferModel.objects.filter(send_offer_slug=rand_slug)
    if send_offer.exists():
        createSellerSendOfferRandomSlug(str_len)
    return rand_slug
    
@login_required(login_url='user_login')
@has_selleraccount
def sellerSendOfferView(request, id):
    delivery_time = DeliveryTime.objects.all()

    try:
        post_request = BuyerPostRequest.objects.get(id=id)
    except BuyerPostRequest.DoesNotExist:
        return redirect("BuyeRequestView")
    else:
        if request.method == "POST":
            send_offer_slug = createSellerSendOfferRandomSlug(20)
            buyer_post_request = post_request
            buyer = post_request.user
            seller = request.user
            description = request.POST.get("description")
            offer_price = request.POST.get("offer_price")
            del_time = request.POST.get("delivery_time")

            del_time = DeliveryTime.objects.get(title=del_time)

            if description:
                SendOfferModel.objects.create(send_offer_slug=send_offer_slug, buyer_post_request=buyer_post_request,
                                            buyer=buyer, seller=seller, offer_letter=description,
                                            offered_price=offer_price, delivery_time=del_time)
            else:
                messages.error(request, "Please submit all the field!")
                return redirect(f"/send-offer/{id}/")
            return redirect("BuyeRequestView")

    args = {
        "delivery_time": delivery_time,
    }
    return render(request, "azimpart/seller_send_offer.html", args)


@login_required(login_url='user_login')
@has_selleraccount
def buyerAllPostsView(request):
    buyer_requested_posts = BuyerPostRequest.objects.filter(user=request.user).order_by("-id")
    send_offers = SendOfferModel.objects.filter(buyer=request.user).order_by("-id")

    args = {
        "buyer_requested_posts": buyer_requested_posts,
        "send_offers": send_offers,
    }
    return render(request, "azimpart/buyer_send_posts.html", args)


@login_required(login_url='user_login')
@has_selleraccount
def deleteBuyerPost(request, id):
    # print(id)
    try:
        requested_post = BuyerPostRequest.objects.get(id=id)
    except BuyerPostRequest.DoesNotExist:
        return redirect("buyer-posts")
    else:
        requested_post.delete()
        return redirect("buyer-posts")


@login_required(login_url='user_login')
@has_selleraccount
def reservedBuyerPost(request, id):
    if request.method == 'POST':
        try:
            buyer_post = BuyerPostRequest.objects.get(id=id)
        except BuyerPostRequest.DoesNotExist:
            return redirect("buyer-posts")
        else:
            buyer_post.post_status = "RESERVED"
            buyer_post.save()
            return redirect("buyer-posts")

@login_required(login_url='user_login')
@has_selleraccount
def activeBuyerPost(request, id):
    if request.method == 'POST':
        try:
            buyer_post = BuyerPostRequest.objects.get(id=id)
        except BuyerPostRequest.DoesNotExist:
            return redirect("buyer-posts")
        else:
            buyer_post.post_status = "ACTIVE"
            buyer_post.save()
            return redirect("buyer-posts")

def refundRequestView(request):
    return render(request, "buyingview/refund-req.html")


############# EXAM ALGO STARTS #################

@has_selleraccount
def select_subject_form(request):
    exam_subj = ExamSubject.objects.all()
    
    args = {
        "exam_subj": exam_subj
    }
    return render(request, 'accountview/select_subject.html', args)

# Subject Wise Exam Room

def exam_room(request, subject_id):
    # sub = SellerSubjectChoice.objects.get(pk=subject_id)
    # subs = SellerSubjectChoice.objects.all()
    # seller submitted subject wise qustion
    qustion = QustionModel.objects.random_qustion()

    if request.method == "POST":
        user = request.user,
        attachement = request.FILES.get('attachement')

        exm = ExamModel(
            user=user,
            qustion=qustion,
            attachement=attachement,
            status="PENDING"
        )
        exm.save()
        return redirect("/")

    args = {
        'qustion': qustion,
    }
    return render(request, "azimpart/exam.html", args)




############# EXAM ALGO ENDS #################


# Test #

def read_txt(request):
    pass


# END TEST PART #


# Rafsun Testing Part

def rafsun_header(request):
    return render(request, "rafsunpart/test_header.html")


# azim password reset page
def password_reset_confirm(request):
    return render(request, "accountview/password_reset_confirm.html")
    
    
    
    
# Paypal Success view Here, after successfull payment Checkout paid will update to True


# Paypal Succes URL View Here order will be updated to UNPAID to PAID
def paypal_success(request, id):
    body = json.loads(request.body)
    print("BODY", body)
    order = Checkout.objects.get(pk=id)
    order.paid = True
    order.save()

    args = {
        "order": order
    }

    return JsonResponse("", safe=False)
    
    
def payemntTermsView(request):
    return render(request, "azimpart/payment_terms.html")
    
    

# Review Seller Function
# So it will be (100 * 5 + 70 * 4 + 50 * 3 + 30 * 2 + 20 * 1) / 100 + 70 + 50 + 30 + 20
@login_required(login_url='user_login')
def review_offer(request, checkout_id):
    ratings = Rating.objects.all()
    review = Checkout.objects.get(pk=checkout_id)
    if request.method == "POST":
        client = request.user
        seller = review.seller
        text = request.POST.get('text')
        rate = request.POST.get('rate')
        
        rv = ReviewSeller(
            order=review,
            client=client,
            seller=seller,
            rate_seller=Rating.objects.get(title=rate),
            text=text,
        )
        review.rated = True
        review.save()
        rv.save()
        
        return HttpResponse("Success")
    
    args = {
        'review': review,
        'ratings': ratings
    }
    return render(request, 'sellingview/review.html', args)
    

############## PREMIUM OFFER PACKAGE VIEW ####################
@has_selleraccount
def premium_offer_package_view(request):
    p_packages = PremiumOfferPackage.objects.all()
    p_pkgs = None
    if len(p_packages) > 0:
        p_pkgs = PremiumOfferPackage.objects.filter(pkg_title="BRONZE")
        p_pkgs2 = PremiumOfferPackage.objects.filter(pkg_title="SILVER")
        p_pkgs3 = PremiumOfferPackage.objects.filter(pkg_title="GOLD")
    args = {
        "p_pkgs": p_pkgs,
        "p_pkgs2": p_pkgs2,
        "p_pkgs3": p_pkgs3,
    }
    return render(request, "azimpart/premium_package.html", args)

@has_selleraccount
def add_package_to_cart(request):
    premium_cart = request.session.get('premium_cart')
    pkg_id = request.POST.get('pkg_id')

    if request.method == 'POST':
        if premium_cart:
            quantity = premium_cart.get(pkg_id)
            if quantity:
                premium_cart[pkg_id] = quantity + 1
            else:
                premium_cart[pkg_id] = 1
        else:
            premium_cart = {}
            premium_cart[pkg_id] = 1
        request.session['premium_cart'] = premium_cart

        return redirect("premium_direct_checkout")


def premium_direct_checkout(request):
    premium_cart = request.session.get('premium_cart')
    if not premium_cart:
        request.session['premium_cart'] = {}
    ids = list(request.session.get('premium_cart').keys())
    premium_packages = PremiumOfferPackage.get_package_ids(ids)
    # user = request.user
    off = Offer.objects.filter(user=request.user)
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        address = request.POST.get('addresss')
        user = request.user
        offer_id = request.POST.get('offer_id')
        premium_packages = PremiumOfferPackage.get_package_ids(list(premium_cart.keys()))
        for pp in premium_packages:
            p_checkout = PremiumOfferPackageCheckout(
                first_name=first_name,
                addresss=address,
                user=user,
                pkg=pp,
                offer=Offer.objects.get(id=offer_id),
                quantity=premium_cart.get(str(pp.id)),
                total=pp.price
            )
            p_checkout.save()
            request.session['cart'] = {}
            return redirect("BuyerOrders")

    args = {
        "off": off,
        "premium_packages": premium_packages
    }

    return render(request, "azimpart/package_checkout.html", args)


def premium_payment(request, id, *args, **kwargs):
    premium_details = PremiumOfferPackageCheckout.objects.get(pk=id)
    if request.method == 'POST':
        settings = {
                'store_id': 'testbox', 'store_pass': 'qwerty', 'issandbox': True
            }
        premium_details = PremiumOfferPackageCheckout.objects.get(pk=id)
        user = request.user
        first_name = premium_details.first_name
        address = premium_details.addresss
        email = premium_details.user.email
        phone_number = request.user.selleraccount.contact_no
        country = request.user.selleraccount.country
        city = request.user.selleraccount.city
        # package_category = premium_details.package.offer.category
        quantity = premium_details.quantity
        total = premium_details.total
        transaction_id = premium_details.id

        # Checkout.objects.filter(pk=kwargs['id'])
        PremiumOfferPackageCheckout.objects.get(pk=id)

        sslcommerz1 = SSLCOMMERZ(settings)
        post_body1 = {}
        post_body1['total_amount'] = total
        post_body1['currency'] = "BDT"
        # post_bo1dy1['tran_id'] = "STFU"
        post_body1['tran_id'] = transaction_id
        post_body1['success_url'] = "https://marketage.io/betaversion/premium-success/"
        post_body1['fail_url'] = "https://marketage.io/betaversion/premium-failed/"
        post_body1['cancel_url'] = "https://marketage.io/betaversion/premium-cancel/"
        post_body1['emi_option'] = 0
        post_body1['cus_name'] = first_name
        post_body1['cus_email'] = email
        post_body1['cus_add1'] = "N/A"
        post_body1['cus_phone'] = phone_number
        post_body1['cus_city'] = city
        post_body1['cus_country'] = country
        post_body1['shipping_method'] = "NO"
        post_body1['multi_card_name'] = ""
        post_body1['num_of_item'] = "1"
        post_body1['product_name'] = premium_details.pkg
        post_body1['product_category'] = "DIGITAL"
        post_body1['product_profile'] = "general"
        print(post_body1)
        response = sslcommerz1.createSession(post_body1)
        print(response)
        return redirect(response['GatewayPageURL'])
        # return redirect(response['failedreason'])
        # return HttpResponse("HAHA")
    args = {
        "premium_details": premium_details
    }
    return render(request, "azimpart/premium_payment.html", args)

@csrf_exempt
def premium_successView(request):
    if request.POST.get('status') == "VALID":
        tran_id = request.POST['tran_id']
        # print("TRAIN ID:", tran_id)
        premium_details = PremiumOfferPackageCheckout.objects.get(id=tran_id)
        premium_details.is_paid = True
        premium_details.status = "ACTIVE"
        premium_details.offer.is_premium=True
        premium_details.offer.save()
        premium_details.save()
        
    return render(request, "responseview/premium_success.html")


@login_required(login_url='user_login')
@has_selleraccount
@csrf_exempt
def premiumfailedView(request):
    return render(request, "responseview/premium_failed.html")


@login_required(login_url='user_login')
@has_selleraccount
@csrf_exempt
def premiumcancelledView(request):
    return render(request, "responseview/premium_cancel.html")