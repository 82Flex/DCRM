from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import RequestContext, Template
from django.test import TestCase
from django.test.client import RequestFactory

from preferences import context_processors, preferences
from preferences.admin import PreferencesAdmin
from preferences.tests.models import MyPreferences


class AdminTestCase(TestCase):

    def test_changelist_view(self):
        request = RequestFactory().get('/')
        request.user = User.objects.create(username='name', password='pass', is_superuser=True)
        admin_obj = PreferencesAdmin(MyPreferences, admin.site)

        # With only one preferences object redirect to its change view.
        response = admin_obj.changelist_view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/tests/mypreferences/1/change/')

        # With multiple preferences display listing view.
        MyPreferences.objects.create()
        response = admin_obj.changelist_view(request)
        response.render()
        self.failUnless('changelist-form' in response.content, 'Should \
display listing if multiple preferences objects are available.')

    def tearDown(self):
        MyPreferences.objects.all().delete()
        super(AdminTestCase, self).tearDown()


class ContextProcessorsTestCase(TestCase):

    def test_preferences_cp(self):
        request = RequestFactory().get('/')
        context = context_processors.preferences_cp(request)

        # context should have preferences.
        my_preferences = context['preferences']

        # preferences should have test MyPreferences object member.
        my_preferences = my_preferences.MyPreferences
        self.failUnless(isinstance(my_preferences, MyPreferences),
                        "%s should be instance of MyPreferences." % my_preferences)

        # With preferences_cp is loaded as a TEMPLATE_CONTEXT_PROCESSORS
        # templates should have access to preferences object.
        context_instance = RequestContext(request)
        t = Template("{% if preferences %}{{ preferences }}{% endif %}")
        self.failUnless(t.render(context_instance), "preferences should be \
available in template context.")

        t = Template("{% if preferences.MyPreferences %}{{ \
preferences.MyPreferences }}{% endif %}")
        self.failUnless(t.render(context_instance), "MyPreferences should be \
available as part of preferences var in template context.")

    def tearDown(self):
        MyPreferences.objects.all().delete()
        super(ContextProcessorsTestCase, self).tearDown()


class ModelsTestCase(TestCase):

    def test_preferences_class_prepared(self):
        """
        Regardless of what happens in the background, after startup and model
        preparation the preferences.preferences object should have members for
        each of the various preferences models. When accessing the member the
        appropriate object for the current site should be returned (or
        unassociated with a site if not using sites).
        """

        # Should have MyPreferences member without
        # sites since we are not using sites.
        my_preferences = preferences.MyPreferences
        self.failIf(my_preferences.sites.all(), "Without SITE_ID should not \
have any preferences with sites.")

        # Should have MyPreferences member for current site.
        settings.SITE_ID = 1
        current_site = Site.objects.get_current()
        my_preferences = preferences.MyPreferences
        self.failUnlessEqual(current_site, my_preferences.sites.get(), "With \
SITE_ID should have preferences for current site.")

        # Should have MyPreferences member for current site.
        settings.SITE_ID = 2
        second_site, created = Site.objects.get_or_create(id=2)
        my_preferences = preferences.MyPreferences
        self.failUnlessEqual(second_site, my_preferences.sites.get(), "With \
SITE_ID should have preferences for current site.")

    def test_site_cleanup(self):
        """
        There should only ever be a single preferences object per site. Thus on
        many to many changes pre-existing preferences should be cleared of
        sites already associated with current preferences object.
        """
        # When creating new preferences for a site, said site should be
        # removed from existing preference sites.
        site1 = Site.objects.create(domain="testserver")
        site2 = Site.objects.create(domain="another")

        # Add preferences for site 1.
        site1_preferences = MyPreferences.objects.create()
        site1_preferences.sites.add(site1)
        self.failUnlessEqual(site1_preferences.sites.get(), site1)

        # Now if we add another preferences object for site1, original site1
        # preferences should no longer be associated with site1.
        more_site1_preferences = MyPreferences.objects.create()
        more_site1_preferences.sites.add(site1)
        self.failIf(site1 in site1_preferences.sites.all())

        # If we add more sites to a preference,
        # it should be associated with them all.
        more_site1_preferences.sites.add(site2)
        self.failIf(site1 not in more_site1_preferences.sites.all() or site2 not in more_site1_preferences.sites.all())
        some_more_preferences = MyPreferences.objects.create()
        some_more_preferences.sites.add(site1)
        some_more_preferences.sites.add(site2)
        self.failIf(site1 in more_site1_preferences.sites.all() or site2 in more_site1_preferences.sites.all())
        # Double check that we now only have a single
        # preferences object associated with both sites.
        self.failUnlessEqual(MyPreferences.objects.filter(sites__in=[site1, site2]).distinct().get(),
                             some_more_preferences)

    def tearDown(self):
        MyPreferences.objects.all().delete()
        settings.SITE_ID = None
        super(ModelsTestCase, self).tearDown()


class SingletonManagerTestCase(TestCase):

    def test_get_queryset(self):
        # Should return preferences without sites.
        # Shouldn't fail on duplicates.
        self.failIf(MyPreferences.singleton.get().sites.all(), "Without \
                SITE_ID should not have any preferences with sites.")

        # Should return preferences for current site.
        # Shouldn't fail on duplicates.
        settings.SITE_ID = 1
        current_site = Site.objects.get_current()
        obj = MyPreferences.singleton.get()
        self.failUnlessEqual(current_site, obj.sites.get(), "With SITE_ID \
                should have preferences for current site.")

        # Should return preferences for current site.
        # Shouldn't fail on duplicates.
        settings.SITE_ID = 2
        second_site, created = Site.objects.get_or_create(id=2)
        obj = MyPreferences.singleton.get()
        self.failUnlessEqual(second_site, obj.sites.get(), "With SITE_ID \
                should have preferences for current site.")

    def tearDown(self):
        MyPreferences.objects.all().delete()
        settings.SITE_ID = None
        super(SingletonManagerTestCase, self).tearDown()
