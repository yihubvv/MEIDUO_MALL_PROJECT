// Store the backend API server address.
// HTTPS pages should use the nginx proxy on the same origin.
var host = window.location.protocol === 'https:'
    ? window.location.origin
    : 'http://' + window.location.hostname + ':8000';
