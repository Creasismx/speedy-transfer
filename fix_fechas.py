import os

path = r"c:\Users\adolf\Documents\speedy-transfer\templates\speedy_app\includes\fechas.html"

content = """{% load static %}
<section id="hero" class="hero-bg py-8 md:py-16 lg:py-24 relative overflow-hidden">
  <!-- Decorative Background Elements (Optional) -->
  <div class="absolute inset-0 opacity-10" style="background-image: url('{% static 'img/pattern.png' %}');"></div>

  <div class="container relative z-10 grid lg:grid-cols-2 gap-8 md:gap-12 items-center">
    <!-- Hero Text -->
    <div class="text-white text-center lg:text-left mb-8 lg:mb-0">
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 leading-tight">
        Premium Transfers <br><span style="color: var(--secondary);">Puerto Vallarta</span>
      </h1>
      <p class="text-lg md:text-xl opacity-90 mb-8 max-w-xl mx-auto lg:mx-0">
        Safe, reliable, and comfortable airport transportation. Avoid the hassle and start your vacation the moment you
        land.
      </p>
      <div class="flex gap-4 justify-center lg:justify-start">
        <div class="flex items-center gap-2">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span>No hidden fees</span>
        </div>
        <div class="flex items-center gap-2">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <span>Clean Vehicles</span>
        </div>
      </div>
    </div>

    <!-- Booking Widget Card -->
    <div class="card shadow-lg bg-white bg-opacity-100 text-gray-900 w-full max-w-xl mx-auto lg:ml-auto">
      <h2 class="text-2xl font-bold mb-6 text-center text-primary-dark">Book Your Transfer</h2>

      <form action="{% url 'core:results_view' %}" method="get" class="w-full">
        <!-- Trip Type -->
        <div class="flex gap-4 mb-6 justify-center bg-slate-100 p-2 rounded-lg">
          <label class="form-check cursor-pointer">
            <input type="radio" name="trip_type" value="oneway" {% if request.GET.trip_type == 'oneway' or not request.GET.trip_type %}checked{% endif %} />
            <span class="font-medium">One Way</span>
          </label>
          <label class="form-check cursor-pointer">
            <input type="radio" name="trip_type" value="roundtrip" {% if request.GET.trip_type == 'roundtrip' %}checked{% endif %} />
            <span class="font-medium">Round Trip</span>
          </label>
        </div>

        <div class="grid md:grid-cols-2 gap-4">
          <!-- Arrival Information -->
          <div class="form-group">
            <label class="form-label">Pickup Location</label>
            <select name="pickup_location" class="form-control" required>
              <option value="" disabled {% if not request.GET.pickup_location %}selected{% endif %}>Select Hotel /
                Airport</option>
              {% for zone in zones_with_hotels %}
              <optgroup label="{{ zone.name }}">
                {% for hotel in zone.hotels.all %}
                <option value="{{ hotel.id }}" {% if request.GET.pickup_location|add:0 == hotel.id %}selected{% endif %}>
                  {{ hotel.name }}</option>
                {% endfor %}
              </optgroup>
              {% endfor %}
              {% if hotels_without_zone %}
              <optgroup label="Other Locations">
                {% for hotel in hotels_without_zone %}
                <option value="{{ hotel.id }}" {% if request.GET.pickup_location|add:0 == hotel.id %}selected{% endif %}>
                  {{ hotel.name }}</option>
                {% endfor %}
              </optgroup>
              {% endif %}
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Dropoff Location</label>
            <select name="dropoff_location" class="form-control" required>
              <option value="" disabled {% if not request.GET.dropoff_location %}selected{% endif %}>Select Hotel /
                Airport</option>
              {% for zone in zones_with_hotels %}
              <optgroup label="{{ zone.name }}">
                {% for hotel in zone.hotels.all %}
                <option value="{{ hotel.id }}" {% if request.GET.dropoff_location|add:0 == hotel.id %}selected{% endif %}>
                  {{ hotel.name }}</option>
                {% endfor %}
              </optgroup>
              {% endfor %}
              {% if hotels_without_zone %}
              <optgroup label="Other Locations">
                {% for hotel in hotels_without_zone %}
                <option value="{{ hotel.id }}" {% if request.GET.dropoff_location|add:0 == hotel.id %}selected{% endif %}>
                  {{ hotel.name }}</option>
                {% endfor %}
              </optgroup>
              {% endif %}
            </select>
          </div>
        </div>

        <div class="grid md:grid-cols-2 gap-4">
          <div class="form-group">
            <label class="form-label">Pickup Date & Time</label>
            <input type="datetime-local" name="pickup_datetime" class="form-control"
              value="{{ request.GET.pickup_datetime }}" required />
          </div>

          <div class="form-group">
            <label class="form-label">Passengers</label>
            <input name="people" value="{{ request.GET.people }}" min="1" type="number" class="form-control" required
              placeholder="Pax count" />
          </div>
        </div>

        <!-- Return Fields (Hidden by default via JS) -->
        <div id="return-section" class="border-t pt-4 mt-2">
          <h3 class="text-sm font-bold text-muted uppercase mb-3">Return Details</h3>
          <div class="grid md:grid-cols-2 gap-4">
            <div class="form-group">
              <label class="form-label">Return Pickup</label>
              <select name="return_pickup_location" class="form-control">
                <option value="" disabled {% if not request.GET.return_pickup_location %}selected{% endif %}>Select
                  Hotel / Airport</option>
                {% for zone in zones_with_hotels %}
                <optgroup label="{{ zone.name }}">
                  {% for hotel in zone.hotels.all %}
                  <option value="{{ hotel.id }}" {% if request.GET.return_pickup_location|add:0 == hotel.id %}selected{%
                    endif %}>{{ hotel.name }}</option>
                  {% endfor %}
                </optgroup>
                {% endfor %}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Return Dropoff</label>
              <select name="return_dropoff_location" class="form-control">
                <option value="" disabled {% if not request.GET.return_dropoff_location %}selected{% endif %}>Select
                  Hotel / Airport</option>
                {% for zone in zones_with_hotels %}
                <optgroup label="{{ zone.name }}">
                  {% for hotel in zone.hotels.all %}
                  <option value="{{ hotel.id }}" {% if request.GET.return_dropoff_location|add:0 == hotel.id %}selected{%
                    endif %}>{{ hotel.name }}</option>
                  {% endfor %}
                </optgroup>
                {% endfor %}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Return Date & Time</label>
              <input type="datetime-local" name="return_datetime" class="form-control"
                value="{{ request.GET.return_datetime }}" />
            </div>
          </div>
        </div>

        <div class="form-group mt-6">
          <button type="submit" class="btn btn-primary w-full text-lg shadow-md">
            Find Transfers
          </button>
        </div>
      </form>
    </div>
  </div>
</section>

<script>
  document.addEventListener('DOMContentLoaded', function () {
    const radios = document.querySelectorAll('input[name="trip_type"]');
    const returnSection = document.getElementById('return-section');
    const returnDivider = document.getElementById('return-divider');
    const form = document.querySelector('#fechas form');

    const returnDT = document.querySelector('input[name="return_datetime"]');
    const returnPickup = document.querySelector('select[name="return_pickup_location"]');
    const returnDropoff = document.querySelector('select[name="return_dropoff_location"]');

    function setReturnRequired(isRequired) {
      const fields = [returnDT, returnPickup, returnDropoff];
      fields.forEach(function (el) {
        if (!el) return;
        if (isRequired) {
          el.setAttribute('required', 'required');
          el.setAttribute('aria-required', 'true');
        } else {
          el.removeAttribute('required');
          el.removeAttribute('aria-required');
        }
      });
    }

    function updateReturnSection() {
      const selected = document.querySelector('input[name="trip_type"]:checked');
      if (selected?.value === 'oneway') {
        returnSection.style.display = 'none';
        // returnDivider.style.display = 'none'; // Element not in DOM in this template
        setReturnRequired(false);
      } else {
        returnSection.style.display = 'flex';
        // returnDivider.style.display = 'flex';
        setReturnRequired(true);
      }
    }

    // Initial check
    updateReturnSection();

    // Event listener
    radios.forEach(function (radio) {
      radio.addEventListener('change', updateReturnSection);
    });

    // Form level guard
    if (form) {
      form.addEventListener('submit', function (e) {
        const selected = document.querySelector('input[name="trip_type"]:checked');
        if (selected && selected.value === 'roundtrip') {
          if (!returnDT.value || !returnPickup.value || !returnDropoff.value) {
            e.preventDefault();
            e.stopPropagation();
            alert('Please complete the Return date/time, pickup and dropoff for a roundtrip.');
            return false;
          }
        }
        return true;
      });
    }
  });
</script>

<style>
  #return-section {
    transition: all 0.3s ease;
  }
</style>
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully overwrote {path}")
