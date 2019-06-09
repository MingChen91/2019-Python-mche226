// initial functions on load
$('document').ready(function(){
    list_users();
    report();
    get_broadcast();
});


// timed functions
const refresh_time = 10000
setInterval(list_users, refresh_time);
setInterval(report, refresh_time);
setInterval(get_broadcast,refresh_time)

// list users function - lists the users also updates the database
function list_users(){
    $.ajax({
        method: 'GET',
        url:'/list_users',
    }).done(function(data){
        let onlineusers = JSON.parse(data);
        // to get all the keys of onlineuser
        // clear the inner html
        document.getElementById("usersBar").innerHTML = '<h1 id = "status_title">User Status:</h1><ul id="status_list" >';  
        // for loops to add them in order  
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "online"){
                let onlineuser_uppercase = onlineusers[key].username.charAt(0).toUpperCase() + onlineusers[key].username.substring(1);
               document.getElementById("usersBar").innerHTML += "<li>" + onlineuser_uppercase +": Online </li>";
            }
        });
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "busy"){
                let onlineuser_uppercase = onlineusers[key].username.charAt(0).toUpperCase() + onlineusers[key].username.substring(1);
               document.getElementById("usersBar").innerHTML += "<li>" + onlineuser_uppercase +": busy </li>";
            }
        });
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "away"){
                let onlineuser_uppercase = onlineusers[key].username.charAt(0).toUpperCase() + onlineusers[key].username.substring(1);
               document.getElementById("usersBar").innerHTML += "<li>" + onlineuser_uppercase +": busy </li>";
            }
        });
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "offline"){
                let onlineuser_uppercase = onlineusers[key].username.charAt(0).toUpperCase() + onlineusers[key].username.substring(1);
               document.getElementById("usersBar").innerHTML += "<li>" + onlineuser_uppercase +": Offline </li>";
            }
        });
        document.getElementById("usersBar").innerHTML += '</ul>';  
   });
}

// reports status to server
function report(){
    let data = {'status':'online'}
    $.ajax({
        method: 'POST',
        url: '/report',
        data : JSON.stringify(data),
        contentType:'application/json',
    })
};

// private message
function private_message(){
    let message = "another message";
    let target_username = 'tche614';
    let data = {'message':message, 'target_username':target_username}
    
    $.ajax({
        method: 'POST',
        url: '/private_message',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(data){
        alert('pm finished')
   });
}

// broadcast
function broadcast(){
    let message = document.getElementById("broadcast_message").value;
    let data = {'message':message}
    $.ajax({
        method: 'POST',
        url: '/broadcast',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(data){
        alert('broadcast finished')
   });
}

function get_broadcast(){
    $.ajax({
        method: 'GET',
        url:'/get_broadcast',
    }).done(function(data){
        var broadcast_messages = JSON.parse(data);
        // Reference : https://www.encodedna.com/javascript/populate-json-data-to-html-table-using-javascript.htm
        // Extract value for html header
        var col = []
        for (var i = 0; i < broadcast_messages.length; i++){
            for (var key in broadcast_messages[i]){
                if (col.indexOf(key)===-1){
                    col.push(key);
                }
            }
        }

        // Create dynamic table
        var table = document.createElement('table');
        table.className = 'broadcast_table';
        // create html table header row using extracted headers
        var tr = table.insertRow(-1); //table row

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // TABLE HEADER.
            th.innerHTML = col[i];
            tr.appendChild(th);
        }
        
        // add json data to table 
        for (var i = 0; i < broadcast_messages.length; i++) {
            tr = table.insertRow(-1);
            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = broadcast_messages[i][col[j]];
            }
        }

        // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
        var divContainer = document.getElementById("broadcast_div");
        divContainer.innerHTML = "";
        divContainer.appendChild(table);
    })
}
