from django.urls import path
from django.conf import settings
from newsletter.apps import NewsletterConfig
from newsletter.views import HomeView, RecipientListView, MailingListView, RecipientDetailView, MailingDetailView, \
        MailSend, StatisticView, RecipientCreateView, MailingListCreateView, MailingListToggleView, MessageCreateView, \
        MessageListView, MessageUpdateView, MessageDeleteView, MailingListUpdateView, MailingListDeleteView, \
        RecipientDeleteView, RecipientUpdateView
from django.conf.urls.static import static


app_name = NewsletterConfig.name

urlpatterns = ([
        path("home_page/", HomeView.as_view(), name="home_page"),
        path("recipient_list/", RecipientListView.as_view(), name="recipient_list"),
        path("recipient_detail/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
        path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
        path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),
        path('recipient/<int:pk>/edit/', RecipientUpdateView.as_view(), name='recipient_edit'),
        path("mailing_list/", MailingListView.as_view(), name="mailing_list"),
        path("mailing_detail/<int:pk>", MailingDetailView.as_view(), name="mailing_detail"),
        path("mailing/create/", MailingListCreateView.as_view(), name="mailing_create"),
        path('mailing/<int:pk>/edit/', MailingListUpdateView.as_view(), name='mailing_edit'),
        path('mailing/<int:pk>/delete/', MailingListDeleteView.as_view(), name='mailing_delete'),
        path("mailing_detail/<int:pk>/send_mai", MailSend.as_view(), name="send_mail"),
        path('statistic/', StatisticView.as_view(), name='statistic'),
        path("mailing/toggle/<int:pk>/", MailingListToggleView.as_view(), name="mailing_toggle"),
        path('messages/', MessageListView.as_view(), name='message_list'),
        path('message/create/', MessageCreateView.as_view(), name='message_create'),
        path('message/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
        path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
