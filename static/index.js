//submits the form details to server to get new API key and log in
function submit_click(){
    let username = document.getElementById("username").value
    let password = document.getElementById("password").value
    let priv_password= document.getElementById("priv_password").value
    let data = {'username' : username,'password' : password,'priv_password' : priv_password}
    
    $.ajax({
        method: 'POST',
        url: '/signin',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(response){

        let data_json = JSON.parse(response)
        if (data_json.response == "ok"){
            window.location.href = "/main";
            // alert('success')
        } else {
            if (data_json.response == "Can't load private data"){
                alert("Couldn't load private data");
            } else {
                alert("Couldn't authenticate.");
            }
        }
    });
};


// creating new private data
function new_private_data(){
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;
    let priv_password = document.getElementById('new_priv_password').value;

    let data = {'username':username,'password':password,'priv_password':priv_password}
    $.ajax({
        method: 'POST',
        url: '/create_new_private_data',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(data){
        alert(data)
   });

};


