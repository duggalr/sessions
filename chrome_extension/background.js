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


function getWindowDict(windows_res) {

  return new Promise(function(resolve, reject){

    var tmp_arr = []
    for (i=0; i<=windows_res.length-1; i++){
      var window_di = windows_res[i]
      var window_id = window_di['id']
      chrome.tabs.query({windowId: window_id}, function(tabs_info){
        for (x=0; x<=tabs_info.length-1; x++){
          tmp_arr.push(tabs_info[x])
          // tmp_arr.push('testing')
          // var ti = tabs_info[x]
          // tmp_arr[x] = ti
          // tmp_arr.push({
          //   // 'title': ti['title'], 'url': ti['url'], 'window_id': ti['windowId']
          //   0: 'title'
          // })
          // tmp_arr.push({
          //   'title': ti['title'], 'url': ti['url']
          // })
          // final_arr.push(ti)
          // final_arr.push({
          //   'title': ti['title'], 'url': ti['url'], 'window_id': ti['windowId']
          // })
        }
      })
    }

    resolve(tmp_arr)

  })
  
}

    // // var final_dict = {} // {window_1: [tab_one, tab_two] ...}
    // var final_arr = []
    // for (i=0; i<=windows_res.length-1; i++){
    //   var window_di = windows_res[i]
    //   var window_id = window_di['id']
    //   chrome.tabs.query({windowId: window_id}, function(tabs_info){
    //     // var tmp_arr = []
    //     for (x=0; x<=tabs_info.length-1; x++){
    //       var ti = tabs_info[x]
    //       // tmp_arr.push({
    //       //   'title': ti['title'], 'url': ti['url']
    //       // })

    //       // final_arr.push(ti)
    //       final_arr.push({
    //         'title': ti['title'], 'url': ti['url'], 'window_id': ti['windowId']
    //       })
    //     }

    //     // final_dict[window_id] = tabs_info
    //     // final_arr.push({'window_id': window_id, 'tabs_info': tabs_info})
    //     // final_arr.push(tabs_info)
    //     // final_arr.push({''})
    //     // for (x=0; x<=tabs_info.length-1; i++){
    //     //   final_arr.push
    //     // }

    //   })
    // }
    // var final_data = {'window_info': windows_res, 'tab_arr': final_arr}
    // resolve(final_data)

  // })

// }


function sendRes(final_info){

  let response = Request(url=REFRESH_WINDOW_API_URL, data=final_info);
  response.then(function(res){
    console.log('window-refresh-response:', res)
  });

}



function mainFN(){

  chrome.windows.getAll(function(windows_res){

    getWindowDict(windows_res).then(function(final_info){
      console.log('window-dict:', final_info)
      setTimeout(function(){
        // console.log('js', JSON.stringify(final_info))
        sendRes(final_info)
      }, 2000)
      // console.log(JSON.stringify(final_info))
  
  
      // var new_final_info = Object.assign({}, final_info)
      // console.log(JSON.stringify(new_final_info))
  
      // let response = Request(url=REFRESH_WINDOW_API_URL, data=final_info);
      // response.then(function(res){
      //   console.log('window-refresh-response:', res)
      // });
  
    })
  
    // console.log('windows-res:', windows_res)
    // var final_dict = {} // {window_1: [tab_one, tab_two] ...}
    // for (i=0; i<=windows_res.length-1; i++){
    //   var window_di = windows_res[i]
    //   var window_id = window_di['id']
  
    //   chrome.tabs.query({windowId: window_id}, function(tabs_info){
    //     console.log('tabs:', tabs_info)
    //     final_dict[window_id] = tabs_info
    //     // send to flask; will be sent on 'refresh' <-- update the page (don't save in DB)
    //       // save the tab-info for only those in a session on CRUD
    //     // favIconUrl, title, url
    //   })
      
    // }
  
  })


  // setTimeout(mainFN, 5000);

}


// hacky tmp-way
mainFN();


