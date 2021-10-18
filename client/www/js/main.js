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


function PrintMsgsToConsole() {
    messages.users.forEach((usr) => {
        console.log("Printing messages from "+usr.nickname);
        usr.messages.forEach((msg) => {
            console.log(msg.senderNickname+": "+msg.msg);
        });
    });
}

function msgToNode(msg, sender) {
    if (sender == "me") {
        var frag = document.createRange().createContextualFragment(
            '<li class="clearfix"><div class="message my-message float-right">'+msg+'</div></li>'
        );
        console.log(frag);
    } else {
        var frag = document.createRange().createContextualFragment(
            '<li class="clearfix"><div class="message other-message ">'+msg+'</div></li>'
        );
        console.log(frag);
    }
    return frag
}

function addMessage(msg, sender) {
    var messages = document.getElementById("messages");
    messages.appendChild(msgToNode(msg, sender));
}

function Autoscroll() {
    (function() {
        var intervalObj = null;
        var retry = 0;
        var clickHandler = function() { 
            console.log("Clicked; stopping autoscroll");
            clearInterval(intervalObj);
            document.body.removeEventListener("click", clickHandler);
        }
        function scrollDown() { 
            var scrollHeight = document.body.scrollHeight,
                scrollTop = document.body.scrollTop,
                innerHeight = window.innerHeight,
                difference = (scrollHeight - scrollTop) - innerHeight

            if (difference > 0) { 
                window.scrollBy(0, difference);
                if (retry > 0) { 
                    retry = 0;
                }
                console.log("scrolling down more");
            } else {
                if (retry >= 3) {
                    console.log("reached bottom of page; stopping");
                    clearInterval(intervalObj);
                    document.body.removeEventListener("click", clickHandler);
                } else {
                    console.log("[apparenty] hit bottom of page; retrying: " + (retry + 1));
                    retry++;
                }
            }
        }
        document.body.addEventListener("click", clickHandler);
        intervalObj = setInterval(scrollDown, 1000);
    })();
}

console.log(getMessages());
