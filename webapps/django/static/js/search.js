$(document).ready(function(){
   
    $("#filters").hide();

    $("#togglefilters").click(function () {
        if ($('#filters').is(":hidden")) {
            $('#toggleiconURI').attr({src: "/debian/static/images/arrow-open.png"})
        }
        else {
            $('#toggleiconURI').attr({src: "/debian/static/images/arrow-closed.png"})
        }
        $("#filters").toggle("slow");
    });    

  });
