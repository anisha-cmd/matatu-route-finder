from django.db import models
from django.conf import settings
from decimal import Decimal


class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class SACCO(models.Model):
    PAYMENT_METHODS = (
        ('MPESA', 'MPESA'),
        ('CASH', 'Cash'),
        ('BOTH', 'MPESA & Cash'),
    )

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='MPESA')

    def __str__(self):
        return self.name


class Route(models.Model):
    name = models.CharField(max_length=150)
    from_stage = models.ForeignKey(Stage, related_name='routes_from', on_delete=models.CASCADE)
    to_stage = models.ForeignKey(Stage, related_name='routes_to', on_delete=models.CASCADE)

    # A route can have many matatus (SACCOs)
    saccos = models.ManyToManyField(SACCO, related_name='routes')

    base_fare = models.DecimalField(max_digits=8, decimal_places=2)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_stage} → {self.to_stage}"

    # ✅ Dynamic Fare Logic
    def get_current_fare(self, hour):
        """
        Peak hours:
        6–9 AM and 4–8 PM → +30%
        """
        if 6 <= hour <= 9 or 16 <= hour <= 20:
            return self.base_fare * Decimal('1.3')
        return self.base_fare


class Stop(models.Model):
    name = models.CharField(max_length=100)
    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # ← this is required

    def _str_(self):
        return self.name

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'route')
        ordering = ['-created_at']

    def _str_(self):
        return f"{self.user} → {self.route} ({self.rating}/5)"
