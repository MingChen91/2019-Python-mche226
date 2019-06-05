// $(document).ready(function(){
//     $('#submit').on('click', function(){
//         alert("Button Clicked!")
//     });
// });
// change the ip if needed
const ip = "http://192.168.1.75:1234";

function submit_click(){
    // alert("he");
    // let username = document.getElementById("username").value
    // let password = document.getElementById("password").value

    $.ajax({
        method: 'POST',
        url: ip+'/signin',
        dataType:'json'
    }).done(function(data){
        console.log(data);
        if (data.response == "ok"){
            window.location.href = "http://192.168.1.75:1234/main";
        } else {
            alert('Invalid username / password combo')
        }
    });
    // console.log(username + password )
};