// Load and display SoundCloud sounds:
// -----------------------------------

SC.initialize({
  client_id: '0183346830552e3721f88daf4c6a8f8d'
});

function loopSound(sound) {
  sound.play({
    onfinish: function() {
      loopSound(sound);
    }
  });
};

$.getJSON('/sounds.json', function (json) {
    $.each(json.sounds, function (index, sound) {

        var sound_marker = L.marker([sound.latitude, sound.longitude], {icon: playIcon}).addTo(map);

        var popup_str = '<b>' + sound.human_readable_location + '</b>'
        if (sound.description) {
            popup_str = popup_str + '<br/>' + sound.description;
        };
        sound_marker.bindPopup(popup_str);

        sound_marker.on('click', function (event) {
            if (sound_marker.sound) {
                sound_marker.sound.togglePause();
                if (sound_marker.sound.paused) {
                    // sound paused
                    sound_marker.setIcon(playIcon);
                    sound_marker.setOpacity(0.75);
                } else {
                    // sound playing
                    sound_marker.setIcon(pauseIcon);
                    sound_marker.setOpacity(1.0);
                }
            } else {
                SC.stream("/tracks/" + sound.soundcloud_id, function(sound){
                    sound_marker.sound = sound;
                    loopSound(sound_marker.sound);
                    // sound playing
                    sound_marker.setIcon(pauseIcon);
                });
            };
        });

        sound_marker.on('mouseover', function (event) {
            sound_marker.openPopup();
        });

        sound_marker.on('mouseout', function (event) {
            sound_marker.closePopup();
        });
    });
});
