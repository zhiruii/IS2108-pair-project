from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AdminUserForm
from django.contrib import messages
from django.db.models import RestrictedError

from accounts.models import User, Child


@login_required
def admin_home_view(request):
    if request.user.role != 'STAFF':
        return redirect('index')

    context = {
        'user_count': User.objects.count(),
        'parent_count': User.objects.filter(role='PARENT').count(),
        'tutor_count': User.objects.filter(role='TUTOR').count(),
        'child_count': Child.objects.count(),
    }
    return render(request, 'adminpanel/home.html', context)


@login_required
def user_list_view(request):
    if request.user.role != 'STAFF':
        return redirect('index')

    users = User.objects.all().order_by('role', 'email')

    # Filter user based on roles
    role = request.GET.get('role')
    if role in ('PARENT', 'TUTOR', 'STAFF'):
        users = users.filter(role=role)

    return render(request, 'adminpanel/user_list.html', {'users': users, 'role': role})

@login_required
def user_edit_view(request, user_id):
    if request.user.role != 'STAFF':
        return redirect('index')

    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # No 'instance=' means we create new row
        form = AdminUserForm(request.POST, instance=target)

        if form.is_valid():
            if target == request.user and not form.cleaned_data['is_active']:
                form.add_error('is_active', 'You cannot deactivate your own account')
            else:
                form.save()
                return redirect('admin_user_list')

    else:
        form = AdminUserForm(instance=target)

    return render(request, 'adminpanel/user_edit.html', {'form': form, 'target': target})

@login_required
def user_delete_view(request, user_id):
    if request.user.role != 'STAFF':
        return redirect('index')

    target = get_object_or_404(User, id=user_id)

    if target == request.user:
        messages.error(request, 'You cannot delete your own admin account')
        return redirect('admin_user_list')

    if request.method == 'POST':
        try:
            target.delete()
            messages.success(request, f'Deleted {target.email}')

        except RestrictedError:
            messages.error(request, f'Cannot delete {target.email}, they have requests or bookings.')
        
        return redirect('admin_user_list')

    return render(request, 'adminpanel/user_delete.html', {'target': target})