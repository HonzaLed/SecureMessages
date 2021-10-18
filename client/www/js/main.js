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
async function getMessages(response=undefined) {
    let n = await eel.getReceivedMsgs()();
    getMsgsHandler(n);
    return n;
}
function getMsgsHandler(obj) {
    console.log("Got "+obj+" from python!");
    msgsJson = JSON.parse(obj);
}

function displayMsgs() {
    msgsDiv = document.getElementById("messages");
    removeChilds(msgsDiv);
    getMessages();
    msgsJson.messages.forEach((msg)=>{console.log("msg "+msg);});
}

console.log(getMessages());
