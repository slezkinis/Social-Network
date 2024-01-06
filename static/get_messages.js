window.addEventListener("DOMContentLoaded", () => {
    function req() {
        const request = new XMLHttpRequest();
        request.open("GET", "/profiles/get_new_messages");
        request.setRequestHeader("Content-Type" , "application/json; charset=utf-8");
        request.send()
        request.addEventListener('readystatechange', function () {
            function notifyMe (count) {
                if (count == 1) {
                    var notification = new Notification ('Новое уведомление', {
                        tag : "ache-mail",
                        body : "Прочитай скорее)",
                    });
                } else {
                    var notification = new Notification ('Новый уведомления', {
                        tag : "ache-mail",
                        body : "Прочитай скорее)",
                    });
                }
            }
            if (request.status == 200 && request.readyState == 4) {
                let data = JSON.parse(request.response)
                if (data['status'] == true) {
                    console.log('NEW');
                    if (data['count'] == 1) {
                        UIkit.notification({message: 'Новое уведомление'});
                    } else {
                        UIkit.notification({message: 'Новые уведомления'});
                    }
                    notifyMe(data['count']);
                }
            }
        });
    }
	function notifSet() {
		if (!("Notification" in window))
			a = 1;
		else if (Notification.permission === "granted") {
                    console.log('Уведомления подключены');
        }  else if (Notification.permission !== "denied") {
			Notification.requestPermission (function (permission) {
				if (!('permission' in Notification))
					Notification.permission = permission;
				if (permission === "granted")
                    console.log('Уведомления подключены');
			});
		}
	}
    notifSet();
    setInterval(req, 5000);
});
    