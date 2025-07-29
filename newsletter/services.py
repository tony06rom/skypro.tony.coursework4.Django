from django.contrib.messages import SUCCESS
from django.db.models import Count, Q

from .models import SendAttempt, MailingList


class Statistic:
    @staticmethod
    def get_statistic(user):
        # Получаем все попытки пользователя
        attempts = SendAttempt.objects.filter(owner=user)

        # Статистика по попыткам
        total_attempts = attempts.count()
        success_attempts = attempts.filter(status=SendAttempt.SUCCESS).count()  # Проверяем нижний регистр
        failed_attempts = attempts.filter(status=SendAttempt.FAILURE).count()  # Проверяем нижний регистр

        # Рассчитываем процент успешных попыток
        success_rate = 0
        if total_attempts > 0:
            success_rate = (success_attempts / total_attempts) * 100

        # Статистика по сообщениям
        messages_stats = MailingList.objects.filter(
            owner=user
        ).annotate(
            total=Count('sendattempt'),
            success=Count('sendattempt', filter=Q(sendattempt__status=SendAttempt.SUCCESS)),  # Проверяем нижний регистр
            failed=Count('sendattempt', filter=Q(sendattempt__status=SendAttempt.FAILURE))  # Проверяем нижний регистр
        ).values(
            'message__title',
            'total',
            'success',
            'failed'
        )

        return {
            'total_attempts': total_attempts,
            'success_attempts': success_attempts,
            'failed_attempts': failed_attempts,
            'success_rate': round(success_rate, 2),
            'messages_stats': messages_stats,
            'total_mailings': MailingList.objects.filter(owner=user).count(),
            'active_mailings': MailingList.objects.filter(owner=user, status=MailingList.STARTED).count(),
            # Проверяем нижний регистр
            'completed_mailings': MailingList.objects.filter(owner=user, status=MailingList.COMPLETED).count()
            # Проверяем нижний регистр
        }
