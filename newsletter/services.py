from django.db.models import Count, Q

from .models import MailingList, SendAttempt


class Statistic:
    @staticmethod
    def get_statistic(user):
        attempts = SendAttempt.objects.filter(owner=user)
        total_attempts = attempts.count()
        success_attempts = attempts.filter(status=SendAttempt.SUCCESS).count()
        failed_attempts = attempts.filter(status=SendAttempt.FAILURE).count()
        success_rate = 0
        if total_attempts > 0:
            success_rate = (success_attempts / total_attempts) * 100
        messages_stats = (
            MailingList.objects.filter(owner=user)
            .annotate(
                total=Count("sendattempt"),
                success=Count("sendattempt", filter=Q(sendattempt__status=SendAttempt.SUCCESS)),
                failed=Count("sendattempt", filter=Q(sendattempt__status=SendAttempt.FAILURE)),
            )
            .values("message__title", "total", "success", "failed")
        )

        return {
            "total_attempts": total_attempts,
            "success_attempts": success_attempts,
            "failed_attempts": failed_attempts,
            "success_rate": round(success_rate, 2),
            "messages_stats": messages_stats,
            "total_mailings": MailingList.objects.filter(owner=user).count(),
            "active_mailings": MailingList.objects.filter(owner=user, status=MailingList.STARTED).count(),
            "completed_mailings": MailingList.objects.filter(owner=user, status=MailingList.COMPLETED).count(),
        }
