var vm = new Vue({
    el: '.header_con',
    data: {
        username: '',
    },
    mounted(){

    }
});


// $(function () {
//     // Set the username for session persistence
//     set_username();
// });
//
// // Set the username for session persistence
// function set_username() {
//     // Read the user's session persistence information
//     var username = getCookie('username');
//     var $username;
//
//     if (username) {
//         $username =
//             "Welcome, <em>" + username + "</em>\n" +
//             "\t\t\t\t\t<span>|</span>\n" +
//             "\t\t\t\t\t<a href='/logout/'>Logout</a>";
//
//         $('.login_btn').append($username);
//     } else {
//         $username =
//             "<a href='/login/'>Login</a>\n" +
//             "\t\t\t\t\t<span>|</span>\n" +
//             "\t\t\t\t\t<a href='/register/'>Register</a>";
//
//         $('.login_btn').append($username);
//     }
// }