uiblockcss = { border: 'none', 
               padding: '15px', 
               backgroundColor: '#000', 
               opacity: .5, 
               color: '#fff' } 


$(function() {
    $('.wait').click(function() { 
            $.blockUI({message: "Now searching. This operation could take a while...",
                       css: uiblockcss})
        });

    $('#button-all-news').click(function() {
        $.blockUI({message: "Now searching. This operation could take a while...",
                   css: uiblockcss})
        $('#form-all-news').submit()
    });

    if($('#form-all-news > input').size() == 0) {
        $('#form-all-news').remove()
        $('#button-all-news').remove()
    }
});
