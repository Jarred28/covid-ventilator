var map;

var locations = {};

function getLatlng(address) {
  return new Promise(function(resolve) {
    var oReq = new XMLHttpRequest();

    function reqListener () {
      var data = JSON.parse(this.responseText);
      var location = data.results[0].geometry.location;
      const latitude = location.lat;
      const longitude = location.lng;
      resolve({ lat: latitude, lng: longitude });
    }

    oReq.addEventListener('load', reqListener);
    oReq.open('GET', 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address.replace(/ +/g, '+') +'&key=' + apiKey);
    oReq.send();
  });
}

var promises = [];
for (var i = 0; i < demands.length; i++) {
  promises.push(getLatlng(demands[i]));
}

for (var i = 0; i < supplies.length; i++) {
  promises.push(getLatlng(supplies[i]));
}

for (var i = 0; i < transits.length; i++) {
  promises.push(getLatlng(transits[i]));
}

Promise.all(promises).then(function(res) {
  locations.demand = res.slice(0, demands.length);
  locations.supply = res.slice(demands.length, demands.length + supplies.length);
  locations.transit = res.slice(demands.length + supplies.length, demands.length + supplies.length + transits.length);

  var newyorkBounds = {
    north: 45.01,
    south: 40.30,
    west: -79.46,
    east: -71.52
  };

  map = new google.maps.Map(document.getElementById('map'), {
    center: {
      lat: (newyorkBounds.north + newyorkBounds.south) / 2,
      lng: (newyorkBounds.west + newyorkBounds.east) / 2
    },
    restriction: {
      latLngBounds: newyorkBounds,
      strictBounds: false,
    },
    zoom: 7
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
});
