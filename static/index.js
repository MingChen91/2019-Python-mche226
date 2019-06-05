// $(document).ready(function(){
//     $('#submit').on('click', function(){
//         alert("Button Clicked!")
//     });
// });
// change the ip if needed
const ip = "http://192.168.1.75:1234";

//submits the form details to server to get new API key and log in
function submit_click(){
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value
    let data = {'username' : username,'password' : password}
    $.ajax({
        method: 'POST',
        url: ip+'/signin',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(data){
        let data_json = JSON.parse(data)
        if (data_json.response == "ok"){
            window.location.href = "http://192.168.1.75:1234/main";
        } else {
            alert('Invalid username / password combo')
        }
    });
};

// signout
function sign_out(){
    $.ajax({
        method: 'GET',
        url: ip+'/signout',
    }).done(function(data){
        alert("Come back again soon =)")
        window.location.href = "http://192.168.1.75:1234/"
    });
    
}