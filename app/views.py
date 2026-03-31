from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, MembershipPlan
from django.contrib import messages

def dashboard(request):
    # This ensures "Deleted" members vanish from this list
    active_members = Member.objects.filter(is_active=True)
    return render(request, 'dashboard.html', {'members': active_members})

def add_member(request):
    # CRITICAL: This line fetches the plans from MySQL
    plans = MembershipPlan.objects.all() 
    
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        plan_id = request.POST.get('plan')
        months = int(request.POST.get('months')) 
        
        selected_plan = MembershipPlan.objects.get(id=plan_id)
        
        # User creation logic
        from django.contrib.auth.models import User
        import uuid
        username = f"{full_name.replace(' ', '').lower()}_{uuid.uuid4().hex[:4]}"
        user = User.objects.create(username=username)
        
        Member.objects.create(
            user=user,
            full_name=full_name,
            email=email,
            plan=selected_plan,
            duration_months=months
        )
        return redirect('dashboard')

    # CRITICAL: Passing 'plans' to the HTML template
    return render(request, 'add_member.html', {'plans': plans})

# 2. Delete Member Logic
def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_active = False # Move to archive
    member.save()
    messages.warning(request, f"{member.full_name} moved to Archive.")
    return redirect('dashboard')

def upgrade_membership(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    plans = MembershipPlan.objects.all()

    if request.method == "POST":
        new_plan_id = request.POST.get('new_plan')
        new_plan = MembershipPlan.objects.get(id=new_plan_id)

        # Logical Check: New tier must be higher than current tier
        if new_plan.tier_level > member.plan.tier_level:
            member.plan = new_plan
            member.save()
            messages.success(request, "Membership upgraded successfully!")
        else:
            messages.error(request, "You can only upgrade your plan, not downgrade.")
        
        return redirect('dashboard')

    return render(request, 'upgrade.html', {'member': member, 'plans': plans})

# 1. Workout Plans Logic
def workout_plans(request):
    return render(request, 'plans.html')

# 2. Tier Benefits Logic
def tier_benefits(request):
    plans = MembershipPlan.objects.all().order_by('tier_level')
    return render(request, 'tier_benefits.html', {'plans': plans})

# 3. Archive & Contacts Logic (Past Members)
def member_archive(request):
    # This captures only the people you "deleted"
    past_members = Member.objects.filter(is_active=False)
    return render(request, 'member_archive.html', {'members': past_members})

def restore_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.is_active = True
    member.save()
    messages.success(request, f"{member.full_name} has been restored to Active Members.")
    return redirect('member_archive')