// timed functions
setInterval(list_users, 1000);

// list users function - lists the users also updates the database
function list_users(){
    $.ajax({
        method: 'GET',
        url:'/list_users',
    }).done(function(data){
        
    });
}
