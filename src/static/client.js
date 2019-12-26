

class Client {
    constructor() {
        $('#start-recording').click(this.onStartRecording);
        $('#stop-recording').click(this.onStopRecording);
        $('#reconnect-sphero').click(this.onReconnectSphero);
        $('#predict').click(this.onPredict);

    }

    onStartRecording(event) { // $ represent an instance of jquery
        let description = $('#description').val()
        console.log(description)
        $.ajax({ // ajax is a func wich utils to send http request (it oprates on $)
            url: '/start-recording/', // ajax func recive a jason as an argument with the key url. url is the path of the specific button in the server.
            type: "POST",
	        data: JSON.stringify({'description': description}),
	        contentType: "application/json; charset=utf-8",
        }).done(function() {
            alert('Recording started.')
        })
    }

    onStopRecording(event) {
        $.ajax({
            url: '/stop-recording/'
        }).done(function() {
            alert('Recording stopped.')
        })
    }

    onReconnectSphero(event) {
        $.ajax({
            url: '/reconnect-sphero/'
        }).done(function() {
            console.log('reconnected.')
        })
    }

    onPredict(event) {
        $.ajax({
            url: '/predict/'
        }).done(function() {
            alert('Predicting.')
        })
    }

}


new Client()