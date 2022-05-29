
console.log('from-content-script...')

window.addEventListener("message", function(event) {
  console.log('message:', event)

  if (event.origin == 'http://127.0.0.1:5000' && event.source == window){

    if (event.data.type == 'remove_tab') {
      var tab_id = event.data['tabID']
      console.log('removing tab-id:', tab_id)

      chrome.runtime.sendMessage({type: "remove_tab", 'data': {'tab_id': tab_id}}, function(response) {
        // console.log('bckjs-res:', response)
        // TODO: 
          // update the refresh-session on delete-tab and refresh-button
          // CRUD for sessions <-- most important (will need for tmw)
            // work on UI
          // verify tab-delete is successful and if so, send message to home-page to remove the tab (dom-based is easiest) 
            // add window-delete as well
          // refresh active windows button

      });

    }

    else if (event.data.type == 'refresh_session'){
      chrome.runtime.sendMessage({type: 'refresh_session'})

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


