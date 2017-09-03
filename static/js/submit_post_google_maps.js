var map, infoWindow, geocoder;
function getRandom(min, max) {
    return Math.random() * (max - min) + min;
}

$('#submit_address').on('click', function (evt) {geocodeAddress(geocoder, evt)
});
function geocodeAddress(geocoder, evt) {
  evt.preventDefault();
  var address = $('#post_locator').val();
  console.log(address); 
  if (address !== "") {
    geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {
      var ran_float = getRandom(-0.01, 0.01);
      latitude = results[0].geometry.location.lat() + ran_float;
      longitude = results[0].geometry.location.lng() + ran_float;
      $('#latitude').val(latitude);
      $('#longitude').val(longitude);
      map.setCenter({lat: latitude, lng: longitude});
      infoWindow.setPosition({lat: latitude, lng: longitude});
      infoWindow.setContent('Approximate location of address found.' + "<br>" + "<h6>" + "This exact address will not appear anywhere. A random lat/long generator has been used to provide a location within a reasonsble distance of this address." + "</h6>");
      infoWindow.open(map);
      // resultsMap.setCenter(results[0].geometry.location);
      // var marker = new google.maps.Marker({
      //   map: resultsMap,
      //   position: results[0].geometry.location
      // });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
  }
}

function initMap() {
  geocoder = new google.maps.Geocoder();
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: -34.397, lng: 150.644},
    zoom: 15
  });
  infoWindow = new google.maps.InfoWindow;

  // Try HTML5 geolocation.

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var ran_float = getRandom(-0.01, 0.01);
      console.log(ran_float);
      var pos = {
        lat: position.coords.latitude + ran_float,
        lng: position.coords.longitude + ran_float
      };
      $('#latitude').val(pos['lat']);
      $('#longitude').val(pos['lng']);

      infoWindow.setPosition(pos);
      infoWindow.setContent('Approximate location found.' + "<br>" + "<h6>" + "Your exact address will not appear anywhere. A random lat/long generator has been used to provide a location within a reasonsble distance of your current location." + "</h6>");
      infoWindow.open(map);
      map.setCenter(pos);
    }, function() {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  } else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
                        'Error: The Geolocation service failed.' :
                        'Error: Your browser doesn\'t support geolocation.');
  infoWindow.open(map);
}