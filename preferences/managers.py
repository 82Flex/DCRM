from django.conf import settings
from django.db import models
from django.contrib.sites.models import Site


class SingletonManager(models.Manager):
    """
    Returns only a single preferences object per site.
    """
    def get_queryset(self):
        """
        Return the first preferences object for the current site.
        If preferences do not exist create it.
        """
        queryset = super(SingletonManager, self).get_queryset()

        # Get current site
        current_site = None
        if getattr(settings, 'SITE_ID', None) is not None:
            current_site = Site.objects.get_current()

        # If site found limit queryset to site.
        if current_site is not None:
            queryset = queryset.filter(sites=settings.SITE_ID)

        try:
            queryset.get()
        except self.model.DoesNotExist:
            # Create object (for current site) if it doesn't exist.
            obj = self.model.objects.create()
            if current_site is not None:
                obj.sites.add(current_site)

        return queryset
