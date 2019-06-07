//submits the form details to server to get new API key and log in
function submit_click(){
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value
    let data = {'username' : username,'password' : password}
    
    $.ajax({
        method: 'POST',
        url: '/signin',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(response){
        console.log(response)
        let data_json = JSON.parse(response)
        if (data_json.response == "ok"){
            window.location.href = "/main";
            // alert('success')
        } else {
            alert('Invalid username / password combo')
        }
    });
};

// signout
function sign_out(){
    $.ajax({
        method: 'GET',
        url:'/signout',
    }).done(function(data){
        console.log(data)
        alert("Come back again soon =)")
        window.location.href = ip
    });
    
}