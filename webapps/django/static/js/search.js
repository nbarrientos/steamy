$(function() {
    $("#accordion").accordion({ header: "h3", autoHeight: false});
    $("#tabs").tabs();

    $('#id_exactmatch').click(function() {
        if ($('#id_exactmatch').is(':checked')) {
            if ($('#id_searchtype_2').is(':checked')) {
                $("#id_searchtype_2").removeAttr("checked");
                $("#id_searchtype_0").attr("checked", "checked");
            }
            $("#id_searchtype_2").attr("disabled", "disabled");
        } else {
            $("#id_searchtype_2").removeAttr("disabled");
        } 
    });
});
