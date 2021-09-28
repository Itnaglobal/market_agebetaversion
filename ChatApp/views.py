from django.shortcuts import render, HttpResponse, redirect

from ChatApp.models import ChatRoom, Message

from django.contrib.auth.models import User

from django.db.models import Q

from datetime import datetime

from django.utils import timezone

from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

import random, string

# Create your views here.





@login_required(login_url='user_login')

def home_page(request):

    all_users = User.objects.exclude(username=request.user)

    # all_users = User.objects.all()

    ct_room = ChatRoom.objects.filter(sellers=request.user).order_by("-id")

    for_buyer = ChatRoom.objects.filter(buyer=request.user).order_by("-id")

    # print(ct_room)

    args = {

        'all_users': all_users,

        'ct_room': ct_room,

        'for_buyer': for_buyer

    }

    return render(request, 'Test/index.html', args)





def create_random_chatroom_slug(str_len):

    rand_slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))

    chatroom = ChatRoom.objects.filter(slug=rand_slug)

    if chatroom.exists():

        create_offer_random_slug(str_len)

    return rand_slug



@login_required(login_url='user_login')

def user_details(request, id):

    user_details = User.objects.get(pk=id)

    

    args = {

        'user_details': user_details

    }

    if request.method == 'POST':
        buyer = request.user
        sellers = user_details.username        

        try:

            sellers = User.objects.get(username=sellers)
            room_name = request.POST.get('room_name')

        except:

            return redirect("/")

        else:

            slug = create_random_chatroom_slug(20)

            room = ChatRoom(

                slug=slug, buyer=buyer, sellers=sellers, room_name=room_name

            )

            room.save()



            return redirect(f"/betaversion/chat/chatroom/{room.id}/{room.slug}/")

        

    return render(request, 'Test/user_details.html', args)



@login_required(login_url='user_login')

def postChatRoomView(request, id, slug):

    msg_lst = []

    chatroom = ChatRoom.objects.get(pk=id, slug=slug)

    values = Message.objects.filter(chatroom=id)

    month_dct = {

                1: "Jan.", 2: "Feb.", 3: "March", 4: "April", 5: "May",

                6: "June", 7: "July", 8: "Aug.", 9: "Sept.", 10: "Oct.",

                11: "Nov.", 12: "Dec."

            }

    

    for item in values:

        send_at = item.send_date

        month = int(send_at.strftime("%m"))

        month = str(month_dct[month])

        # print(month)

        day = str(int(send_at.strftime("%d")))

        # print(day)

        year = str(send_at.strftime("%Y"))

        hour = str(send_at.strftime("%I"))

        minute = str(send_at.strftime("%M"))

        am_pm = str(send_at.strftime("%p").lower())

        

        send_at = f"{month} {day}, {year}, {hour}:{minute} {am_pm}"

        

        msgs = {

            "id": str(sent.id),

            "profile_image": str(item.sender.selleraccount.profile_picture),

            "message": item.msg,

            "username": item.sender.username,

            "send_at": send_at

        }

        msg_lst.append(msgs)

    return JsonResponse(msg_lst, safe=False)



@login_required(login_url='user_login')

def chatRoomView(request, id, slug):

    try:

        chatroom = ChatRoom.objects.get(pk=id, slug=slug)

    except ChatRoom.DoesNotExist:

        return redirect("manage-order")

    else:

        values = Message.objects.filter(chatroom=id)

        rooms = ChatRoom.objects.filter(Q(buyer=request.user) or Q(sellers=request.user)).order_by("-id")

        # print(values.sent_date)

        current_time = datetime.now(timezone.utc)

        # print("Current Time: " + str(current_time))

    

        last = chatroom.buyer.last_login

    

        ago = str(current_time - last).split(",")[0]

    

        # print(ago + "AGOOOOOOOO")

    

        # print("BEFORE:", len(Message.objects.all()))

    

        if request.method == 'POST':

            receiver = None

            sender = request.user

            

            if sender == chatroom.sellers:

                receiver = chatroom.buyer

            else:

                receiver = chatroom.sellers

            

            msg = request.POST.get('msg')

            message = None

            sent = Message(sender=sender, receiver=receiver, msg=msg, chatroom=chatroom)

    

            chatroom.recent_chat = True

            chatroom.save()

            sent.save()

    

            # print("IMAGE:", str(sender.selleraccount.profile_picture))

            # print("USER:", sender)

            # print("MESSAGE:", msg)

    

            if request.is_ajax():

                month_dct = {

                    1: "Jan.", 2: "Feb.", 3: "March", 4: "April", 5: "May",

                    6: "June", 7: "July", 8: "Aug.", 9: "Sept.", 10: "Oct.",

                    11: "Nov.", 12: "Dec."

                }

    

                send_at = sent.sent_date

                month = int(send_at.strftime("%m"))

                month = str(month_dct[month])

                # print(month)

                day = str(int(send_at.strftime("%d")))

                # print(day)

                year = str(send_at.strftime("%Y"))

                hour = str(send_at.strftime("%I"))

                minute = str(send_at.strftime("%M"))

                am_pm = str(send_at.strftime("%p").lower())

                

    

                # send_at = send_at.strftime("%b %d, %Y, %I:%M %p")

                send_at = f"{month} {day}, {year}, {hour}:{minute} {am_pm}"

                profile_image = str(sender.selleraccount.profile_picture)

    

                message = {

                    "id": str(sent.id),

                    "profile_image": profile_image,

                    "message": msg,

                    "username": sender.username,

                    "send_at": send_at

                }

    

                print("MESAGE", message)

                print("AFTER:", len(Message.objects.all()))

    

                # x =  str(Message.objects.all())

                # print(Message.objects.values())

    

                data = {

                    "message_info": message

                }

                return JsonResponse(data)

            return redirect(f"/betaversion/chat/chatroom/{chatroom.id}/{chatroom.slug}/")

    

    

    args = {

        'chatroom': chatroom,

        'values': values,

        'rooms': rooms,

        'ago': ago

    }

        

    # print(chatroom)

    return render(request, "Test/chatRoom.html", args)