var myApp = angular.module('myApp', ['ui.router']);
myApp.config(function($stateProvider, $urlRouterProvider) {
    //
    // For any unmatched url, redirect to /state1
    $urlRouterProvider.otherwise("/state1");
    //
    // Now set up the states
    $stateProvider
        .state('login', {
            url: "/login",
            views: {
                "viewA": { template: "../partials/state1.html" },
                "viewB": { template: "index.viewB" }
            }
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