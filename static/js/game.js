var camera, scene, renderer;
var geometry, material, mesh, skin, dae, pointLight, particleLight;

var loader = new THREE.ColladaLoader();
loader.options.convertUpAxis = true;
loader.load( '/static/js/models/Tiny_SpaceShip_by_CoyHot.dae', function ( collada ) {

        dae = collada.scene;
        skin = collada.skins[ 0 ];

        dae.scale.x = dae.scale.y = dae.scale.z = 0.5;
        dae.updateMatrix();

        init();
        animate();

} );

function init() {

        camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 1, 10000 );
        camera.position.z = 1000;

        scene = new THREE.Scene();

        geometry = new THREE.CubeGeometry( 200, 200, 200 );
        material = new THREE.MeshLambertMaterial( { color: 0xFFFFFF} );

        mesh = new THREE.Mesh( geometry, material );
        //scene.add( mesh );

        scene.add( dae );
        particleLight = new THREE.Mesh( new THREE.SphereGeometry( 4, 8, 8 ), new THREE.MeshBasicMaterial( { color: 0xffffff } ) );
        scene.add( particleLight );

        // Lights

        //scene.add( new THREE.AmbientLight( 0xcccccc ) );

        var directionalLight = new THREE.DirectionalLight(/*Math.random() * 0xffffff*/0xeeeeee );
        directionalLight.position.x = Math.random() - 0.5;
        directionalLight.position.y = Math.random() - 0.5;
        directionalLight.position.z = Math.random() - 0.5;
        directionalLight.position.normalize();
        //scene.add( directionalLight );

        pointLight = new THREE.PointLight( 0xffffff, 4 );
        pointLight.position = particleLight.position;
        //scene.add( pointLight );

        // add to the scene
        //scene.add(pointLight);

        renderer = new THREE.CanvasRenderer();
        renderer.setSize( window.innerWidth, window.innerHeight );

        document.body.appendChild( renderer.domElement );

}

var t = 0;
var clock = new THREE.Clock();

function animate() {

        var delta = clock.getDelta();

        requestAnimationFrame( animate );

        if ( t > 1 ) t = 0;

        if ( skin ) {

                // guess this can be done smarter...

                // (Indeed, there are way more frames than needed and interpolation is not used at all
                //  could be something like - one morph per each skinning pose keyframe, or even less,
                //  animation could be resampled, morphing interpolation handles sparse keyframes quite well.
                //  Simple animation cycles like this look ok with 10-15 frames instead of 100 ;)

                for ( var i = 0; i < skin.morphTargetInfluences.length; i++ ) {

                        skin.morphTargetInfluences[ i ] = 0;

                }

                skin.morphTargetInfluences[ Math.floor( t * 30 ) ] = 1;

                t += delta;

        }

        var timer = Date.now() * 0.0005;

        camera.position.x = Math.cos( timer ) * 10;
        camera.position.y = 2;
        camera.position.z = Math.sin( timer ) * 10;

        camera.lookAt( scene.position );

        particleLight.position.x = Math.sin( timer * 4 ) * 3009;
        particleLight.position.y = Math.cos( timer * 5 ) * 4000;
        particleLight.position.z = Math.cos( timer * 4 ) * 3009;
        renderer.render( scene, camera );

}