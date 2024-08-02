
function CustomAlert() {
    this.alert = function(message, title, url) {
        if (!document.getElementById('dialogoverlay')) {
            document.body.innerHTML += `
                <div id="maindialog">
                    <div id="dialogoverlay"></div>
                    <div id="dialogbox" class="slit-in-vertical">
                        <div>
                            <div id="dialogboxhead"></div>
                            <div id="dialogboxbody"></div>
                            <div id="dialogboxfoot"></div>
                        </div>
                    </div>
                </div>`;
        }

        let dialogoverlay = document.getElementById('dialogoverlay');
        let dialogbox = document.getElementById('dialogbox');
        let maindialog = document.getElementById('maindialog');
        
        dialogoverlay.style.height = window.innerHeight + "px";
        
        dialogoverlay.style.display = "block";
        dialogbox.style.display = "block";
        maindialog.style.display = "flex";
        
        let dialogboxhead = document.getElementById('dialogboxhead');
        let dialogboxbody = document.getElementById('dialogboxbody');
        let dialogboxfoot = document.getElementById('dialogboxfoot');
        
        if (typeof title === 'undefined') {
            dialogboxhead.style.display = 'none';
        } else {
            dialogboxhead.innerHTML = '<i class="fa fa-exclamation-circle" aria-hidden="true"></i> ' + title;
        }
        dialogboxbody.innerHTML = message;
        dialogboxfoot.innerHTML = `
            <button class="pure-material-button-contained" onclick="customAlert.ok('${url}')">OK</button>
            <button class="pure-material-button-contained" onclick="customAlert.cancel()">Cancel</button>`;
    };
    
    this.ok = function(url) {
        document.getElementById('maindialog').style.display = "none";
        document.getElementById('dialogbox').style.display = "none";
        document.getElementById('dialogoverlay').style.display = "none";
        window.location.href = url; 
    };
    
    this.cancel = function() {
        document.getElementById('maindialog').style.display = "none";
        document.getElementById('dialogbox').style.display = "none";
        document.getElementById('dialogoverlay').style.display = "none";
    };
}

let customAlert = new CustomAlert();

function zconfirm(event, url,head,body) {
    event.preventDefault();
    customAlert.alert(body, head, url);
}
