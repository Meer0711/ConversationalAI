import json
import time

import jwt
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from main.settings import EXTERNAL_SERVICE_BASE_URL


class DashboardView(View):
    def get(self, request):
        api_key = request.COOKIES.get("api_key")
        user_id = request.COOKIES.get("user_id")
        if api_key is not None and user_id is not None:
            # getting user details
            response = requests.get(
                headers={
                    "X-API-KEY": api_key,
                    "USER-ID": user_id 

                },
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/user-detail/{user_id}"
            )
            return render(
                request,
                "dashboard.html",
                context=response.json()
            )
        return redirect("login_or_signup")


class LoginSignUpView(View):

    def get(self, request):
        api_key = request.COOKIES.get("api_key")
        user_id = request.COOKIES.get("user_id")
        if api_key is not None and user_id is not None:
            return redirect("dashboard")
        return render(
            request,
            "login.html",
            {}
        )

    def post(self, request):
        try:
            action = request.POST["action"]
            if action == "sign_in":
                response = requests.post(
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/sign-in",
                    json=dict(
                        email=request.POST["email"]
                    )
                )
            else:
                response = requests.post(
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/sign-up",
                    json=dict(
                        account_name=request.POST["account_name"],
                        email=request.POST["email"],
                        is_admin=True
                    )
                )
            if response.status_code == 200:
                response_data = response.json()
                return JsonResponse(
                    data={
                        "api_key": response_data["api_key"],
                        "user_id": response_data["user_id"]
                    }, 
                    status=200
                )
            return JsonResponse(
                data=response.json(), status=response.status_code
            )
        except Exception as exc:
            return JsonResponse(
                data={"detail": exc.__str__()}, status=500
            )


class BotUserMessageView(View):

    def get(self, request, bot_id):
        api_key = request.COOKIES.get("api_key")
        user_id = request.COOKIES.get("user_id")
        if api_key is not None and user_id is not None:
            response = {"messages": [], "detail": "", "user": {}, "bot_id": bot_id, "bot_detail": {}}
            
            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }

            user_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/user-detail{user_id}"
            )
            if user_response.status_code == 200:
                response["user"] = user_response.json()

            bot_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/bot-detail/{bot_id}"
            )
            if bot_response.status_code == 200:
                response["bot_detail"] = bot_response.json()

            messages_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/bot-messages/{bot_id}"
            )
            messages_response_detail = messages_response.json()
            if messages_response.status_code == 200:
                response["messages"] = messages_response_detail
            else:
                response["detail"] = messages_response_detail["detail"]

            return render(
                request,
                "BotUserMessageView.html",
                context=response
            )
        return redirect("login_or_signup")


class SendMessageView(View):

    def post(self, request):
        try:
            response = {"data": {}, "detail": "", "status": True}
            api_key = request.COOKIES.get("api_key")
            user_id = request.COOKIES.get("user_id")

            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }

            send_response = requests.post(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/send-message",
                json=dict(
                    bot_id=request.POST["bot_id"],
                    message=request.POST["message"]
                )
            )
            if send_response.status_code == 200:
                response["data"] = send_response.json()
            else:
                response["status"] = False
                response["detail"] = send_response.json()["detail"]

            return JsonResponse(
                data=response, status=send_response.status_code
            )
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return JsonResponse(
                data={"detail": str(exc)}, status=500
            )


class BotPendingMessageView(View):

    def get(self, request):
        response = {"message": "", "status": False, "error": ""}
        try:
            api_key = request.COOKIES.get("api_key")
            user_id = request.COOKIES.get("user_id")
            bot_id = request.GET["bot_id"]
            message_id = request.GET["message_id"]

            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }

            ext_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/get-message/{bot_id}/{message_id}"
            )
            if ext_response.status_code == 200:
                response_data = ext_response.json()
                return JsonResponse(data=response_data, status=ext_response.status_code)
            return JsonResponse(data={"detail": ext_response.json()["detail"]}, status=ext_response.status_code)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            response["error"] = str(exc)
            return JsonResponse(data=response, status=500)


class UserView(View):

    def get(self, request):
        api_key = request.COOKIES.get("api_key")
        user_id = request.COOKIES.get("user_id")
        if api_key is not None and user_id is not None:
            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }
            
            response = {"users": [], "detail": "", "user": {}, "bots": [], "is_admin": True}
            
            user_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/user-detail{user_id}"
            )
            if user_response.status_code == 200:
                response["user"] = user_response.json()

            bot_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/bots"
            )
            if bot_response.status_code == 200:
                response["bots"] = bot_response.json()

            users_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/users"
            )
            if users_response.status_code == 200:
                response["users"] = users_response.json()

            return render(
                request,
                "users.html",
                context=response
            )
        return redirect("login_or_signup")

    def post(self, request):
        try:
            api_key = request.COOKIES.get("api_key")
            user_id = request.COOKIES.get("user_id")
            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }
            
            action = request.POST["action"]
            if action == "create":
                response = requests.post(
                    headers=headers,
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/create-user",
                    json=dict(
                        email=request.POST["email"]
                    )
                )
            elif action == "update":
                response = requests.put(
                    headers=headers,
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/update-user-bots",
                    json=dict(
                        user_id=request.POST["user_id"],
                        bot_ids=request.POST.getlist("bot_ids")
                    )
                )
            else:  # assume delete action
                user_id = request.POST["user_id"]
                response = requests.delete(
                    headers=headers,
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/delete-user/{user_id}"
                )

            if response.status_code == 200:
                return JsonResponse(data={}, status=response.status_code)
            return JsonResponse(data={"detail": response.json()["detail"]}, status=response.status_code)
        except Exception as exc:
            raise exc


class BotView(View):

    def get(self, request):
        api_key = request.COOKIES.get("api_key")
        user_id = request.COOKIES.get("user_id")
        if api_key is not None and user_id is not None:
            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }
            
            response = {"detail": "", "user": {}, "bots": [], "data_sources": [], "is_Admin": True}
            
            user_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/user-detail/{user_id}"
            )
            if user_response.status_code == 200:
                response["user"] = user_response.json()

            bot_response = requests.get(
                headers=headers,
                url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/bots"
            )
            if bot_response.status_code == 200:
                response["bots"] = bot_response.json()

            return render(
                request,
                "bots.html",
                context=response
            )
        return redirect("login_or_signup")

    def post(self, request):
        try:
            api_key = request.COOKIES.get("api_key")
            user_id = request.COOKIES.get("user_id")
            headers = {
                "X-API-KEY": api_key,
                "USER-ID": user_id
            }
            
            action = request.POST["action"]
            if action == "createBot":
                response = requests.post(
                    headers=headers,
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/create-bot",
                    json=dict(
                        name=request.POST["name"]
                    )
                )
            elif action == "createDataSource":
                file = request.FILES.get('file')
                response = requests.post(
                    headers=headers,
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/create-data-source",
                    data=dict(
                        bot_id=request.POST["bot_id"]
                    ),
                    files={"file": file}
                )
            else:  # assume delete action
                bot_id = request.POST["bot_id"]
                response = requests.delete(
                    headers=headers,
                    url=f"{EXTERNAL_SERVICE_BASE_URL}/api/v1/delete-bot/{bot_id}"
                )

            if response.status_code == 200:
                return JsonResponse(data={}, status=response.status_code)
            return JsonResponse(data={"detail": response.json()["detail"]}, status=response.status_code)
        except Exception as exc:
            raise exc
