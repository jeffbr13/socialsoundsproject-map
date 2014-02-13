// Soundcloud
SC.initialize({
  client_id: '0183346830552e3721f88daf4c6a8f8d'
});

function loopSound(sound) {
  sound.play({
    onfinish: function() {
      loopSound(sound);
    }
  });
}

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


var location1 = L.marker([55.946, -3.186], {icon: soundIcon}).addTo(map);
location1.bindPopup('<b>Nicholson Street</b> Jan 27 2014,16:07 - <i>Traffic</i>')

// // Popups don't get added to the DOM, it would seem...
// location1Button = $('<button/>', {
//     id: 'location1Button',
//     class: 'btn btn-default',
//     text: 'location1Button'
// }).appendTo('#location1ButtonWrapper')

// var location2 = L.marker([55.94, -3.18], {icon: soundIcon}).addTo(map);
// location2.bindPopup('<b>Old College</b> Jan 27 2014, 15:28 - <i>Lecture</i>')


// L.tileLayer('http://{s}.tile.cloudmade.com/57b268dd39b742c0962bb4ebd0efa432/997/256/{z}/{x}/{y}.png', {
//     attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
//     maxZoom: 18
// }).addTo(map);


// // adding shapes
// var marker = L.marker([55.95, -3.2], {icon: soundIcon}).addTo(map);
// marker.bindPopup("<b>Hello, world!</b> I am a popup.").openPopup();

// var circle = L.circle([51.508, -0.11], 500, {
// 	color: 'red',
// 	fillColor: '#f03',
// 	fillOpacity: 0.5
// }).addTo(map);
// circle.bindPopup("I am a circle");

// var polygon = L.polygon([
// 	[51.509, -0.08],
// 	[51.503, -0.06],
// 	[51.510, -0.047]
// ]).addTo(map);
// polygon.bindPopup("I am a triangle!");


// // Popup as a Layer
// var popup = L.popup()
// 	// .setLatLng([51.5, -0.09])
// 	// .setContent("I am a standalone popup.")
// 	// .openOn(map);


// // Events
// function onMapClick(e) {
// 	// alert("You clicked the map at " + e.latlng);
// 	L.popup()e
// 	.setLatLng(e.latlng)
// 	.setContent("You clicked the map at " + e.latlng.toString())
// 	.openOn(map);
// }

// map.on('click', onMapClick);



// SC.get('/resolve', {url: 'http://soundcloud.com/socialsoundsproject/nicholson-street-jan-27-2014'}, function(track) {
//     alert('track id is ' + track.id)
// });


location1.on('click', function(event){
    if (location1.sound) {
        location1.sound.togglePause();
    } else {
        SC.stream("/tracks/131794424", function(sound){
            location1.sound = sound;
            loopSound(location1.sound);
        })
    }
});

location1.on('mouseover', function(event){
    // location1.togglePopup();
    location1.openPopup();
});

location1.on('mouseout', function(event){
    setTimeout(function(){
        location1.closePopup();
    }, 1000);
});
