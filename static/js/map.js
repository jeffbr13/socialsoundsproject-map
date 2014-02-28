// Map setup:
// ----------

function map_container_height () {
    var map_container_height = $( window ).height() - 100;
    $('#map').height(map_container_height);
}

map_container_height();
$( window ).resize(map_container_height);


var map = L.map( 'map' )
    .setView([55.947, -3.2], 11)
    .addLayer(L.mapbox.tileLayer('socialsoundsproject.h9hbe4l4', {
        detectRetina: true
    }));


var soundIcon = L.icon({
    iconUrl: '/static/img/marker.png',
    iconRetinaUrl: '/static/img/marker@2X.png',
    iconSize: [28,28]
});

var playIcon = L.icon({
    iconUrl: '/static/img/play.png',
    iconRetinaUrl: '/static/img/play@2X.png',
    iconSize: [28,28]
});

var pauseIcon = L.icon({
    iconUrl: '/static/img/pause.png',
    iconRetinaUrl: '/static/img/pause@2X.png',
    iconSize: [28,28]
});


// Load projects and set up map-panning:
// -------------------------------------
var projects = {}

function move_map_to_location_hash () {
    var project = projects[location.hash.slice(1)];
    var centre = L.latLng(project.centre[0], project.centre[1]);
    map.panTo(centre, 11);
};

// Get projects and update map location once loaded:
$.getJSON('/locations.json', function (json) {
    $.each(json.locations, function (index, project) {
        var project_link = '<li><a href="#' + project.name + '">' + project.human_readable_name + '</a></li>';
        $('#locations').append(project_link);
        projects[project.name] = project;
    });
    move_map_to_location_hash();
});

// Update map location when location-hash changes:
window.onhashchange = move_map_to_location_hash;

