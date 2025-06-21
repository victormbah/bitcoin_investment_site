from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_usd = models.FloatField()
    btc_rate = models.FloatField(default=0.0)
    confirmed = models.BooleanField(default=False)  # Whether user has actually paid BTC
    timestamp = models.DateTimeField(auto_now_add=True)

    def btc_amount(self):
        if self.btc_rate == 0:
            return 0  # Avoid ZeroDivisionError
        return self.amount_usd / self.btc_rate

    def days_since(self):
        return (timezone.now() - self.timestamp).days

    def current_value(self):
        """Simulate growth (75% profit after 30 days)"""
        days = self.days_since()
        growth_factor = min(days / 30, 1.0)  # Cap at 1.0
        return self.amount_usd * (1 + 0.75 * growth_factor)

    def can_withdraw(self):
        return self.confirmed and self.days_since() >= 30

    def __str__(self):
        return f"{self.user.username} - ${self.amount_usd} at ${self.btc_rate}"
