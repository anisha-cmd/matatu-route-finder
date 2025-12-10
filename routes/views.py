from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.utils.timezone import now
from django.contrib import messages
from .models import Stage, Route, Stop, Review, SACCO
from .mpesa import lipa_na_mpesa

# Home Page
def home(request):
    popular_routes = Route.objects.all()[:6]
    stages = Stage.objects.all()
    stops = Stop.objects.all()

    current_hour = now().hour
    dynamic_fares = {route.id: route.get_current_fare(current_hour) for route in popular_routes}

    return render(request, 'routes/home.html', {
        'popular_routes': popular_routes,
        'stages': stages,
        'stops': stops,
        'dynamic_fares': dynamic_fares
    })

# Search Routes
def search_routes(request):
    from_id = request.GET.get('from_stage')
    to_id = request.GET.get('to_stage')
    stop_id = request.GET.get('stop_stage')

    routes = Route.objects.all()

    if from_id:
        routes = routes.filter(Q(from_stage_id=from_id) | Q(to_stage_id=from_id))

    if to_id:
        routes = routes.filter(Q(from_stage_id=to_id) | Q(to_stage_id=to_id))

    if stop_id:
        routes = routes.filter(stops__id=stop_id)

    current_hour = now().hour
    dynamic_fares = {route.id: route.get_current_fare(current_hour) for route in routes}

    context = {
        'routes': routes,
        'from_stage': Stage.objects.filter(id=from_id).first() if from_id else None,
        'to_stage': Stage.objects.filter(id=to_id).first() if to_id else None,
        'stop': Stop.objects.filter(id=stop_id).first() if stop_id else None,
        'dynamic_fares': dynamic_fares
    }

    return render(request, 'routes/search_results.html', context)

# Route Details
def route_details(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    stops = route.stops.all()
    reviews = route.reviews.all()
    current_hour = now().hour
    dynamic_fare = route.get_current_fare(current_hour)

    return render(request, 'routes/route_details.html', {
        'route': route,
        'stops': stops,
        'reviews': reviews,
        'dynamic_fare': dynamic_fare
    })

# Add Review
def add_review(request, route_id):
    route = get_object_or_404(Route, id=route_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.update_or_create(
            user=request.user,
            route=route,
            defaults={'rating': rating, 'comment': comment}
        )
        return redirect('route_details', route_id=route.id)

    return render(request, 'routes/add_review.html', {'route': route})

# Stage Details
def stage_details(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id)
    routes = Route.objects.filter(Q(from_stage=stage) | Q(to_stage=stage))

    return render(request, 'routes/stage.html', {
        'stage': stage,
        'routes': routes
    })

# M-Pesa Payment per Stop
def mpesa_pay(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    stop_id = request.GET.get('stop_id')
    stop = get_object_or_404(Stop, id=stop_id, route=route)

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        sacco_id = request.POST.get("sacco_id")
        sacco = get_object_or_404(SACCO, id=sacco_id)

        try:
            result = lipa_na_mpesa(
                phone_number=phone_number,
                amount=float(stop.fare),
                account_ref=f"{route.from_stage.name} → {route.to_stage.name} | Stop: {stop.name}",
                transaction_desc="Matatu Fare Payment"
            )
            messages.success(request, f"Payment initiated. Response: {result.get('ResponseDescription')}")
        except Exception as e:
            messages.error(request, f"Payment failed: {str(e)}")

        return redirect("route_details", route_id=route.id)

    return render(request, 'routes/mpesa_pay.html', {
        'route': route,
        'stop': stop,
        'saccos': route.saccos.all()
    })


def cash_pay(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    stop_id = request.GET.get('stop_id')
    stop = get_object_or_404(Stop, id=stop_id, route=route)

    if request.method == "POST":
        payer_name = request.POST.get("payer_name")
        sacco_id = request.POST.get("sacco_id")
        sacco = get_object_or_404(SACCO, id=sacco_id)

        messages.success(request, f"Cash payment for stop '{stop.name}' recorded successfully.")
        return redirect("route_details", route_id=route.id)

    return render(request, 'routes/cash_pay.html', {
        'route': route,
        'stop': stop,
        'saccos': route.saccos.all()
    })