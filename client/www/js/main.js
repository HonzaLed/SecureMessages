function range(end) {
    return Array(end).keys()
}
function removeChilds(node) {
    try {
        for (const i of range(node.children.length)) {
            node.removeChild(node.children.item(i));
        }
        return true;
    } catch {
        return false;
    }
}

var msgsJson;
var messages = {"users":[]};
async function getMessages(response=undefined) {
    let n = await eel.getReceivedMsgs()();
    getMsgsHandler(n);
    return n;
}
function getMsgsHandler(obj) {
    console.log("Got "+obj+" from python!");
    msgsJson = JSON.parse(obj);
    msgsJson.messages.forEach( (msg) => {
        var nickname = msg.senderNickname;
        var user = messages.users.find( (usr)=>{if (usr.nickname == nickname){return true}});
        if (typeof(user) != "undefined") {
            user.messages.push(msg);
        } else {
            messages.users.push( {"nickname":nickname, "messages":[msg]} )
        }
    });
}

function displayMsgs() {
    msgsDiv = document.getElementById("messages");
    removeChilds(msgsDiv);
    getMessages();
    msgsJson.messages.forEach((msg)=>{console.log("msg "+msg);});
}

function PrintMsgsToConsole() {
    messages.users.forEach((usr) => {
        console.log("Printing messages from "+usr.nickname);
        usr.messages.forEach((msg) => {
            console.log(msg.senderNickname+": "+msg.msg);
        });
    });
}

console.log(getMessages());
