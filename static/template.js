// signout
function sign_out(){
    $.ajax({
        method: 'GET',
        url:'/signout',
    }).done(function(data){
        alert("Come back again soon =)")
        window.location.href = "/main";
    });
}
