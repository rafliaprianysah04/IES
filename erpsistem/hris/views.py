from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def dashboard(request):
    if request.user.app_id != 'hris':
        return HttpResponseForbidden('Anda tidak memiliki akses ke halaman ini.')

    context = {
        'title': 'Dashboard HRIS',
        'user': request.user
    }
    return render(request, 'hris/dashboard.html', context)
