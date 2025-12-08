from django.db import models
from django.conf import settings

class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class SACCO(models.Model):
    PAYMENT_CHOICES = [
        ('MPESA', 'MPESA'),
        ('CASH', 'Cash Only'),
        ('CARD', 'Card'),
    ]
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=50, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')

    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField(max_length=150)
    from_stage = models.ForeignKey(Stage, related_name='routes_from', on_delete=models.CASCADE)
    to_stage = models.ForeignKey(Stage, related_name='routes_to', on_delete=models.CASCADE)
    saccos = models.ManyToManyField(SACCO, related_name='routes')
    fare = models.DecimalField(max_digits=8, decimal_places=2)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='routes/', blank=True, null=True)  # optional image per route
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_stage} → {self.to_stage}"

class Stop(models.Model):
    name = models.CharField(max_length=100)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order}. {self.name} ({self.route})"

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'route')
        ordering = ['-id']

    def __str__(self):
        return f"{self.user} → {self.route} ({self.rating}/5)"


