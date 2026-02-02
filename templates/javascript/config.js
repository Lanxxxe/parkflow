BASE_URL = 'http://127.0.0.1:5000/'

function requestOptions(method) {
    return {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    }
}

const fetchData = async (url = '', method = 'GET', data = {}) => {
    const options = requestOptions(method);
    if (method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    const response = await fetch(BASE_URL + url, options);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
}



