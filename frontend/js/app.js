var app = angular.module('myApp', ['ui.router']);


app.config(function($stateProvider, $urlRouterProvider){
    /*路由模块*/
    $urlRouterProvider.otherwise("/state1");
    $stateProvider
        .state('login', {
            url: "/login",
            templateUrl:"../partials/state1.html"
        })
        .state('state1', {
            url: "/state1",
            templateUrl: "../partials/state1.html"
        })
        .state('state1.list', {
            url: "/list",
            templateUrl: "../partials/state1.list.html",
            controller: "ctrl1"
        })
        .state('state2', {
            url: "/state2",
            templateUrl: "../partials/state2.html"
        })
        .state('state2.list', {
            url: "/list",
            templateUrl: "../partials/state2.list.html",
            controller: function($scope) {
                $scope.things = ["A", "Set", "Of", "Things"];
            }
        });

});


app.run(['$rootScope', '$window', '$location', '$log', function ($rootScope, $window, $location, $log) {
    //监听location的变化，实时更新path变量
    var locationChangeSuccessOff = $rootScope.$on('$locationChangeSuccess', locationChangeSuccess);
    function locationChangeSuccess(event) {
        $rootScope.path=$location.path();
    }
}]);