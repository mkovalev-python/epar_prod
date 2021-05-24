/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 15.07.14
 * Time: 16:18
 */
var iOS = /iPad|iPhone|iPod/.test(navigator.platform);

if (!iOS) {
    var sound = new Howl({
      urls: ['/static/audio/puck.mp3', '/static/audio/puck.ogg', '/static/audio/puck.wav'],
      autoplay: false,
      loop: false,
      volume: 1,
      iOSAutoEnable: false,
      onend: function() {
        console.log('Finished!');
      }
    });
    var knock = function(){
        return sound.play();
    };
}
