// author Joe Tan & Jonathan Reynolds
var map;
var current_location;
var currentUsername;
var marker;
var userMarkers = {};

/**
 * Run any methods needed to initialize the DOM
 */
function initialize() {
  var styles = [
    {
        "featureType": "water",
        "stylers": [
            {
                "color": "#19a0d8"
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "color": "#ffffff"
            },
            {
                "weight": 6
            }
        ]
    },
    {
        "featureType": "administrative",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "color": "#e85113"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -40
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.stroke",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -20
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "lightness": 100
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "lightness": -100
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "labels.icon"
    },
    {
        "featureType": "landscape",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "landscape",
        "stylers": [
            {
                "lightness": 20
            },
            {
                "color": "#efe9e4"
            }
        ]
    },
    {
        "featureType": "landscape.man_made",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "lightness": 100
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "lightness": -100
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels.text.fill",
        "stylers": [
            {
                "hue": "#11ff00"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels.text.stroke",
        "stylers": [
            {
                "lightness": 100
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels.icon",
        "stylers": [
            {
                "hue": "#4cff00"
            },
            {
                "saturation": 58
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "geometry",
        "stylers": [
            {
                "visibility": "on"
            },
            {
                "color": "#f0e4d3"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -25
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "geometry.fill",
        "stylers": [
            {
                "color": "#efe9e4"
            },
            {
                "lightness": -10
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "labels",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    }
];
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 0, lng: 0},
    zoom: 15,
    styles: styles
  });
  setUsernameStyles();
  initCenterMapButton();
  getUserLocation();
  getAllActiveUsersLatLng();
  setInterval(getAllActiveUsersLatLng, 30000);
  activateSocketIO();
}

// sets user to Active
$(window).focus(function() {
  jQuery.ajax({
    type: 'GET',
    url: "/setActive",
  });
});

// sets user to Inactive
$(window).blur(function() {
  jQuery.ajax({
    type: 'GET',
    url: "/setInactive",
  });
});

/**
 * Create and add styles to the page for the current logged-in user.
 */
function setUsernameStyles(){
  currentUsername = $('#username').html();
  var style = document.createElement('style');
  style.type = 'text/css';
  style.innerHTML = 'li.' + currentUsername + " {text-align:right; background-color: rgb(237, 132, 132)!important;}";
  document.getElementsByTagName('head')[0].appendChild(style);
}

/**
 * Takes a message and user as an argument and returns an HTML
 * representation of the message to be used on the page.
 * @param {String} msg
 *    Message sent by current user
 * @param {String} username
 *    Username of current user
 * @returns {String}
 *    HTML formatted representation of user's message.
 */
function formatChatMessage(msg, username){
  var htmlString = "";
  htmlString+= "<p class = \"username\">"+ username + "</p>";
  htmlString += "<p>" + msg + "</p>";
  return htmlString;
}//updates the users location so there isnt a static pin

/**
 * Connect to remote SocketIO client for chat handling.
 */
function activateSocketIO() {
  var socket = io.connect('http://salty-shore-2311.herokuapp.com:80')
  $('form').submit(function(){
    socket.emit('chat message', $('#m').val(), currentUsername);
    $('#m').val('');
    return false;
  });
  socket.on('chat message', function(msg, username){
    var innerHTMLofMessage = formatChatMessage(msg,username);
    $('#messages').append($('<li>').addClass(username).html(innerHTMLofMessage));
  });
  $('#messages').bind("DOMSubtreeModified",function(){
    $('#messages').stop().animate({
      scrollTop: $("#messages")[0].scrollHeight
    }, 800);
  });
}
//connects to the chat handler

/**
 * Try to initialize Google Map API's geolocation functionality.
 */
function getUserLocation() {
  if (navigator.geolocation){
    /*
     * REPLACE setInterval with HTML5 watchPosition. Should be a
     * a cleaner implementation of what we want.
     */
     var options = {
       enableHighAccuracy: true
     }
     function error(err) {
       console.warn('ERROR(' + err.code + '): ' + err.message);
     }
    navigator.geolocation.watchPosition(setLocation, error, options);
  }
  else
    document.getElementById("locationData").innerHTML = "Sorry - your browser doesn't support geolocation!";
}

/**
 * Set location on map.
 * @param {JSON} position
 *    Object containing user's position data.
 */
function setLocation(position) {

  var lat = position.coords.latitude
  var long = position.coords.longitude;
  var positionData = {lat: lat, lng: long};
  var blob = JSON.stringify(positionData);
  //If the marker has already been created
  if(marker != null){
    //update the position of the marker
    updateMarker(positionData);
  }
  else{
    //otherwise, create a new marker
    var current_location = new google.maps.LatLng(lat,long);
    createMarker(current_location);
    map.setCenter(positionData);
    //Commented out since it'll be fetched from db anyways
    //createMarker(positionData);
  }
  //POST lat and long to backend
  jQuery.ajax({
    type: 'POST',
    url: "/map",
    name: "latlng",
    data: {"json":blob},
    success:
    function(data){
      // console.log(data);
    },
    error:
    function(data){
      // console.log(data);
    }
  });
}

/**
 * Create a new marker on the map.
 * @param {JSON} latLng
 *    Object containing latitude and longitude.
 */
function createMarker(latLng) {
  var pinColor = "1aff1a";
  var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + pinColor,
    new google.maps.Size(21, 34),
    new google.maps.Point(0,0),
    new google.maps.Point(10, 34));

  marker = new google.maps.Marker({
    map: map,
    position: latLng,
    icon: pinImage,
    title: 'You'
  });
}

/**
 * Update marker's position on the map.
 * @param {JSON} latLng
 *    Object containing lat and lang properties.
 */
function updateMarker(latLng) {
  marker.setPosition(latLng);
}

/**
 * Make a GET request for Active users lat/lng data objects
 */
function getAllActiveUsersLatLng(){
  jQuery.ajax({
    type: 'GET',
    url: "/users",
    success:
    function(data){
      setUsersPositions(data.userInfoArray);
    },
    error:
    function(data){
    }
  });
}

/**
 * For each user in an array of user information objects,
 * create or update the marker for the respective user.
 * @param {Array<JSON>} userInfoArray
 *    An array of user information JSON objects
 */
function setUsersPositions(userInfoArray){
  for(var i = 0; i < userInfoArray.length; i = i + 1){
    //if the userMarkers dict already has this user
    if(userMarkers.hasOwnProperty(userInfoArray[i].username)){
      //update their marker
      updateUserMarker(userInfoArray[i]);
    }
    //otherwise, create a new marker.
    else {
      createUsersMarker(userInfoArray[i]);
    }
  }
}

function addFriend(username){
  console.log(username);
  jQuery.ajax({
    name: "username",
    type: 'POST',
    url: "/addFriend",
    data: {'username':JSON.stringify(username)},
    success: function(data){
        alert('Added ' + username + " to Friends!");
    }
  });
}

/**
 * Create marker for users other than current user.
 * @param {JSON} object
 *    JSON object containing relevant user information.
 */
function createUsersMarker(object){
  var latLng = object.latlng;
  var userId = object.user_id;
  var user_name = object.username;
  var userSubject = object.subject;
  var pinColor = "FE7569";
  var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + pinColor,
    new google.maps.Size(21, 34),
    new google.maps.Point(0,0),
    new google.maps.Point(10, 34));

  var contentString = '<div id="content">'+
    '<h4>' + user_name + '</h4>' +
    '<p>Wants to study: '+ userSubject + '.</p>' +
    '</div>' + '<div id="addFriend" class="text-center">' +
    '<button class="btn btn-primary" onclick="addFriend(\''+user_name+'\')"> Add Friend </button></div>';

  var infoWindow = new google.maps.InfoWindow({
    content: contentString
  });

  var userMarker = new google.maps.Marker({
    map: map,
    position: latLng,
    icon: pinImage,
    title: 'User: ' + username
  });

  infoWindow.open(map, userMarker);

  userMarker.addListener('click', function() {
    infoWindow.open(map, userMarker);
  });

  userMarkers[username] = {"marker": userMarker};
  console.log("Creating marker for user: " + username + "'s location.'");
  console.log(userMarkers);
}


/**
 * Update marker for users other than current user.
 * @param {JSON} object
 *    JSON object containing relevant user information.
 */
function updateUserMarker(object) {
    var latLng = object.latlng;
    var userId = object.user_id;
    var username = object.username;
    var userMarker = userMarkers[username]["marker"];
    userMarker.setPosition(latLng);
    console.log("Updating user: " + username + "'s location.'");
}

/**
 * The CenterControl adds a control to the map that recenters the map on a given location.
 * This constructor takes the control DIV as an argument.
 */
function CenterControl(controlDiv, map) {

  // Set CSS for the control border.
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = '#fff';
  controlUI.style.border = '2px solid #fff';
  controlUI.style.borderRadius = '3px';
  controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
  controlUI.style.cursor = 'pointer';
  controlUI.style.marginBottom = '22px';
  controlUI.style.textAlign = 'center';
  controlUI.title = 'Click to recenter the map';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior.
  var controlText = document.createElement('div');
  controlText.style.color = 'rgb(25,25,25)';
  controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
  controlText.style.fontSize = '16px';
  controlText.style.lineHeight = '38px';
  controlText.style.paddingLeft = '5px';
  controlText.style.paddingRight = '5px';
  controlText.innerHTML = 'Center Map';
  controlUI.appendChild(controlText);

  // Setup the click event listeners:
  controlUI.addEventListener('click', function() {
    map.setCenter(marker.getPosition());
  });

}

/**
 * Initializes the button on the map to center the map on the
 * logged in user's position.
 */
function initCenterMapButton() {

  // Create the DIV to hold the control and call the CenterControl() constructor
  // passing in this DIV.
  var centerControlDiv = document.createElement('div');
  var centerControl = new CenterControl(centerControlDiv, map);

  centerControlDiv.index = 1;
  map.controls[google.maps.ControlPosition.TOP_CENTER].push(centerControlDiv);
}

google.maps.event.addDomListener(window, 'load', initialize);
