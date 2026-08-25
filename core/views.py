import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import VIPVisitor, EntryExitLog


@login_required
def dashboard(request):
    visitors = VIPVisitor.objects.all().order_by('-created_at')
    stats = {
        'total': visitors.count(),
        'expected': visitors.filter(status='EXPECTED').count(),
        'entered': visitors.filter(status='ENTERED').count(),
        'exited': visitors.filter(status='EXITED').count(),
    }
    recent_logs = EntryExitLog.objects.select_related('visitor')[:10]
    return render(request, 'core/dashboard.html', {
        'visitors': visitors,
        'stats': stats,
        'recent_logs': recent_logs
    })


@login_required
def add_visitor(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization', '')
        designation = request.POST.get('designation', '')

        if not full_name or not email or not phone:
            messages.error(request, 'Name, Email, and Phone are required.')
            return render(request, 'core/add_visitor.html')

        visitor = VIPVisitor.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            organization=organization,
            designation=designation
        )
        messages.success(request, f'VIP Pass generated for {visitor.full_name}')
        return redirect('view_pass', pass_id=visitor.pass_id)

    return render(request, 'core/add_visitor.html')


@login_required
def view_pass(request, pass_id):
    visitor = get_object_or_404(VIPVisitor, pass_id=pass_id)
    return render(request, 'core/view_pass.html', {'visitor': visitor})


@login_required
def scanner_interface(request):
    return render(request, 'core/scanner.html')


@login_required
@csrf_exempt
def process_scan(request):
    """API endpoint triggered by QR code reader."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)

    try:
        data = json.loads(request.body)
        pass_id = data.get('pass_id')
        action = data.get('action')  # 'ENTRY' or 'EXIT'

        if action not in ['ENTRY', 'EXIT']:
            return JsonResponse({'success': False, 'message': 'Invalid scan action.'}, status=400)

        with transaction.atomic():
            visitor = VIPVisitor.objects.select_for_update().get(pass_id=pass_id)

            if action == 'ENTRY':
                if visitor.status == 'ENTERED':
                    return JsonResponse({'success': False, 'message': f'{visitor.full_name} has ALREADY entered.'}, status=400)
                if visitor.status == 'EXITED':
                    return JsonResponse({'success': False, 'message': f'{visitor.full_name} has already completed their visit.'}, status=400)
                
                visitor.status = 'ENTERED'

            elif action == 'EXIT':
                if visitor.status == 'EXPECTED':
                    return JsonResponse({'success': False, 'message': f'Cannot exit. {visitor.full_name} has not entered yet.'}, status=400)
                if visitor.status == 'EXITED':
                    return JsonResponse({'success': False, 'message': f'{visitor.full_name} has already exited.'}, status=400)
                
                visitor.status = 'EXITED'

            visitor.save()
            EntryExitLog.objects.create(visitor=visitor, action=action)

            return JsonResponse({
                'success': True,
                'message': f'Successful {action} for {visitor.full_name}',
                'visitor': {
                    'name': visitor.full_name,
                    'organization': visitor.organization,
                    'status': visitor.get_status_display()
                }
            })

    except VIPVisitor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid QR Code: VIP Pass not found.'}, status=44)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)
    
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")