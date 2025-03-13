from django.urls import path
from main.views import (DashboardView, LoginSignUpView, BotUserMessageView, SendMessageView, BotPendingMessageView,
                        UserView, BotView)

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('login', LoginSignUpView.as_view(), name="login_or_signup"),
    path("chat-bot/<int:bot_id>", BotUserMessageView.as_view(), name="bot_messages"),
    path("send-message", SendMessageView.as_view(), name="send_message"),
    path("get-pending-message", BotPendingMessageView.as_view(), name="get_pending_message"),
    path("users", UserView.as_view(), name="users"),
    path("bots", BotView.as_view(), name="bots"),
]
