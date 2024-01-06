let old_data = []
let old_recived = [];
// var audio = new Audio();
// audio.src = '/static/sound.wav';

window.addEventListener("DOMContentLoaded", () => {
    function req() {
        const request = new XMLHttpRequest();
        request.open("GET", "json/");
        request.setRequestHeader("Content-Type" , "application/json; charset=utf-8");
        request.send()
        request.addEventListener('readystatechange', function () {
            function notifyMe (input_message) {
                var notification = new Notification ("Новое уведомление", {
                    tag : "ache-mail",
                    body : "Прочитай скорее)",
                });
                console.log('1234');
            }
            if (request.status == 200 && request.readyState == 4) {
                let data = JSON.parse(request.response)
                // console.log(data.messages);
                if (JSON.stringify(data.messages) != JSON.stringify(old_data)) {
                    // console.log(JSON.stringify(data.received) != JSON.stringify(old_recived));
                    // console.log(data.received);
                    if (JSON.stringify(data.received) != JSON.stringify(old_recived) && old_recived.length != 0) {
                        notifyMe();
                    }
                    old_recived = data.received;
                    // console.log("NEW!");
                    old_data  = data.messages;
                    document.querySelector('.messages').remove();
                    let div = document.createElement('div');
                    div.classList.add('messages');
                    document.querySelector('.chat_main').appendChild(div);
                    data.messages.forEach(item => {
                        let was = false;
                        for (var i = 0; i < data.sent.length; i++) {
                            if (data.sent[i] === item.pk) {
                                was = true;
                            }
                        }
                        if (was) {
                            let message = document.createElement('div');
                            message.classList.add('ui');
                            message.classList.add('grid');
                            message.style.marginLeft = "24.1%";
                            message.innerHTML = `
                            <br>
                            <div class='row'>
                                <div class='left floated four wide column'>
                                    <div class="ui large message" style="background-color: rgb(205, 144, 58); color: white;">
                                    <p>${item.content}</p>
                                    <br>
                                    <br>
                                    <h6>${item.created}</h6>
                                    </div>
                                </div>
                            </div>
                            `
                            document.querySelector('.messages').appendChild(message)
                        } else {
                            let message = document.createElement('div');
                            message.classList.add('ui');
                            message.classList.add('grid');
                            message.style.marginRight = "9%";
                            message.innerHTML = `
                            <br>
                            <div class='row'>
                                <div class='right floated  four wide column'>
                                    <div class="ui left floated red large message" style="background-color: rgb(254, 190, 101);">
                                        <p>${item.content}</p>
                                        <br>
                                        <br>
                                        <h6>${item.created}</h6>
                                    </div>
                                </div>
                            </div>
                        </div>
                            `
                        document.querySelector('.messages').appendChild(message)

                            }

                    })
                };
            }
        });
    }
	
	function notifSet() {
		if (!("Notification" in window))
			a = 1;
		else if (Notification.permission === "granted") {
                    console.log('Уведомления подуключены');
        }  else if (Notification.permission !== "denied") {
			Notification.requestPermission (function (permission) {
				if (!('permission' in Notification))
					Notification.permission = permission;
				if (permission === "granted")
                    console.log('Уведомления подуключены');
			});
		}
	}
    notifSet();
    setInterval(req, 5000);
    req();
});
    