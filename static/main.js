// initial functions on load
$('document').ready(function(){
    list_users();
    report();
    get_broadcast();
    private_message_box();
});


// timed functions
const refresh_time = 10000
setInterval(list_users, refresh_time);
setInterval(report, refresh_time);
setInterval(get_broadcast,refresh_time);
setInterval(private_message_box,2000);


// list users function - lists the users also updates the database
function list_users(){
    $.ajax({
        method: 'GET',
        url:'/list_users',
    }).done(function(data){
        let onlineusers = JSON.parse(data);
        // update the status on the message box
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].username == global_target_user_name){
                document.getElementById('pm_user_status').innerHTML  = onlineusers[key].status;
            };
        });

        // to get all the keys of onlineuser
        // clear the inner html
        document.getElementById("usersBar").innerHTML = '<h1 id = "status_title">User Status:</h1><ul id="status_list" >';  
        // for loops to add them in order  
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "online"){
                document.getElementById("usersBar").innerHTML += "<li onclick = load_target_username('" + onlineusers[key].username + "')>" + onlineusers[key].username +": Online </li>";
            }
        });
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "busy"){
               document.getElementById("usersBar").innerHTML += "<li onclick = load_target_username('" + onlineusers[key].username + "')>" + onlineusers[key].username +": Busy </li>";
            }
        });
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "away"){
               document.getElementById("usersBar").innerHTML += "<li onclick = load_target_username('" + onlineusers[key].username + "')>" + onlineusers[key].username +": Away </li>";
            }
        });
        Object.keys(onlineusers).forEach(function(key){
            if (onlineusers[key].status == "offline"){
               document.getElementById("usersBar").innerHTML += "<li onclick = load_target_username('" + onlineusers[key].username + "')>" + onlineusers[key].username +": Offline </li>";
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
    let message = document.getElementById('pm_text_box').value;
    let target_username = document.getElementById("pm_user").innerHTML;
    let data = {'message':message, 'target_username':target_username}
    private_message_box();
    $.ajax({
        method: 'POST',
        url: '/private_message',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(data){
        document.getElementById('pm_text_box').value = "";
    });
}

var global_target_user_name = '';
function load_target_username(target_username){
    global_target_user_name = target_username;
    private_message_box();
}

function private_message_box(){
    // loads the private message box with a targets data
    let data = {"target_username" : global_target_user_name};
    // change the text box
    document.getElementById("pm_user").innerHTML = global_target_user_name;
    $.ajax({
        method: 'POST',
        url: '/get_private_message',
        data : JSON.stringify(data),
        contentType:'application/json'
    }).done(function(data){
       // load the table
       var private_messages = JSON.parse(data);
        // Reference : https://www.encodedna.com/javascript/populate-json-data-to-html-table-using-javascript.htm
        // Extract value for html header
        var col = []
        for (var i = 0; i < private_messages.length; i++){
            for (var key in private_messages[i]){
                if (col.indexOf(key)===-1){
                    col.push(key);
                };
            };
        };

        // Create dynamic table
        var table = document.createElement('table');
        table.className = 'private_message_table';
        // create html table header row using extracted headers
        var tr = table.insertRow(-1); //table row

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // TABLE HEADER.
            th.innerHTML = col[i];
            tr.appendChild(th);
        };
        
        // add json data to table 
        for (var i = 0; i < private_messages.length; i++) {
            tr = table.insertRow(-1);
            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = private_messages[i][col[j]];
            };
        };

        // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
        var divContainer = document.getElementById("private_message_block");
        divContainer.innerHTML = "";
        divContainer.appendChild(table);
   });
};


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
        document.getElementById('broadcast_message').value = "";
    });
};

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
                };
            };
        };

        // Create dynamic table
        var table = document.createElement('table');
        table.className = 'broadcast_table';
        // create html table header row using extracted headers
        var tr = table.insertRow(-1); //table row

        for (var i = 0; i < col.length; i++) {
            var th = document.createElement("th");      // TABLE HEADER.
            th.innerHTML = col[i];
            tr.appendChild(th);
        };
        
        // add json data to table 
        for (var i = 0; i < broadcast_messages.length; i++) {
            tr = table.insertRow(-1);
            for (var j = 0; j < col.length; j++) {
                var tabCell = tr.insertCell(-1);
                tabCell.innerHTML = broadcast_messages[i][col[j]];
            };
        };

        // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
        var divContainer = document.getElementById("broadcast_block");
        divContainer.innerHTML = "";
        divContainer.appendChild(table);
    })
}











































































































