function filterSearch(evt) {
  evt.preventDefault();
  console.log('is this getting thru?');
  $('#pre_filter').hide();
  $('#post_filter').show();
  var givenMiles = $('#miles').val();
  console.log(givenMiles);
  var latitude = $('#input_lat').val();
  console.log(latitude);
  var longitude = $('#input_lng').val();
  var postType = $('.type').val();
  var keyword = $('#keyword_search').val();
  var address = $('#location_search').val();
  var categories = $('input:checked').map(function () {
       return $(this).val(); 
   }).get(); // upon second look - no idea what the preceding actually does
  console.log(categories)
  var data = {given_miles : givenMiles,
        latitude : latitude,
        longitude : longitude,
        post_type : postType,
        keyword : keyword,
        categories : categories};
  $.get("/filter_search", data, function(results) {
    var postings = results['results'];
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 3,
      center: {lat: latitude, lng: longitude}
    });
    var labels = [for (posting of postings) posting.title];
    var markers = locations.map(function(location, i) {
      return new google.maps.Marker({
        position: location,
        label: labels[i % labels.length]
      });
    });

    var markerCluster = new MarkerClusterer(map, markers,
        {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
  }
  var locations = [for (posting.latitude of postings) for (posting.longitude of postings) 
                  {lat: posting.latitude, lng: posting.longitude}];
}

$('#filter').on('submit', filterSearch);