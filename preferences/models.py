from django.db import models
from django.dispatch import receiver

import preferences
from preferences.managers import SingletonManager


class Preferences(models.Model):
    objects = models.Manager()
    singleton = SingletonManager()
    sites = models.ManyToManyField('sites.Site', blank=True)

    def __str__(self):
        """
        Include site names.
        """
        site_names = [site.name for site in self.sites.all()]
        prefix = self._meta.verbose_name_plural.capitalize()

        if len(site_names) > 1:
            return '%s for sites %s and %s.' % (prefix, ', '.join(site_names[:-1]), site_names[-1])
        elif len(site_names) == 1:
            return '%s for site %s.' % (prefix, site_names[0])
        return '%s without assigned site.' % prefix


@receiver(models.signals.class_prepared)
def preferences_class_prepared(sender, *args, **kwargs):
    """
    Adds various preferences members to preferences.preferences,
    thus enabling easy access from code.
    """
    cls = sender
    if issubclass(cls, Preferences):
        # Add singleton manager to subclasses.
        cls.add_to_class('singleton', SingletonManager())
        # Add property for preferences object to preferences.preferences.
        setattr(preferences.Preferences, cls._meta.object_name, property(lambda x: cls.singleton.get()))


@receiver(models.signals.m2m_changed)
def site_cleanup(sender, action, instance, **kwargs):
    """
    Make sure there is only a single preferences object per site.
    So remove sites from pre-existing preferences objects.
    """
    if action == 'post_add':
        if isinstance(instance, Preferences) \
            and hasattr(instance.__class__, 'objects'):
            site_conflicts = instance.__class__.objects.filter(
                sites__in=instance.sites.all()
            ).only('id').distinct()

            for conflict in site_conflicts:
                if conflict.id != instance.id:
                    for site in instance.sites.all():
                        conflict.sites.remove(site)
