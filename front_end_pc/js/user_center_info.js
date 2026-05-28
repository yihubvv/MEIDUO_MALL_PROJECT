var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: '',
        mobile: '',
        email: '',
        email_active: false,
        set_email: false,
        send_email_btn_disabled: false,
        send_email_tip: 'Resend Email',
        email_error: false,
        histories: [],
    },
    mounted: function () {
        // Get the username from the cookie        
        this.username = getCookie('username');

        // Get personal information:        
        this.get_person_info()

        this.get_history()
    },
    methods: {
        // Logout button          
        logoutfunc: function () {
            var url = this.host + '/logout/';
            axios.delete(url, {
                responseType: 'json',
                withCredentials:true,
            })
                .then(response => {
                    location.href = 'login.html';
                })
                .catch(error => {
                    console.log(error.response);
                })
        },
        get_history:function(){
            // Add the following code to send a request and retrieve the user's browsing history information:
            axios.get(this.host + '/browse_histories/', {
                    responseType: 'json',
                    withCredentials:true,
                })
                .then(response => {
                    this.histories = response.data.skus;
                    for(var i=0; i<this.histories.length; i++){
                      this.histories[i].url='/goods/'+this.histories[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error)
                });
        },
        // Get all user profile information        
        get_person_info: function () {
            var url = this.host + '/info/';
            axios.get(url, {
                responseType: 'json',
                withCredentials: true
            })
                .then(response => {
                    if (response.data.code == 400) {
                        location.href = 'login.html'
                        return
                    }
                    this.username = response.data.info_data.username;
                    this.mobile = response.data.info_data.mobile;
                    this.email = response.data.info_data.email;
                    this.email_active = response.data.info_data.email_active;
                })
                .catch(error => {
                    this.set_email = false
                    location.href = 'login.html'
                })
        },
        // save email
        save_email: function () {
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.email_error = false;
            } else {
                this.email_error = true;
                return;
            }

            // Make a frontend page request:            
            var url = this.host + '/emails/'
            axios.put(url,
                {
                    email: this.email
                },
                {
                    responseType: 'json',
                    withCredentials:true,
                })
                // Callback function for a successful request                
                .then(response => {
                    this.set_email = false;
                    this.send_email_btn_disabled = true;
                    this.send_email_tip = 'Email Sent'
                })
                // Callback function for a failed request
                .catch(error => {
                    alert('Failed Request:', error);
                });
        }
    }
});