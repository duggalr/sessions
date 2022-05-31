const REFRESH_WINDOW_API_URL = 'http://127.0.0.1:5000/refresh_windows'


async function Request(url, data, method = 'POST') {
  // Default options are marked with *
  const response = await fetch(url, {
    method: method, // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {
      'Content-Type': "application/json",
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },    
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data), // body data type must match "Content-Type" header
    dataType: 'json',
  });
  return response.json(); // parses JSON response into native JavaScript objects

}


function getTabData(window_di){

  return new Promise(function(resolve, reject){
    chrome.tabs.query({windowId: window_di['id']}, function(tabs_info){
      // console.log('ti:', tabs_info[0])
      tabs_info.push({'window_id': window_di['id'], 'window_state': window_di['state'], 'window_focused': window_di['focused']})
      // tabs_info['window_state'] = window_di['state']
      // tabs_info['window_focused'] = window_di['focused']
      // console.log('tabs-info:', tabs_info)
      resolve(tabs_info)
    })
  })

}


function sendAllWindows(){

  chrome.windows.getAll(function(all_windows_res){
    var finalData = []

    for (i=0; i <= all_windows_res.length-1; i++){
      // console.log('window-dict:', all_windows_res[i])
      finalData.push(getTabData(all_windows_res[i]))
    }

    Promise.all(finalData).then(function(values) {

      let response = Request(url=REFRESH_WINDOW_API_URL, data=values)
      response.then(function(res){
        console.log('window-refresh-response:', res)
        chrome.tabs.update({  // redirect to flask-app once complete
          url: 'http://127.0.0.1:5000'
        });
      });

    });

  })

}


// On Initial Load (install, update)
chrome.runtime.onInstalled.addListener((reason) => {

  // sendWindows();

  // // console.log('reason:', reason)
  // // sendAllWindows()
  
  // chrome.windows.getAll(function(all_windows_res){
  //   var finalData = []

  //   for (i=0; i <= all_windows_res.length-1; i++){
  //     finalData.push(getTabData(all_windows_res[i]))
  //   }

  //   Promise.all(finalData).then(function(values) {
  //     // console.log('final-values:', values)
      
  //     let response = Request(url=REFRESH_WINDOW_API_URL, data=values);
  //     response.then(function(res){
  //       console.log('window-refresh-response:', res)
  //       chrome.tabs.create({  // redirect to flask-app once complete
  //         url: 'http://127.0.0.1:5000'
  //       });
  //     });

  //   });

  // })

});


// chrome.tabs.onCreated.addListener(function(res){
//     console.log('tab-created:', res)

//     var pending_url = res['pendingUrl']
//     console.log('pend-url:', pending_url)
//     if (pending_url == "chrome://newtab/"){
//       chrome.tabs.update({
//         url: 'main.html'
//       })
      
//       // console.log('new-tab!')
//       // sendWindows()
//     }

//   }
// )

chrome.action.onClicked.addListener(function(res){
  console.log('extension-clicked:', res)
  sendAllWindows()

})


chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    console.log('message:', request, sender)
    
    if (request['type'] == 'remove_tab'){
      chrome.tabs.remove(parseInt(request['data']['tab_id']), function(){
        sendResponse({success: true});
      })
    }
    else if (request['type'] == 'refresh_session'){
      sendAllWindows()
    }
    else if (request['type'] == 'open_session'){

      var data = request['data']
      for (k in data) {
        var tabsArr = data[k]
        var tab_url_list = []
        for (i=0; i <= tabsArr.length-1; i++){
          tab_url_list.push(tabsArr[i]['tab_url'])
        }
        chrome.windows.create({'url': tab_url_list}, function(res){
          console.log('wc-res:', res)
        })
      }

    }

  }
);





// // On inital load, get all open windows
//   // After that, have event-listeners for CRUD on tabs
//     // Setup the BE here and have the retrieve ability (click tab/window, goes to that specific tab/window)

// chrome.windows.getAll(function(windows_res){

//   getWindowDict(windows_res).then(function(final_info){
//     console.log('window-dict:', final_info)
//     setTimeout(function(){
//       // console.log('js', JSON.stringify(final_info))
//       sendRes(final_info)
//     }, 2000)
//     // console.log(JSON.stringify(final_info))

// })





