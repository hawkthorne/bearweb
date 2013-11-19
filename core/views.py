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

from .forms import ContactForm, AccessKeyForm
from core import tasks
from dockerindex.models import Repository, AccessKey
from dockerindex import models
from core.models import Subscription

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


class HomeView(TemplateView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            self.template_name = 'core/home_feed.html'
        else:
            self.template_name = 'core/index.html'
        response = super(HomeView, self).get(request, *args, **kwargs)
        return response.render()

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        if not self.request.user.is_authenticated():
            return context

        token = AccessKey.find_or_create(self.request.user)
        code_tag = CODE_TAG.format(self.request.user.get_username())
        code_push = CODE_PUSH.format(self.request.user.get_username())

        context['repos'] = Repository.objects.filter(user=self.request.user)
        context['docker_tag'] = highlight(code_tag,
                                          BashLexer(), HtmlFormatter())
        context['docker_push'] = highlight(code_push,
                                           BashLexer(), HtmlFormatter())
        context['dockercfg'] = highlight(token.logincmd(),
                                         BashLexer(), HtmlFormatter())
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

    def get_context_data(self, **kwargs):
        context = super(GuideView, self).get_context_data(**kwargs)
        user = self.request.user
        context['host'] = settings.DOCKER_DOMAIN

        if user.is_authenticated():
            context['username'] = user.get_username()
            context['token'] = AccessKey.find_or_create(user).token
        else:
            context['token'] = "{token}"
            context['username'] = "{username}"

        return context


class AccessTokenCreate(LoginRequiredMixpanel, FormView):
    template_name = "dockerindex/accesskey_form.html"
    success_url = reverse_lazy('tokens')
    form_class = AccessKeyForm

    def get_form(self, form_class):
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        repo = form.cleaned_data['repository']

        if repo and repo.user != self.request.user:
            raise Http404

        # FIXME: Leaky abstraction
        key = AccessKey(user=self.request.user, token=models._token(),
                        access=form.cleaned_data['access'])

        if repo:
            key.repository = repo

        key.save()
        return super(AccessTokenCreate, self).form_valid(form)


class AccessTokenView(LoginRequiredMixpanel, TemplateView):
    template_name = "core/tokens.html"

    def get_context_data(self, **kwargs):
        context = super(AccessTokenView, self).get_context_data(**kwargs)
        context['tokens'] = AccessKey.objects.filter(user=self.request.user)
        return context


class PortalView(LoginRequiredMixpanel, TemplateView):
    template_name = "core/account.html"

    def get_context_data(self, **kwargs):
        context = super(PortalView, self).get_context_data(**kwargs)

        token = AccessKey.find_or_create(self.request.user)
        code = CODE_TAG.format(self.request.user.get_username())

        context['plan'] = Subscription.display_name_for(self.request.user)
        context['docker'] = highlight(code, BashLexer(), HtmlFormatter())
        context['dockercfg'] = highlight(token.logincmd(),
                                         BashLexer(), HtmlFormatter())
        return context


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


class RepositoryView(LoginRequiredMixpanel, DetailView):
    model = Repository

    def get_context_data(self, **kwargs):
        context = super(RepositoryView, self).get_context_data(**kwargs)

        namespace = self.request.user.get_username()

        push = REPO_PUSH.format(namespace, self.object.name)
        pull = REPO_PULL.format(namespace, self.object.name)

        tag = self.object.latest_tag()

        raw = {}

        if tag:
            raw = json.loads(tag.image.json)

            if 'id' in raw:
                raw['id'] = raw['id'][:16]

            if 'container' in raw:
                raw['container'] = raw['container'][:16]

            if 'parent' in raw:
                raw['parent'] = raw['parent'][:16]

        context['pullcode'] = highlight(pull, BashLexer(), HtmlFormatter())
        context['pushcode'] = highlight(push, BashLexer(), HtmlFormatter())
        context['info'] = raw

        return context

    def get_object(self, queryset=None):
        obj = super(RepositoryView, self).get_object(queryset=queryset)
        if obj.user != self.request.user:
            raise Http404("Repository not owned by current user")
        return obj


class RepositoryDelete(LoginRequiredMixpanel, DeleteView):
    model = Repository
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        obj = super(RepositoryDelete, self).get_object(queryset=queryset)
        if obj.user != self.request.user:
            raise Http404("Repository not owned by current user")
        return obj


def user_redirect(request):
    return redirect('portal')
