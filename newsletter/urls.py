from django.urls import path
from django.conf import settings
from newsletter.apps import NewsletterConfig
from newsletter.views import HomeView, RecipientListView, MailingListView, RecipientDetailView, MailingDetailView, \
        MailSend, StatisticView
from django.conf.urls.static import static


app_name = NewsletterConfig.name

urlpatterns = ([
        path("home_page/", HomeView.as_view(), name="home_page"),
        path("recipient_list/", RecipientListView.as_view(), name="recipient_list"),
        path("recipient_detail/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
        path("mailing_list/", MailingListView.as_view(), name="mailing_list"),
        path("mailing_detail/<int:pk>", MailingDetailView.as_view(), name="mailing_detail"),
        path("mailing_detail/<int:pk>/send_mai", MailSend.as_view(), name="send_mail"),
        path('statistic/', StatisticView.as_view(), name='statistic'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
