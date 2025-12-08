from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db import models
from .models import Stage, Route, Stop, SACCO, Review
from django.contrib.auth.decorators import login_required

# Dynamic fare logic example
def get_dynamic_fare(route):
    """Adjust fare based on time of day."""
    now = timezone.localtime().time()  # current local time
    base_fare = route.fare
    # Example: rush hour 7-10am, 5-7pm = +20%
    if (now >= timezone.datetime.strptime("07:00", "%H:%M").time() and now <= timezone.datetime.strptime("10:00", "%H:%M").time()) \
        or (now >= timezone.datetime.strptime("17:00", "%H:%M").time() and now <= timezone.datetime.strptime("19:00", "%H:%M").time()):
        return round(base_fare * 1.2, 2)
    return base_fare

# Home page
def home(request):
    stages = Stage.objects.all()
    popular_routes = Route.objects.all()[:6]

    context = {
        'stages': stages,
        'popular_routes': popular_routes,
    }
    return render(request, 'routes/home.html', context)

# Search routes
def search_routes(request):
    from_stage_id = request.GET.get('from_stage')
    to_stage_id = request.GET.get('to_stage')
    stop_stage_id = request.GET.get('stop_stage')

    routes = Route.objects.all()

    if from_stage_id and to_stage_id:
        # Include bidirectional routes
        routes = routes.filter(
            (
                (models.Q(from_stage_id=from_stage_id) & models.Q(to_stage_id=to_stage_id)) |
                (models.Q(from_stage_id=to_stage_id) & models.Q(to_stage_id=from_stage_id))
            )
        )
    elif from_stage_id:
        routes = routes.filter(models.Q(from_stage_id=from_stage_id) | models.Q(to_stage_id=from_stage_id))
    elif to_stage_id:
        routes = routes.filter(models.Q(from_stage_id=to_stage_id) | models.Q(to_stage_id=to_stage_id))

    if stop_stage_id:
        routes = routes.filter(stops__id=stop_stage_id)

    stages = Stage.objects.all()
    context = {
        'routes': routes.distinct(),
        'stages': stages,
        'from_stage': Stage.objects.filter(id=from_stage_id).first() if from_stage_id else None,
        'to_stage': Stage.objects.filter(id=to_stage_id).first() if to_stage_id else None,
        'stop': Stage.objects.filter(id=stop_stage_id).first() if stop_stage_id else None,
    }
    return render(request, 'routes/search_results.html', context)

# Route details
def route_details(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    # Compute dynamic fare
    route_dynamic_fare = get_dynamic_fare(route)
    context = {
        'route': route,
        'stops': route.stops.all().order_by('order'),
        'dynamic_fare': route_dynamic_fare,
        'reviews': route.reviews.all()
    }
    return render(request, 'routes/route_details.html', context)

# Add review
@login_required
def add_review(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment", "")
        # Check if user already reviewed
        review, created = Review.objects.update_or_create(
            user=request.user,
            route=route,
            defaults={'rating': rating, 'comment': comment}
        )
        return redirect('route_details', route_id=route.id)
    return redirect('route_details', route_id=route.id)

# Optional: view all reviews
def ad_review(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    context = {
        'route': route,
    }
    return render(request, 'routes/ad_review.html', context)


# Placeholder MPESA payment
def mpesa_pay(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    if request.method == 'POST':
        sacco_id = request.POST.get('sacco_id')
        phone_number = request.POST.get('phone_number')
        sacco = get_object_or_404(SACCO, id=sacco_id)

        if sacco.payment_method != 'MPESA':
            return JsonResponse({"error": "This SACCO does not accept MPESA"}, status=400)

        amount = route.fare
        response = lipa_na_mpesa(phone_number, amount, account_reference=str(route.id),
                                 transaction_desc="Route Payment", shortcode=sacco.mpesa_shortcode)
        return JsonResponse(response)
    return redirect('route_details', route_id=route_id)
