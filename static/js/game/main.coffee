Vector3 = THREE.Vector3

game = window.GAME


NB_TANKS = 4;

chars = new Backbone.Collection

#lifeIndicator = new LifeIndicator("life_indicator");
#radar = new Radar("radar");

###
var message = $('#message');
function death () {
  message.show().text("Game Over");
  setTimeout(function() {
    message.hide();
    startSelfTank();
  }, 1000);
}
###

startSelfTank = () ->
  myChar = new Tank
  #myChar.setControls(new TankKeyboardControls(document));


addTank = () ->
  tank = new Tank
  game.addTank tank


startSelfTank()

setInterval ->
  if (game.tanks.size()<NB_TANKS)
    addTank
, 2000
game.animate();
