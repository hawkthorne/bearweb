import json

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.forms import ValidationError
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView, DeleteView
from django.http import Http404
from django.conf import settings

from braces.views import LoginRequiredMixin
from pygments import highlight
from pygments.lexers import BashLexer
from pygments.formatters import HtmlFormatter

from .forms import ContactForm
from core import tasks
from games.models import Game

import stripe

CODE_TAG = """# Then, find the image you'd like to push to your repository
$ docker images
{{name}}  latest  123abc123abc  12 weeks ago  263 MB (virtual 263 MB)

# Almost there!
# Tag to create a repository with the full registry location.
# The location becomes a permanent part of the repository name.
$ docker tag 123abc123abc stackmachine.com/{0}/{{name}}
"""

CODE_PUSH = """
# Finally, push the new repository to its home location.
$ docker push stackmachine.com/{0}/{{name}}
"""

REPO_PUSH = """
$ docker push stackmachine.com/{0}/{1}
"""

REPO_PULL = """
$ docker pull stackmachine.com/{0}/{1}
"""


def track(event, **kwargs):
    try:
        tasks.track.delay(event, **kwargs)
    except:  # Gotta catch 'em all
        pass


class LoginRequiredMixpanel(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        view = super(LoginRequiredMixpanel, self).\
            dispatch(request, *args, **kwargs)

        if request.method == 'GET' and request.user.username:
            track('Visit Page', distinct_id=request.user.username,
                  path=request.path)

        return view


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'core/home_feed.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context['games'] = Game.objects.filter(owner=self.request.user)
        return context


class ContactView(FormView):
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = '/contact'

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'Contact email sent')
        return super(ContactView, self).form_valid(form)


class PricingView(TemplateView):
    template_name = "core/pricing.html"


class GuideView(TemplateView):
    template_name = "core/guide.html"


class PortalView(LoginRequiredMixpanel, TemplateView):
    template_name = "core/account.html"


class UpgradeView(LoginRequiredMixpanel, TemplateView):

    def get(self, request, *args, **kwargs):
        if request.user.subscription_set.count() > 0:
            self.template_name = "core/upgrade_existing.html"
        else:
            self.template_name = "core/upgrade_initial.html"
        response = super(UpgradeView, self).get(request, *args, **kwargs)
        return response.render()

    def get_context_data(self, **kwargs):
        context = super(UpgradeView, self).get_context_data(**kwargs)
        context['plan'] = Subscription.display_name_for(self.request.user)
        context['stripe_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


class ChangePlanView(LoginRequiredMixpanel, FormView):

    def post(self, request, *args, **kwargs):
        plan = request.POST.get('plan')
        if not plan:
            return ValidationError("Missing token or plan")
        subscription = Subscription.objects.get(user=self.request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        c = stripe.Customer.retrieve(subscription.stripe_id)
        c.update_subscription(plan=plan, prorate="True")
        subscription.plan = plan
        subscription.save()

        track('Change Plan', distinct_id=request.user.username, plan=plan)

        messages.success(self.request, "Changed to the %s plan." % plan)
        return redirect("portal")


class UpgradePayView(LoginRequiredMixpanel, FormView):

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Get the credit card details submitted by the form
        token = request.POST.get('stripeToken')
        plan = request.POST.get('plan')

        if not token or not plan:
            return ValidationError("Missing token or plan")

        # Create a Customer
        customer = stripe.Customer.create(
            card=token,
            plan=plan,
            email=self.request.user.get_username() + "@users.stackmachine.com"
        )
        request.user.subscription_set.create(
            stripe_id=customer["id"], plan=plan
        )

        track('Upgrade', distinct_id=request.user.username, plan=plan)

        messages.success(self.request, "Subscribed to the %s plan." % plan)
        return redirect("portal")


def user_redirect(request):
    return redirect('portal')
