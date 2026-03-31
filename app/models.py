from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

class MembershipPlan(models.Model):
    # Tier levels: 1=Basic, 2=Premium, 3=VIP
    tier_level = models.IntegerField(unique=True) 
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    plan = models.ForeignKey(MembershipPlan, on_delete=models.SET_NULL, null=True)
    registration_date = models.DateTimeField(default=timezone.now)
    duration_months = models.IntegerField(default=1)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # NEW FIELD: This determines if they show on Dashboard or Archive
    is_active = models.BooleanField(default=True) 

    def save(self, *args, **kwargs):
        if not self.expiry_date:
            self.expiry_date = self.registration_date + timedelta(days=30 * self.duration_months)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name
