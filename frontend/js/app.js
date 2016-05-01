var app = angular.module('myApp', ['ui.router','chart.js']);


app.config(function($stateProvider, $urlRouterProvider){
    /*路由模块*/
    $urlRouterProvider.otherwise("/tasks");
    $stateProvider
        .state('tasks', {
            url: "/tasks",
            templateUrl: "partials/tasks.html",
            controller:'ctrl_task'
        })
        .state('mytask', {
            url: "/mytask",
            templateUrl: "partials/tasks.html",//和tasks界面共用一个网页template
            controller:'ctrl_task'//和tasks界面共用一个controller
        })
        .state('newtask', {
            url: "/newtask",
            templateUrl: "partials/newtask.html",
            controller:'ctrl_newtask'
        })
        .state('modifytask', {
            url: "/modifytask",
            templateUrl: "partials/modifytask.html",
            controller:'ctrl_modifytask'
        })
        .state('message', {
            url: "/message",
            templateUrl: "partials/message.html"
        })
        .state('statistics', {
            url: "/statistics",
            templateUrl: "partials/statistics.html",
            controller:'ctrl_statistic'
        })
        .state('about', {
            url: "/about",
            templateUrl: "partials/about.html"
        })
        .state('userinfo', {
            url: "/userinfo",
            templateUrl: "partials/userinfo.html",
            controller:'ctrl_userinfo'
        })
        .state('changepwd', {
            url: "/changepwd",
            templateUrl: "partials/changepwd.html",
            controller:'ctrl_changepwd'
        });


});


app.run(['$rootScope', '$window', '$location', '$log', function ($rootScope, $window, $location, $log,$http) {
    //监听location的变化，实时更新path变量
    var locationChangeSuccessOff = $rootScope.$on('$locationChangeSuccess', locationChangeSuccess);
    function locationChangeSuccess(event) {
        $rootScope.path=$location.path();
    }
    
    
}]);