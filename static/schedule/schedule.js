$(document).ready(function() {
  var $calendar = $('#calendar');
  $('#calendar').weekCalendar({
    data: eventData,

    timeslotsPerHour: 4,
    allowCalEventOverlap: true,
    overlapEventsSeparate: true,
    totalEventsWidthPercentInOneColumn : 100,
    
    
    height: function($calendar) {
      return $(window).height() - $('h1').outerHeight(true);
    },

    eventRender: function(calEvent, $event) {
      if (calEvent.end.getTime() < new Date().getTime() || (!calEvent.modifiable)) {
        $event.css('backgroundColor', '#aaa');
        $event.find('.time').css({
          backgroundColor: '#999',
          border:'1px solid #888'
        });
      }
    },
    
    eventNew: function(calEvent, $event) {
      var $dialogContent = $("#event_edit_container");
      prepareFields($dialogContent);
      var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
      var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
      var titleField = $dialogContent.find("input[name='title']");
      var bodyField = $dialogContent.find("textarea[name='body']");
      
      //the following fields appear only to the professor
      var courseField = $dialogContent.find("select[name='course']");
      var typeField = $dialogContent.find("select[name='type']");
      var addToOtherWeeks = $dialogContent.find("input[name='copy']");
      

      var courseLabel = $dialogContent.find("#courseLabel");
      var copyLabel = $dialogContent.find("#copyLabel");
      
      courseLabel.hide();
      copyLabel.hide();
      
      typeField.change(function(){
          if (typeField.val() === '0'){ // personal appointment
            courseLabel.hide(400);
            copyLabel.hide(400);
          }else{ // course appointment
            courseLabel.show(400);
            copyLabel.show(400);
          }
          
      });

      

      $dialogContent.dialog({
          modal: true,
          title: "New Appointment",
          
          close: function() {
             $dialogContent.dialog("destroy");
             $dialogContent.hide();
             $('#calendar').weekCalendar("removeUnsavedEvents");
          },
          
          buttons: {
             save : function() {
                calEvent.id = id;
                calEvent.start = new Date(startField.val());
                calEvent.end = new Date(endField.val());
                calEvent.title = titleField.val();
                calEvent.body = bodyField.val();
                
                $calendar.weekCalendar("removeUnsavedEvents");
                $calendar.weekCalendar("updateEvent", calEvent);
                $dialogContent.dialog("close");
                // if the user is not a professor, or if the user is a professor and he/she wants to add a personal appointment
                if( courseField.val() === undefined || typeField.val() === undefined || typeField.val() === "0"){
                  $.ajax({
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                    type:"POST",
                    url:"add_personal_appointment",
                    data: {
                      'title': titleField.val(),
                      'body': bodyField.val(), 
                      'start': new Date(startField.val()), 
                      'end': new Date(endField.val()),
                    },
                    success: function(){
                      //alert("Appointment added successfully"); -- show the success element
                      id += 1;

                      eventData.events.push({
                        'id' : calEvent.id,
                        'title': titleField.val(),
                        'body': bodyField.val(), 
                        'start': new Date(startField.val()), 
                        'end': new Date(endField.val()),
                        'type':'Personal',
                        'modifiable' :true,
                      });

                      $calendar.weekCalendar("refresh");
                    }

                  });
                }
                else{ // the user is a professor
                  $.ajax({
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                    type:"POST",
                    url:"add_course_appointment",
                    data: {
                      'title': titleField.val(),
                      'body': bodyField.val(), 
                      'start': new Date(startField.val()), 
                      'end': new Date(endField.val()),
                      'courseName': courseField.val(),
                      'copy': addToOtherWeeks.is(":checked"),
                    },
                    success: function(){
                      //alert("Appointment added successfully");
                      id += 1;

                      eventData.events.push({
                        'id' : calEvent.id,
                        'title': titleField.val(),
                        'body': bodyField.val(), 
                        'start': new Date(startField.val()), 
                        'end': new Date(endField.val()),
                        'courseName': courseField.val(),
                        'type':'Course', 
                        'modifiable': true,
                      });

                      $calendar.weekCalendar("refresh");
                    }

                  });
                }
              },
                
              cancel : function() {
                $calendar.weekCalendar("removeUnsavedEvents");
                $dialogContent.dialog("destroy");
             }
          }
      }).show();

      var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
      var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
      $dialogContent.find(".date_holder").text($calendar.weekCalendar("formatDate", calEvent.start));
      setupStartAndEndTimeFields(startField, endField, calEvent, $calendar.weekCalendar("getTimeslotTimes", calEvent.start));
      setupCourseFields(courses,calEvent,courseField);
    },

    eventDrop: function(calEvent, $event) {
      if (calEvent.readOnly || !calEvent.modifiable) {
          return;
       }
    },

    eventResize: function(calEvent, $event) {
      if (calEvent.readOnly || !calEvent.modifiable) {
          return;
       }
    },

    // to modify existing calEvents (or remove them)
    eventClick: function(calEvent, $event) {
      
      if (calEvent.readOnly || !calEvent.modifiable) {
          return;
       }
    
       var $dialogContent = $("#event_edit_container");
       prepareFields($dialogContent);
       var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
       var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
       var titleField = $dialogContent.find("input[name='title']").val(calEvent.title);
       var bodyField = $dialogContent.find("textarea[name='body']").val(calEvent.body);

       var courseField = $dialogContent.find("select[name='course']");

       $dialogContent.dialog({
          modal: true,
          title: "Edit",
          close: function() {
             $dialogContent.dialog("destroy");
             $dialogContent.hide();
             $('#calendar').weekCalendar("removeUnsavedEvents");
          },
          buttons: {
            save : function() {
                calEvent.start = new Date(startField.val());
                calEvent.end = new Date(endField.val());
                calEvent.title = titleField.val();
                calEvent.body = bodyField.val();
                
                if(calEvent.type === 'Course' && calEvent.modifiable){
                  $.ajax({
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                    type:"POST",
                    url:"edit_course_appointment",
                    data: {
                      'id' : calEvent.id,
                      'title': titleField.val(),
                      'body': bodyField.val(), 
                      'start': new Date(startField.val()), 
                      'end': new Date(endField.val()),
                      'courseName' : calEvent.courseName,
                    },
                    success: function(){
                      //alert("Successfuly edited event");
                    }
                  });

                  $calendar.weekCalendar("updateEvent", calEvent);
                  $calendar.weekCalendar("refresh");
                  $dialogContent.dialog("close");
                }else if(calEvent.type === 'Personal'){
                    $.ajax({
                      headers: { "X-CSRFToken": getCookie("csrftoken") },
                      type:"POST",
                      url:"edit_personal_appointment",
                      data: {
                        'id' : calEvent.id,
                        'title': titleField.val(),
                        'body': bodyField.val(), 
                        'start': new Date(startField.val()), 
                        'end': new Date(endField.val()),
                      },
                      success: function(){
                        //alert("Successfuly edited event");
                      }
                    });

                  $calendar.weekCalendar("updateEvent", calEvent);
                  $calendar.weekCalendar("refresh");
                  $dialogContent.dialog("close");
                }      

             },

            "delete" : function() {
                
                $calendar.weekCalendar("removeEvent", calEvent.id);
                $dialogContent.dialog("destroy");
                
                if(calEvent.type === 'Personal' && calEvent.modifiable){
                  $.ajax({
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                    type:"POST",
                    url:"remove_personal_appointment",
                    data: {
                      'id' : calEvent.id,
                    },
                    success: function(){
                      //alert("Successfuly removed event");
                      if(calEvent.id === id){
                        id -= 1;
                      }

                      for(var i = 0 ; i < eventData.events.length; i++){
                        var e = eventData.events[i];
                        if(e.id === calEvent.id){
                          eventData.events.splice(i,1);
                        }
                      }

                      data:eventData;

                    }
                  });
                }else if(calEvent.type === 'Course' && calEvent.modifiable){
                  $.ajax({
                    headers: { "X-CSRFToken": getCookie("csrftoken") },
                    type:"POST",
                    url:"remove_course_appointment",
                    data: {
                      'id' : calEvent.id,
                      'courseName': calEvent.courseName,
                    },
                    success: function(){
                      //alert("Successfuly removed event");
                      if(calEvent.id === id){
                        id -= 1;
                      }

                      for(var i = 0 ; i < eventData.events.length; i++){
                        var e = eventData.events[i];
                        if(e.id === calEvent.id){
                          eventData.events.splice(i,1);
                        }
                      }

                      data:eventData;

                    }
                  });
                }
             },
             
            cancel : function() {
                $dialogContent.dialog("close");
             }
          }
       }).show();

       var startField = $dialogContent.find("select[name='start']").val(calEvent.start);
       var endField = $dialogContent.find("select[name='end']").val(calEvent.end);
       $dialogContent.find(".date_holder").text($calendar.weekCalendar("formatDate", calEvent.start));
       setupStartAndEndTimeFields(startField, endField, calEvent, $calendar.weekCalendar("getTimeslotTimes", calEvent.start));
       setupCourseFields(courses,calEvent,courseField);
    },

    eventMouseover: function(calEvent, $event) {
      displayMessage('<strong>Mouseover Event</strong><br/>Start: ' + calEvent.start + '<br/>End: ' + calEvent.end);
    },

    eventMouseout: function(calEvent, $event) {
      displayMessage('<strong>Mouseout Event</strong><br/>Start: ' + calEvent.start + '<br/>End: ' + calEvent.end);
    },

    noEvents: function() {
      displayMessage('There are no events for this week. YAY!');
    }

  });

function displayMessage(message) {
  $('#message').html(message).fadeIn();
}

function prepareFields($dialogContent) {
  $dialogContent.find("input").val("");
  $dialogContent.find("textarea").val("");
  $dialogContent.find("select[name='course']").empty();
}

function getCookie(c_name){
    if (document.cookie.length > 0)
    {
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1)
        {
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
 }


function setupStartAndEndTimeFields($startTimeField, $endTimeField, calEvent, timeslotTimes) {
  for (var i = 0; i < timeslotTimes.length; i++) {
    var startTime = timeslotTimes[i].start;
    var endTime = timeslotTimes[i].end;
    var startSelected = "";
    if (startTime.getTime() === calEvent.start.getTime()) {
      startSelected = "selected=\"selected\"";
    }
    var endSelected = "";
    if (endTime.getTime() === calEvent.end.getTime()) {
      endSelected = "selected=\"selected\"";
    }
    $startTimeField.append("<option value=\"" + startTime + "\" " + startSelected + ">" + timeslotTimes[i].startFormatted + "</option>");
    $endTimeField.append("<option value=\"" + endTime + "\" " + endSelected + ">" + timeslotTimes[i].endFormatted + "</option>");

  }
  
  $endTimeOptions = $endTimeField.find("option");
  $startTimeField.trigger("change");
}

function setupCourseFields(professorCourseList, calEvent, $courseField){
  for(var i=0 ; i < professorCourseList.length ; i++){
    var courseName = professorCourseList[i];
    var courseSelected = "";
    if(calEvent.courseName === courseName){
      courseSelected = "selected = \"selected\"";
    }
    $courseField.append("<option value=\"\">Select Course</option>")
    $courseField.append("<option value=\"" + courseName + "\" " + courseSelected + "\">" + courseName +"</option>");

  }
  $courseField.trigger("change");
}

var $endTimeField = $("select[name='end']");
var $endTimeOptions = $endTimeField.find("option");

//reduces the end time options to be only after the start time options.
$("select[name='start']").change(function() {
  var startTime = $(this).find(":selected").val();
  var currentEndTime = $endTimeField.find("option:selected").val();
  $endTimeField.html(
        $endTimeOptions.filter(function() {
           return startTime < $(this).val();
        })
        );

  var endTimeSelected = false;
  $endTimeField.find("option").each(function() {
     if ($(this).val() === currentEndTime) {
        $(this).attr("selected", "selected");
        endTimeSelected = true;
        return false;
     }
  });

  if (!endTimeSelected) {
     //automatically select an end date 2 slots away.
     $endTimeField.find("option:eq(1)").attr("selected", "selected");
  }

});



});