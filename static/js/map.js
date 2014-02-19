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
    .setView([55.947, -3.2], 14)
    .addLayer(L.mapbox.tileLayer('socialsoundsproject.h9hbe4l4', {
        detectRetina: true
    }));


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


$.getJSON('/sounds.json', function (json) {
    $.each(json.sounds, function (index, sound) {

        var sound_marker = L.marker([sound.latitude, sound.longitude], {icon: playIcon}).addTo(map);

        var popup_str = '<b>' + sound.human_readable_location + '</b>'
        if (sound.description) {
            popup_str = popup_str + '<br/>' + sound.description;
        }
        popup_str = popup_str + '<br/><small>' + sound.datetime + '</small>';
        sound_marker.bindPopup(popup_str);

        sound_marker.on('click', function (event) {

            if (sound_marker.sound) {
                sound_marker.sound.togglePause();

                if (sound_marker.sound.paused) {
                    sound_marker.setIcon(playIcon);
                } else {
                    sound_marker.setIcon(pauseIcon);
                }

            } else {
                SC.stream("/tracks/" + sound.soundcloud_id, function(sound){
                    sound_marker.sound = sound;
                    loopSound(sound_marker.sound);
                    sound_marker.setIcon(pauseIcon);
                })
            }
        });
    })
});
