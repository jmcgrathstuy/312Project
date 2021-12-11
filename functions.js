socket = new WebSocket('ws://' + window.location.host + '/websocket');
socket.onmessage = addMessage

function dmStart(){
    //make form pop up  
    dmPrompt(username);

}


function dmPrompt(username) {
    let message = prompt("Send DM", "");
    if (!(message == null || message == "")) {
        socket.send(JSON.stringify({'username': username, 'message': message, 'type':'dm'}));
    }
}

function upvotePrompt(id){
    socket.send(JSON.stringify({'type':'vote', 'id':id}))
}

function addMessage(message) {
    //Gonna need to treat updoots different!!
    //???
    const chatMessage = JSON.parse(message.data);
    console.log(chatMessage)
    if(chatMessage.type == 'vote'){
        console.log(chatMessage)

        var bttn = document.getElementById(chatMessage.id.toString());
        bttn.value = chatMessage.upvotes.toString()

    }
    else if(chatMessage.type == 'dm'){
        alert(chatMessage.username + ': ' +chatMessage.message)
    }


 }
 