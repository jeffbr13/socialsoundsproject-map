// Click-and-drag marker to update form latitude and longitude:
// ------------------------------------------------------------

position_marker = L.marker([55.946, -3.186], {
    icon: soundIcon,
    draggable: true
});

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
