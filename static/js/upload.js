// Map creation + initialisation
var map = L.map('map')
    .setView([55.947, -3.2], 14)
    .addLayer(L.mapbox.tileLayer('socialsoundsproject.h9hbe4l4', {
        detectRetina: true
    }));


var soundIcon = L.icon({
    iconUrl: '/static/img/marker.png',
    iconRetinaUrl: '/static/img/marker@2X.png',
    iconSize: [12,12]
});

position_marker = L.marker([55.946, -3.186], {
    icon: soundIcon,
    draggable: true
});

// Events
function onMapClick(e) {
    $('#latitude').val(e.latlng.lat);
    $('#longitude').val(e.latlng.lng);
    position_marker.setLatLng(e.latlng).addTo(map);
}

function onMarkerDrag (e) {
    $('#latitude').val(e.target._latlng.lat);
    $('#longitude').val(e.target._latlng.lng);
}

map.on('click', onMapClick);
position_marker.on('drag', onMarkerDrag);
