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
            resolve(tabs_info)
        });
        
    });
  
};


function tmpTwo(all_windows){

    return new Promise(function(resolve, reject) {
        let promises = [];

        let finalData = [];

        for (let i = 0; i <= all_windows.length - 1; i++) {
            let window_di = all_windows[i];

            console.log('window-dict:', window_di);

            let tabDataPromise = getTabData(window_di).then(function(tabDataRes) {
                finalData.push({
                    'window_data': window_di,                    
                    'tab_info': tabDataRes,
                    'num_of_tabs': tabDataRes.length,
                });
            });

            promises.push(tabDataPromise);
        }

        Promise.all(promises)
            .then(function() {
                resolve(finalData);
            })
            .catch(function(error) {
                reject(error);
            });
    });

}



function tmpOne(){

    return new Promise(function(resolve, reject){

        chrome.windows.getAll(function(all_windows_res){

            tmpTwo(all_windows_res).then(function(tmp_two_res){

                console.log('info:', tmp_two_res);

                let response = Request(
                    url = REFRESH_WINDOW_API_URL, 
                    data = tmp_two_res
                )
                // response.then(function(res){
                //     console.log('window-refresh-response:', res)
                //     // chrome.tabs.update({  // redirect to flask-app once complete
                //     //     url: 'http://127.0.0.1:5000'
                //     // });
                // });

            });

            // var finalData = [];
            // for (i=0; i <= all_windows_res.length-1; i++){

            //     let window_di = all_windows_res[i];
            //     getTabData(window_di).then(function(tabDataRes){
            //         finalData.push(tabDataRes);
            //     });

            // };

            // resolve(finalData);
    
            // for (i=0; i <= all_windows_res.length-1; i++){
            //     // console.log('window-dict:', all_windows_res[i])
            //     // finalData.push(getTabData(all_windows_res[i]))
            //     finalData.push({
            //         'window_data': all_windows_res[i],
            //         'tab_info': getTabData(all_windows_res[i])
            //     });
            // };
    
            // Promise.all(finalData).then(function(values) {
    
            //     let response = Request(url=REFRESH_WINDOW_API_URL, data=values)
            //     response.then(function(res){
            //         console.log('window-refresh-response:', res)
            //         // chrome.tabs.update({  // redirect to flask-app once complete
            //         //     url: 'http://127.0.0.1:5000'
            //         // });
            //     });
    
            // });
    
        });

        // resolve(finalData);

    });

}


function sendAllWindows(){

    tmpOne().then(function(res){

        console.log('final-res:', res)

    })

    // chrome.windows.getAll(function(all_windows_res){
    //     var finalData = []



    //     // for (i=0; i <= all_windows_res.length-1; i++){
    //     //     // console.log('window-dict:', all_windows_res[i])
    //     //     // finalData.push(getTabData(all_windows_res[i]))
    //     //     finalData.push({
    //     //         'window_data': all_windows_res[i],
    //     //         'tab_info': getTabData(all_windows_res[i])
    //     //     });
    //     // };

    //     // Promise.all(finalData).then(function(values) {

    //     //     let response = Request(url=REFRESH_WINDOW_API_URL, data=values)
    //     //     response.then(function(res){
    //     //         console.log('window-refresh-response:', res)
    //     //         // chrome.tabs.update({  // redirect to flask-app once complete
    //     //         //     url: 'http://127.0.0.1:5000'
    //     //         // });
    //     //     });

    //     // });

    // })
  
}


chrome.action.onClicked.addListener(function(res){
 
    console.log('extension-clicked:', res)
    sendAllWindows()

})
