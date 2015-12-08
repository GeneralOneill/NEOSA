$(document).ready(function(){
  var selected_Times = [];
;



//schedule handler implemented in profile page and schedule page

  var isMouseDown = false;
  $("#our_table td").mousedown(function () {
    isMouseDown = true;
    //check to see if the object is going from selected to unselected
    if ($(this).hasClass( "highlighted" )){

      //locates index of the element in the array
      var index = selected_Times.indexOf($(this).html());
      selected_Times.splice(index, 1);
    }
    else {
      selected_Times.push($(this).html())
    }
    $(this).toggleClass("highlighted");
  })
  .mouseup(function(){
    //turns mouse down off
    isMouseDown=false;
  })
  .mouseover(function () {
      if (isMouseDown) {
        if ($(this).hasClass( "highlighted" )){

          //locates index of the element in the array
          var index = selected_Times.indexOf($(this).html());
          selected_Times.splice(index, 1);
        }
        else {
          selected_Times.push($(this).html())
        }
        $(this).toggleClass("highlighted");
      }
    });

  $('#find_button_id').click(function(){
    //sending to information to a place should be placed here
    var times = [];
    for (var i = 0; i < selected_Times.length; i++) {
      //gets the integer value of the time
      var timeInt = parseInt(selected_Times[i].substring(0, selected_Times[i].length-3));

      //accounts for 12AM and 12PM-- turning it to the "0th hour" (correct format for DateTime objects)
      timeInt = timeInt % 12;

      //boolean value to tell if the time is AM or PM
      var isAM = selected_Times[i].substring(selected_Times[i].length-2) === "am";

      //Adds 12 to PM hours to get military time
      if(!isAM){
        timeInt = timeInt + 12;
      }

      //the DateTime object :D
      var date = new Date();
      //sets the hours based on our Time int, and sets minutes and seconds to 0.
      date.setHours(timeInt, 0,0);
      //convert it to UTCString so python can interpret it... -_-
      times.push(date.toUTCString());
    }


      //POST schedule to backend
      jQuery.ajax({
        type: 'POST',
        url: "/schedule",
        name: "schedule",
        data: JSON.stringify({"schedule": times}),
        success:
        function(data){
          console.log("Data:"+data);
          location.reload();
        },
        error:
        function(data){
          console.log("err");
          // console.log(data);
        }
      });
  })


});
