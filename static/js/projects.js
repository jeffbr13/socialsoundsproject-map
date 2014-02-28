function move_map_to_location () {
    var project = projects[location.hash.slice(1)];
    var centre = L.latLng(project.centre[0], project.centre[1]);
    map.panTo(centre, 11);
}

// Get projects and update map location once loaded:
var projects = {}
$.getJSON('/locations.json', function (json) {
    $.each(json.locations, function (index, project) {
        var project_link = '<li><a href="#' + project.name + '">' + project.human_readable_name + '</a></li>';
        $('#locations').append(project_link);
        projects[project.name] = project;
    });
    move_map_to_location();
});

// Update map location when location-hash changes:
window.onhashchange = move_map_to_location;
