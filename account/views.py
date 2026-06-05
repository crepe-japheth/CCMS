from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy

from .forms import LoginForm
from .models import AuditLog
from .utils import log_audit


class UserLoginView(LoginView):
    template_name = 'account/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        log_audit(
            self.request.user,
            AuditLog.Action.LOGIN,
            description='User logged in successfully.',
            request=self.request,
        )
        messages.success(self.request, f'Welcome back, {self.request.user.full_name}!')
        return response

    def get_success_url(self):
        return reverse_lazy('ccms_app:dashboard')


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('account:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            log_audit(
                request.user,
                AuditLog.Action.LOGOUT,
                description='User logged out.',
                request=request,
            )
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile(request):
    return render(request, 'account/profile.html', {'active_nav': 'profile'})
