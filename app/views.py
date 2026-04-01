from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Member, MembershipPlan

# 1. DASHBOARD: High-level overview with 4-color stat cards
def dashboard(request):
    active_members = Member.objects.filter(is_active=True)
    archived_count = Member.objects.filter(is_active=False).count()
    
    # Logic for "Expiring Soon" (Yellow Card - Next 7 Days)
    seven_days_from_now = timezone.now() + timedelta(days=7)
    expiring_soon_count = Member.objects.filter(
        is_active=True, 
        expiry_date__lte=seven_days_from_now,
        expiry_date__gte=timezone.now()
    ).count()

    context = {
        'members': active_members,
        'archived_count': archived_count,
        'expiring_soon_count': expiring_soon_count,
    }
    return render(request, 'dashboard.html', context)

# 2. MEMBERS LIST: Dedicated management tab with the EDIT button
def members_list(request):
    members = Member.objects.filter(is_active=True)
    return render(request, 'members_list.html', {'members': members})

# 3. ADD MEMBER: Initial registration (Name, Email, Phone only)
def add_member(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        # Check for existing user to prevent IntegrityError
        if User.objects.filter(username=email).exists():
            messages.error(request, f"Member with email {email} already exists!")
            return redirect('add_member')

        try:
            # Create Auth User
            user = User.objects.create_user(username=email, email=email)
            # Create Gym Member Profile
            Member.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                phone_number=phone_number
            )
            messages.success(request, f"Added {full_name}. Now assign a plan below.")
            return redirect('members_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('add_member')

    return render(request, 'add_member.html')

# 4. EDIT MEMBER: Assign Plan & Duration (The page you requested)
def edit_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    plans = MembershipPlan.objects.all()
    
    if request.method == "POST":
        member.full_name = request.POST.get('full_name')
        member.email = request.POST.get('email')
        member.phone_number = request.POST.get('phone_number')
        
        plan_id = request.POST.get('plan')
        if plan_id:
            member.plan = MembershipPlan.objects.get(id=plan_id)
        
        member.duration_months = int(request.POST.get('months'))
        member.expiry_date = None # Forces model save() to recalculate expiry
        member.save()
        
        messages.success(request, f"Profile for {member.full_name} updated!")
        return redirect('members_list')
        
    return render(request, 'edit_member.html', {'member': member, 'plans': plans})

# 5. UPGRADE: Tier-based upgrading logic
def upgrade_membership(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    plans = MembershipPlan.objects.all().order_by('tier_level')
    
    if request.method == "POST":
        new_plan_id = request.POST.get('new_plan')
        new_plan = MembershipPlan.objects.get(id=new_plan_id)
        
        if new_plan.tier_level > member.plan.tier_level:
            member.plan = new_plan
            member.expiry_date = None # Recalculate based on current tier
            member.save()
            messages.success(request, f"Upgraded to {new_plan.name}!")
        else:
            messages.error(request, "Cannot downgrade membership tier.")
        return redirect('members_list')

    return render(request, 'upgrade.html', {'member': member, 'plans': plans})

# 6. ARCHIVE & DELETE (Soft Delete)
def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_active = False
    member.save()
    messages.warning(request, f"{member.full_name} moved to Archive.")
    return redirect('dashboard')

def member_archive(request):
    past_members = Member.objects.filter(is_active=False)
    return render(request, 'member_archive.html', {'members': past_members})

def restore_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_active = True
    member.save()
    messages.success(request, f"{member.full_name} restored to active list.")
    return redirect('member_archive')

# 7. STATIC INFO TABS
def workout_plans(request):
    return render(request, 'workout_plans.html')

def tier_benefits(request):
    return render(request, 'tier_benefits.html')