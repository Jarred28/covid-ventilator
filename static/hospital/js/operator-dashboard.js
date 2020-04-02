var map;

var locations = {
  demand: [
    {lat: 34.155834, lng: -119.202789},
    {lat: 27.192223, lng: -80.243057},
    {lat: 31.442778, lng: -100.450279},
    {lat: 40.560001, lng: -74.290001},
    {lat: 33.193611, lng: -117.241112}
  ],
  supply: [
    {lat: 41.676388, lng: -86.250275},
    {lat: 41.543056, lng: -90.590836},
    {lat: 39.554443, lng: -119.735558},
    {lat: 44.513332, lng: -88.015831},
    {lat: 37.554169, lng: -122.313057}  
  ],
  transit: [
    {lat: 32.349998, lng: -95.300003},
    {lat: 29.499722, lng: -95.089722},
    {lat: 33.038334, lng: -97.006111},
    {lat: 43.614166, lng: -116.398888},
    {lat: 41.556110, lng: -73.041389}  
  ]
};

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 39.971, lng: -99.668},
    zoom: 5
  });

  for (var type in locations) {
    locations[type].forEach(function(location) {
      var marker = new google.maps.Marker({
        position: location,
        map: map,
        icon: '/static/imgs/markers/' + type + '.png',
      });
    });
  }
}

