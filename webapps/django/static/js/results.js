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
});
