
console.log('from-content-script...')

window.addEventListener("message", function(event) {
  console.log('message:', event)

  if (event.origin == 'http://127.0.0.1:5000' && event.source == window){

    if (event.data.type == 'remove_tab') {
      var tab_id = event.data['tabID']
      console.log('removing tab-id:', tab_id)

      chrome.runtime.sendMessage({type: "remove_tab", 'data': {'tab_id': tab_id}}, function(response) {  
        // console.log('bckjs-res:', response)
      });

    }

    else if (event.data.type == 'refresh_session'){
      chrome.runtime.sendMessage({type: 'refresh_session'})
    }

    else if (event.data.type == 'remove_window'){

      var window_id = event.data['window_id'];
      chrome.runtime.sendMessage({type: 'remove_window', 'data': {'window_id': window_id}}, function(response){})

    }

    else if (event.data.type == 'open_session'){
      // console.log('d:', event)
      chrome.runtime.sendMessage({type: 'open_session', 'data': event.data.data}, function(response){})
    }

  }

  // console.log(chrome.tabs.remove())

  // // We only accept messages from ourselves
  // if (event.source != window)
  //     return;

  // if (event.data.type && (event.data.type == "FROM_PAGE")) {
  //     console.log("Content script received message: " + event.data.text);
  // }

});
