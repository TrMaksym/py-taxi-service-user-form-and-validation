from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import DriverCreationForm, DriverLicenseUpdateForm
from .models import Driver, Car, Manufacturer


@login_required
def index(request):
    """View function for the home page of the site."""

    num_drivers = Driver.objects.count()
    num_cars = Car.objects.count()
    num_manufacturers = Manufacturer.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_drivers": num_drivers,
        "num_cars": num_cars,
        "num_manufacturers": num_manufacturers,
        "num_visits": num_visits + 1,
    }

    return render(request, "taxi/index.html", context=context)


class ManufacturerListView(LoginRequiredMixin, generic.ListView):
    model = Manufacturer
    context_object_name = "manufacturer_list"
    template_name = "taxi/manufacturer_list.html"
    paginate_by = 5


class ManufacturerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Manufacturer
    fields = "__all__"
    success_url = reverse_lazy("taxi:manufacturer-list")


class ManufacturerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Manufacturer
    success_url = reverse_lazy("taxi:manufacturer-list")


class CarListView(LoginRequiredMixin, generic.ListView):
    model = Car
    paginate_by = 5
    queryset = Car.objects.all().select_related("manufacturer")


class CarDetailView(LoginRequiredMixin, generic.DetailView):
    model = Car
    context_object_name = "car"

class CarCreateView(LoginRequiredMixin, generic.CreateView):
    model = Car
    fields = "__all__"
    success_url = reverse_lazy("taxi:car-list")


class CarUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Car
    fields = "__all__"
    success_url = reverse_lazy("taxi:car-list")


class CarDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Car
    success_url = reverse_lazy("taxi:car-list")


class DriverListView(LoginRequiredMixin, generic.ListView):
    model = Driver
    paginate_by = 5


class DriverDetailView(LoginRequiredMixin, generic.DetailView):
    model = Driver
    queryset = Driver.objects.all().prefetch_related("cars__manufacturer")


class DriverCreateView(LoginRequiredMixin, generic.CreateView):
    model = Driver
    form_class = DriverCreationForm
    template_name = 'taxi/driver_form.html'
    success_url = reverse_lazy("taxi:driver-list")


def driver_license_update(request: HttpRequest, pk) -> HttpResponse:
    driver = get_object_or_404(Driver, pk=pk)

    if request.method == 'POST':
        form = DriverLicenseUpdateForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('taxi:driver_list'))
    else:
        form = DriverLicenseUpdateForm(instance=driver)

    return render(request, 'taxi/driver_license_update.html', {'form': form, 'driver': driver})


class DriverUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Driver
    form_class = DriverLicenseUpdateForm
    template_name = "taxi/driver_license_update.html"

def get_success_url(request: HttpRequest) -> HttpResponse:
    return reverse_lazy("taxi:driver-list")


class DriverDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Driver
    success_url = reverse_lazy("taxi:driver-list")
    template_name = "taxi/driver_confirm_delete.html"


@login_required
def assign_driver_to_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.user not in car.drivers.all():
        car.drivers.add(request.user)
    return redirect('taxi:car-detail', pk=car.pk)


@login_required
def remove_driver_from_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.user in car.drivers.all():
        car.drivers.remove(request.user)
    return redirect('taxi:car-detail', pk=car.pk)

def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    manufacturer = car.manufacturer

    context = {
        'car': car,
        "manufacturer": manufacturer,
        'drivers': car.drivers.all(),
    }
    return render(request, 'taxi/car_detail.html', context=context)

@login_required
def driver_detail(request, pk):
    driver = get_object_or_404(User, pk=pk)
    cars = driver.cars.all()

    context = {
        'driver': driver,
        'cars': cars,
    }
    return render(request, 'taxi/driver_detail.html', context)