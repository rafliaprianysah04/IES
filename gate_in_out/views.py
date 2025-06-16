from django.shortcuts import render

# Create your views here.

def dashboard_view(request):
    return render(request, 'gate_in_out/dashboard.html')

def truck_in(request):
    return render(request, 'gate_in_out/truck_in.html')

def truck_out(request):
    return render(request, 'gate_in_out/truck_out.html')

