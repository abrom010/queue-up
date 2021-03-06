var map;
var service;
var infoWindow;
var geocoder;
var autocomplete;
var markers = [];

function httpGet(theUrl) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", theUrl, false );
  xmlHttp.send( null );
  return xmlHttp.response;
}

function httpPost(theUrl,data) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("POST", theUrl, false );
  xmlHttp.send( data );
  return xmlHttp.response;
}

function initMap() {
  var latlong = new google.maps.LatLng(39, -101);
  var mapOptions = {
      zoom: 5.5,
      center: latlong,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    }

  map = new google.maps.Map(
      document.getElementById('map'), mapOptions);

  autocomplete = new google.maps.places.Autocomplete(document.getElementById('autocomplete'));
  autocomplete.addListener('place_changed', onPlaceChanged);

  places = new google.maps.places.PlacesService(map);

  addresses_to_markers();

  map.addListener('bounds_changed',search)
  map.addListener('zoom_changed',search)

  infoWindow = new google.maps.InfoWindow({
      content: document.getElementById('info-content')
  });
}

function onPlaceChanged() {
  console.log('place changed')
  var place = autocomplete.getPlace();
  if (place.geometry) {
    map.panTo(place.geometry.location);
    map.setZoom(13);
    search();
  } else {
    document.getElementById('autocomplete').placeholder = 'Enter a city';
  }
}

function search() {
  bounds = map.getBounds();
  zoom = map.getZoom();

  for(var i = 0; i < markers.length; i++){
    let marker = markers[i]

    if(marker){
      if(bounds.contains(marker.getPosition()) && zoom > 6){
        marker.setMap(map)
      } else {
        marker.setMap(null)
      }
    }
  }
}

function openWindow(){
  marker = this
  document.getElementById("title").innerHTML = marker.title;
  document.getElementById('address').innerHTML = marker.address;
  console.log(marker.id)
  loc = "location='/ticket/" + marker.id + "'";
  document.getElementById("butt").setAttribute( "onclick", loc);
  // console.log(loc)

  infoWindow.open(map,marker)
}

function addresses_to_markers() {
  let data = httpGet('/ids')
  ids = JSON.parse(data)

  geocoder = new google.maps.Geocoder();

  for(var i = 0; i<ids.length; i++){
  	let formdata = new FormData()
  	formdata.append("groceryID",ids[i])
    let address = httpPost('/address', formdata)
    address = address.replace(/['"]+/g, '')
    let name = httpPost('/name', formdata)
    name = name.replace(/['"]+/g, '')
    let id = ids[i]
    // console.log(id)
    geocoder.geocode( { 'address': address }, (results, status) =>{
      // console.log(id)
    if (status == google.maps.GeocoderStatus.OK) {
      let place = results[0]
      // console.log(id)
      markers.push(createMarker(place,name,address,id))
    } else {
      alert('Geocode was not successful for the following reason: ' + status)
    }
    });
  }
}

function createMarker(place,name,address,id) {
  let marker = new google.maps.Marker({
    map: null,
    position: place.geometry.location,
    animation: google.maps.Animation.DROP,
    label:name[0],

    title:name,
    id:id,
    address:address

  });
  google.maps.event.addListener(marker, 'click', openWindow);
  return marker
}
