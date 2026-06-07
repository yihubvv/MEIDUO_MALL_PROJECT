// Store the backend API server address.
// HTTPS pages should use the nginx proxy on the same origin.
var host = window.location.protocol === 'https:'
    ? window.location.origin
    : 'http://' + window.location.hostname + ':8000';

function configureAxiosCsrf() {
    if (!window.axios) {
        return;
    }
    axios.defaults.xsrfCookieName = 'csrftoken';
    axios.defaults.xsrfHeaderName = 'X-CSRFToken';
    axios.defaults.withCredentials = true;
}

function ensureCsrfCookie() {
    configureAxiosCsrf();
    if (!window.axios) {
        return Promise.resolve();
    }
    return axios.get(host + '/csrf/', {
        responseType: 'json',
        withCredentials: true
    });
}

window.addEventListener('load', function () {
    ensureCsrfCookie().catch(function (error) {
        console.log(error);
    });
});
