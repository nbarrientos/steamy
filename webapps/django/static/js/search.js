uiblockcss = { border: 'none', 
               padding: '15px', 
               backgroundColor: '#000', 
               opacity: .5, 
               color: '#fff' } 


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

    $('#search-submit').click(function() {
            if (!$('#id_tojson').is(':checked')) {
                $.blockUI({message: "Now searching. This operation could take a while...",
                           css: uiblockcss})
            }
        });

    $('#sparql-submit').click(function() { 
            if (!$('#id_tojson_sparql').is(':checked')) {
                $.blockUI({message: "Executing query. This operation could take a while...",
                           css: uiblockcss})
            }
        });
});
