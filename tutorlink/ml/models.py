from django.conf import settings
from django.db import models
from listings.models import Listing

# Create your models here.
class PriceFlag(models.Model):
    # the flag belongs to the listing. deleting the listing (or its tutor) deletes the flag
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='price_flag')
    note = models.CharField(max_length=250, blank=True)
    # the staff member who flagged it. if their account is deleted the flag stays,because it is about the listing's price, not about them
    flagged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, related_name='price_flags_raised')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Flag on {self.listing}'