class Game extends Backbone.Model
	initialize: ->
		this.startTime = +new Date;
		
		this.effectsEnabled = true;
  
		this.boundMin = this.get("boundMin");
		this.boundMax = this.get("boundMax");

		this.ships = new Backbone.Collection
		this.bullets = new Backbone.Collection

		this.scene = new Scene
		#this.scene.fog = new THREE.Fog(0x000000, 1, 6000);

		this.camera = new PerspectiveCamera 75, WIDTH/HEIGHT, 1, 10000
		this.scene.add this.camera

		this.makeGround 100, 0x008800, 0
		this.makeLimitWalls 100, 0x008800, 10000

		this.renderer = new THREE.WebGLRenderer;
		this.renderer.setSize WIDTH, HEIGHT

		self = this


		$('#game').append(this.renderer.domElement);



class GameObj extends Backbone.Model
	update: ->

