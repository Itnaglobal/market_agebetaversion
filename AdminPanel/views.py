from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from mainApp.models import *
from django.core.paginator import Paginator

# Create your views here.

def adminLoginView(request):
    return render(request, "admin_login.html")




def get_adminpanel_url(request):
    orders = Checkout.objects.all().order_by('-id')
    count_order = Checkout.objects.all().count()
    count_offers = Offer.objects.all().count()

    completed_orders = Checkout.objects.filter(is_complete=True).count()

    increase = completed_orders / 100

    orders_paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')

    orders_obj = orders_paginator.get_page(page_number)

    args = {
        "orders": orders,
        "orders_obj": orders_obj,
        "count_order": count_order,
        "count_offers": count_offers,
        "increase": increase
    }
    return render(request, 'admin_panel.html', args)


def order_details(request, id):
    order_details = Checkout.objects.get(pk=id)

    args = {
        "order_details": order_details
    }

    return render(request, "admin_order_Details.html", args)




def uploadedOfferView(request):
    all_offers = Offer.objects.all().order_by('-id')

    args = {
        "all_offers": all_offers
    }
    return render(request, "uploaded_offer.html", args)



# Edit Offer for admin panel
def admin_edit_offer(request, id):
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
            admin_post_status = request.POST.get("admin_post_status")

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

            service = Services.objects.get(title=service)
            category = Category.objects.get(title=category)

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
            offer.description = content
            
            if admin_post_status:
                offer.offer_status = admin_post_status
                
            offer.save()
            
            if main_image_id or extra_image_id1 or extra_image_id2 or extra_image_id3 or offer_video_id or offer_document_id:
                return redirect(f"/betaversion/adminpanel/update_offer/{offer.id}/")
            
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
    return render(request, 'admin_edit_offer.html', args)



def allUsersView(request):
    users = User.objects.exclude(username=request.user).order_by('-id')

    args = {
        "users": users
    }

    return render(request, "all_users.html", args)



def allOrdersView(request):
    orders = Checkout.objects.all().order_by('-id')
    args = {
        "orders": orders
    }
    return render(request, "all_order.html", args)



def adminLoginView(request):
    return render(request, "admin_login.html")



def transactionView(request):
    transactions = Checkout.objects.filter(paid=True)
    completed_orders = Checkout.objects.filter(is_complete=True).count()
    increase = (completed_orders / 100)
    args = {
        'transactions': transactions,
        'increase': increase
    }
    return render(request, "transactions.html", args)


def withdrawView(request):
    withdraws = WithDrawModel.objects.filter(on_review=True)
    args = {
        'withdraws': withdraws,
    }
    return render(request, "withdraw.html", args)

def clear_amount(request, id):
    clear_wd = WithDrawModel.objects.get(pk=id)
    order_by_seller = Checkout.objects.filter(seller =clear_wd.user)
    if request.method == "POST":
        method = request.POST.get('method')
        amount = request.POST.get('amount')
        user = clear_wd.user
        stat = request.POST.get('stat')

        WithDrawModel.objects.update(
            stat=stat
        )
        

        # return HttpResponse("SUCCESS")
        return redirect("WithdrawView")
    args = {
        "clear_wd": clear_wd,
        "order_by_seller": order_by_seller,
    }

    return render(request, "withdraw_details.html", args)
