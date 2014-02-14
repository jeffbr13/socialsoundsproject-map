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
