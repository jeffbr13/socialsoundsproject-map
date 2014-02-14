// Map creation + initialisation
var map = L.map('map')
    .setView([55.95, -3.2], 14)
    .addLayer(L.mapbox.tileLayer('jeffbr13.h81gnbgn', {
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

map.on('click', onMapClick);
