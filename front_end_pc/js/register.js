var vm = new Vue({
    el: '#app',
    data: {
        host: host,

        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_sms_code: false,
        error_name_message: '',
        error_phone_message: '',
        error_sms_code_message: '',
        error_image_code:'',

        sms_code_tip: 'Get SMS Code',
        sending_flag: false, // Sending SMS flag

        // Image Verification Code:
        image_code_id: '',
        image_code_url: '',

        username: '',
        password: '',
        password2: '',
        mobile: '',
        sms_code: '',
        allow: false,
        image_code:'',
        error_image_code_message:''
    },
    mounted: function(){
		// Get the image verification code from the server.
		this.generate_image_code();
	},
    methods: {
        //Generate an image verification code ID and set the `src` attribute of the image captcha `img` tag on the page.
		generate_image_code: function(){
			// Generate an ID: For stricter uniqueness, use `UUID` to ensure the ID is unique. In less strict situations, a timestamp can also be used.
			this.image_code_id = generateUUID();
			// Set the `src` attribute of the image captcha `img` tag on the page.
			this.image_code_url = this.host + "/image_codes/" + this.image_code_id + "/";
		},
        refresh_image_code: function () {
            this.image_code = '';
            this.generate_image_code();
        },
        // Check username.
        check_username: function () {
            var re = /^[a-zA-Z0-9_-]{5,20}$/;
            var re2 = /^[0-9]+$/;
            if (re.test(this.username) && !re2.test(this.username)) {
                this.error_name = false;
            } else {
                this.error_name_message = 'Use 5-20 letters, numbers, underscores, or hyphens.';
                this.error_name = true;
            }
            // Check for duplicate usernames.
            if (this.error_name == false) {
                var url = this.host + '/usernames/' + this.username + '/count/';
                // How does Vue send AJAX requests? Using `axios`. 
                axios.get(url, {
                    responseType: 'json',
                    withCredentials:true,
                })
                    .then(response => {
                        if (response.data.count > 0) {
                            this.error_name_message = 'Username already exists.';
                            this.error_name = true;
                        } else {
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if (this.password != this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        // Check phone number.
        check_phone: function () {
            var mobile = this.mobile.trim();
            var re = /^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$/;

            if (re.test(mobile)) {
                this.mobile = mobile.replace(/\D/g, '');
                this.error_phone_message = '';
                this.error_phone = false;
            } else {
                this.error_phone_message = 'Please enter a valid phone number.';
                this.error_phone = true;
            }
            if (this.error_phone == false) {
                var url = this.host + '/mobiles/' + this.mobile + '/count/';
                axios.get(url, {
                    responseType: 'json',
                     withCredentials:true,
                })
                    .then(response => {
                        if (response.data.count > 0) {
                            this.error_phone_message = 'Phone number already exists.';
                            this.error_phone = true;
                        } else {
                            this.error_phone = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        // Check image verification code.
		check_image_code: function (){
			if(!this.image_code) {
				this.error_image_code_message = 'Please enter the image code.';
				this.error_image_code = true;
			} else {
				this.error_image_code = false;
			}
		},
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code_message = 'Please enter the SMS code.';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        check_allow: function () {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // Send SMS verification code.
        send_sms_code: function () {
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = true;

            // Validate the parameters to ensure the input fields contain data.
            this.check_phone();

            if (this.error_phone == true) {
                this.sending_flag = false;
                return;
            }

            // Send a request to the backend API and let the backend send the SMS verification code.
            var url = this.host + '/sms_codes/' + this.mobile + '/' + '?image_code=' + this.image_code
                + '&image_code_id=' + this.image_code_id
            axios.get(url, {
                responseType: 'json',
                withCredentials:true,
            })
                .then(response => {
                    this.refresh_image_code();
                    if(response.data.code==400){
                        this.error_sms_code = true;
                        this.error_sms_code_message = response.data.errmsg;
                        return;
                    }
                    // Indicates that the backend successfully sent the SMS message
                    // Start a 60-second countdown.
                    // After 60 seconds, allow the user to click the button to send the SMS verification code again.                    
                    var num = 60;
                    // Set a timer                    
                    var t = setInterval(() => {
                        if (num == 1) {
                            // If the timer reaches the end, clear the timer object                            
                            clearInterval(t);
                            // Restore the original text displayed on the "Get Verification Code" button                            
                            this.sms_code_tip = 'Get SMS Code';
                            // Restore the onclick event function of the button                            
                            this.sending_flag = false;
                        } else {
                            num -= 1;
                            // Display the countdown information                            
                            this.sms_code_tip = num + 's';
                        }
                    }, 1000, 60)
                })
                .catch(error => {
                    this.refresh_image_code();
                    if (error.response.status == 400) {
                        this.error_sms_code_message = error.response.data.errmsg;
                        this.error_sms_code = true;
                    } else {
                        console.log(error.response.data);
                    }
                    this.sending_flag = false;
                })
        },
        // Registration
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_image_code();
            this.check_sms_code();
            this.check_allow();



            // After clicking the register button, send a request
            // (The following code passes parameters through the request body)            
            if (this.error_name == false && this.error_password == false && this.error_check_password == false
                && this.error_phone == false && this.error_image_code == false
                && this.error_sms_code == false && this.error_allow == false) {
                var csrfReady = window.ensureCsrfCookie ? window.ensureCsrfCookie() : Promise.resolve();
                csrfReady.then(() => {
                    return axios.post(this.host + '/register/', {
                        username: this.username,
                        password: this.password,
                        password2: this.password2,
                        mobile: this.mobile,
                        sms_code: this.sms_code,
                        image_code: this.image_code,
                        image_code_id: this.image_code_id,
                        allow: this.allow
                    }, {
                        responseType: 'json',
                        withCredentials:true,
                    });
                })
                    .then(response => {
                        if (response.data.code==0) {
                           location.href = 'index.html';
                        }
                        if (response.data.code == 400) {
                            this.refresh_image_code();
                            alert(response.data.errmsg)
                        }
                    })
                    .catch(error => {
                        this.refresh_image_code();
                        if (error.response.code == 400) {
                            if ('non_field_errors' in error) {
                                this.error_sms_code_message = error.response;
                            } else {
                                this.error_sms_code_message = 'Invalid data.';
                            }
                            this.error_sms_code = true;
                        } else {
                            console.log(error);
                        }
                    })
            }
        }
    }
});
