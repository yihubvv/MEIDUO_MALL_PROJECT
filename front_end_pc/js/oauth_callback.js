var site_url = window.location.protocol + '//' + window.location.host;

var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        is_show_waiting: true,

        error_password: false,
        error_phone: false,
        error_sms_code: false,
        error_phone_message: '',
        error_sms_code_message: '',

        sms_code_tip: 'Get SMS',
        sending_flag: false, // Flag indicating that an SMS is currently being sent

        password: '',
        mobile: '',
        sms_code: '',
        access_token: '',

        image_code: '',
        error_image_code_message: '',
        error_image_code: '',
        image_code_url: ''
    },
    mounted: function () {
        if (window.location.hostname == 'localhost' || window.location.hostname == '127.0.0.1') {
            location.replace(site_url + window.location.pathname + window.location.search + window.location.hash);
            return;
        }

        // get captcha:
        this.generate_image_code()


        //Get the code returned by the QQ redirect from the URL path
        var code = this.get_query_string('code');
        axios.get(this.host + '/oauth_callback/?code=' + code, {
                responseType: 'json',
                withCredentials: true,
            })
            .then(response => {
                if (response.data.code == 0) {
                    // Connected account
                    var state = this.get_query_string('state');
                    location.href = site_url + '/';
                } else {
                    // Account not aonnected
                    this.access_token = response.data.access_token;
                    this.is_show_waiting = false;
                }
            })
            .catch(error => {
                console.log(error.response.data);
                alert('error');
            })
    },
    methods: {
        //Generate an image captcha ID and set the src attribute of the image captcha <img> element on the page
        generate_image_code: function () {
            // Generate an ID: For strict uniqueness, use a UUID. In less strict scenarios, a timestamp can also be used.			
            this.image_code_id = generateUUID();
            // Set the src attribute of the image captcha <img> element on the page.
            this.image_code_url = this.host + "/image_codes/" + this.image_code_id + "/";
        },
        // Get URL path parameters
        get_query_string: function (name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_phone: function () {
            var re = /^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone_message = 'Bad Phone Format';
                this.error_phone = true;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code_message = 'Please Enter SMS';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code_message = 'Pleases Enter Captcha.';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        send_sms_code: function () {
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;

            this.check_phone();

            if (this.error_phone == true) {
                this.sending_flag = false;
                return;
            }

            // Send a request to the backend API and let the backend send the SMS verification code
            // var url = this.host + '/sms_codes/' + this.mobile + '/'
            // Send a request to the backend API and let the backend send the SMS verification code
            var url = this.host + '/sms_codes/' + this.mobile + '/' + '?image_code=' + this.image_code +
                '&image_code_id=' + this.image_code_id
            axios.get(url, {
                    responseType: 'json',
                    withCredentials: true,
                })
                .then(response => {
                    // Indicates that the backend successfully sent the SMS verification code
                    // Start a 60-second countdown.
                    // After 60 seconds, allow the user to click the "Send SMS Verification Code" button again.
                    var num = 60;
                    // Set a timer
                    var t = setInterval(() => {
                        if (num == 1) {
                            // If the countdown reaches the end, clear the timer object
                            clearInterval(t);
                            // Restore the original text displayed on the "Get Verification Code" button
                            this.sms_code_tip = 'Get SMS';
                            // Restore the button's onclick event handler
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            // Display the countdown information
                            this.sms_code_tip = num + 's';
                        }
                    }, 1000, 60)
                })
                .catch(error => {
                    if (error.response.status == 400) {
                        this.error_sms_code = 'Captcha does not match.';
                        this.error_sms_code_message = true;
                    } else {
                        console.log(error.response.data);
                    }
                    this.sending_flag = false;
                })
        },
        // save
        on_submit: function () {
            this.check_pwd();
            this.check_phone();
            this.check_sms_code();

            if (this.error_password == false && this.error_phone == false && this.error_sms_code == false) {
                axios.post(this.host + '/oauth_callback/', {
                        password: this.password,
                        mobile: this.mobile,
                        sms_code: this.sms_code,
                        access_token: this.access_token
                    }, {
                        responseType: 'json',
                        withCredentials: true,
                    })
                    .then(response => {
                        // Record the user's login status
                        location.href = site_url + '/'
                    })
                    .catch(error => {
                        if (error.response.status == 400) {
                            this.error_sms_code_message = error.response.data.message;
                            this.error_sms_code = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        }
    }
});