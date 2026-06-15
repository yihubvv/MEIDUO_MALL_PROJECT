var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'], // 修改vue模板符号，防止与django冲突
    data: {
        host,
        f1_tab: 1, // 1F 标签页控制
        f2_tab: 1, // 2F 标签页控制
        f3_tab: 1, // 3F 标签页控制
        cart_total_count: 0, // 购物车总数量
        carts: [], // 购物车数据,
        username:'',
        content_category:[],
        banners: [
            {
                id: 1,
                title: '美图M8s',
                url: 'https://www.meiduo.site/index.html',
                image_url: '/group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396'
            },
            {
                id: 2,
                title: '黑色星期五',
                url: 'https://www.meiduo.site/index.html',
                image_url: '/group1/M00/00/01/CtM3BVrLmiKANEeLAAFfMRWFbY86177278'
            },
            {
                id: 3,
                title: '厨卫365',
                url: 'https://www.meiduo.site/index.html',
                image_url: '/group1/M00/00/01/CtM3BVrLmkaAPIMJAAESCG7GAh43642702'
            },
            {
                id: 4,
                title: '君乐宝买一送一',
                url: 'https://www.meiduo.site/index.html',
                image_url: '/group1/M00/00/01/CtM3BVrLmnaADtSKAAGlxZuk7uk4998927'
            }
        ]
    },
    mounted(){
        // 获取购物车数据
        // this.get_carts();

         // 获取cookie中的用户名
    	this.username = getCookie('username');


        this.get_cart();
        this.get_banners();
        this.$nextTick(this.init_slide);
    },
    methods: {
        // get_category_data:function(){
        //     var url = this.host + '/content_category/';
        //     axios.get(url, {
        //         responseType: 'json',
        //     })
        //         .then(response => {
        //             this.content_category = response.data.content_category
        //         })
        //         .catch(error => {
        //             console.log(error.response);
        //         })
        // },
        get_banners: function () {
            var url = this.host + '/contents/index_lbt/';
            axios.get(url, {
                responseType: 'json',
                withCredentials:true,
            })
                .then(response => {
                    if (response.data.code === 0 && response.data.contents.length > 0) {
                        this.banners = response.data.contents;
                    }
                    this.$nextTick(this.init_slide);
                })
                .catch(error => {
                    console.log(error);
                    this.$nextTick(this.init_slide);
                })
        },
        init_slide: function () {
            if (window.initSlide) {
                window.initSlide();
            }
        },
        // 退出登录按钮
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
        // 获取购物车数据
       get_cart(){
        let url = this.host + '/carts/simple/';
        axios.get(url, {
            responseType: 'json',
            withCredentials:true,
        })
            .then(response => {
                this.carts = response.data.cart_skus;

                this.cart_total_count = 0;
                for(let i=0;i<this.carts.length;i++){
                    if (this.carts[i].name.length>25){
                        this.carts[i].name = this.carts[i].name.substring(0, 25) + '...';
                    }
                    this.cart_total_count += this.carts[i].count;
                }
            })
            .catch(error => {
                console.log(error);
            })
    },

    }
});










// $(function(){
//     // 楼层选项卡
// 	var $tab = $('.subtitle a');
// 	var $content = $('.goods_list_con .goods_list');
//
// 	$tab.click(function(){
// 		var $index = $tab.index($(this));
// 		$(this).addClass('active').siblings().removeClass('active');
// 		$content.eq($index).addClass('goods_list_show').siblings().removeClass('goods_list_show');
// 	});
//
// 	// 获取并展示购物车数据
// 	get_cart();
// });
