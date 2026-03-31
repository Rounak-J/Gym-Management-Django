from django.shortcuts import render, redirect, get_object_or_404
from .models import Member, MembershipPlan
from django.contrib import messages

def dashboard(request):
    members = Member.objects.all()
    plans = MembershipPlan.objects.all()
    return render(request, 'dashboard.html', {'members': members, 'plans': plans})

# 2. Delete Member Logic
def delete_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    member.delete()
    messages.success(request, "Member deleted successfully.")
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