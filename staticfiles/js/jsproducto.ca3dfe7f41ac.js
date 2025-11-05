mapboxgl.accessToken = 'pk.eyJ1IjoiZGVpZ28wMSIsImEiOiJjbTJmNW9hYTMwNXE2Mm1vbXJ4eWptY3NjIn0.mV36MUpkaaMXHZgv1_bDug';

// Obtener las coordenadas del input
const latitudeStr = document.getElementById('latitude').value.trim().replace(',', '.');
const longitudeStr = document.getElementById('longitude').value.trim().replace(',', '.');

// Convertir las coordenadas a números
const latitude = parseFloat(latitudeStr);
const longitude = parseFloat(longitudeStr);

// Verificar las coordenadas en la consola
console.log("Longitud:", longitude);
console.log("Latitud:", latitude);

// Verifica que las coordenadas sean válidas
if (isNaN(latitude) || isNaN(longitude)) {
    console.error("Las coordenadas no son válidas");
} else {
    const coordinates = [longitude, latitude];

    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/deigo01/cm2gk8sve000901pebrgx74cy',
        center: coordinates,
        zoom: 10
    });

    // Añadir marcador
    new mapboxgl.Marker()
        .setLngLat(coordinates)
        .addTo(map);
}