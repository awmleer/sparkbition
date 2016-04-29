var app = angular.module('myApp', ['ui.router']);


app.config(function($stateProvider, $urlRouterProvider){
    /*路由模块*/
    $urlRouterProvider.otherwise("/tasks");
    $stateProvider
        .state('tasks', {
            url: "/tasks",
            templateUrl: "partials/tasks.html",
            controller:'ctrl_task'
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
            templateUrl: "partials/statistics.html"
        })
        .state('state2', {
            url: "/state2",
            templateUrl: "partials/state2.html"
        })
        .state('state2.list', {
            url: "/list",
            templateUrl: "partials/state2.list.html",
            controller: function($scope) {
                $scope.things = ["A", "Set", "Of", "Things"];
            }
        });

});


app.run(['$rootScope', '$window', '$location', '$log', function ($rootScope, $window, $location, $log,$http) {
    //监听location的变化，实时更新path变量
    var locationChangeSuccessOff = $rootScope.$on('$locationChangeSuccess', locationChangeSuccess);
    function locationChangeSuccess(event) {
        $rootScope.path=$location.path();
    }
    
    
}]);