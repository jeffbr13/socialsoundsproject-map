// Map creation + initialisation
var map = L.map('map')
    .setView([55.95, -3.2], 13)
    .addLayer(L.mapbox.tileLayer('jeffbr13.h81gnbgn', {
        detectRetina: true
    }));


var soundIcon = L.icon({
    iconUrl: '/static/img/marker.png',
    iconRetinaUrl: '/static/img/marker@2X.png',
    iconSize: [12,12]
});

// Events
function onMapClick(e) {
    $('#latitude').val(e.latlng.lat);
    $('#longitude').val(e.latlng.lng);
}

map.on('click', onMapClick);
