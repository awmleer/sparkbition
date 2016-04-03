var app = angular.module('myApp', ['ui.router']);


app.config(function($stateProvider, $urlRouterProvider){
    /*路由模块*/
    $urlRouterProvider.otherwise("/tasks");
    $stateProvider
        .state('tasks', {
            url: "/tasks",
            templateUrl: "../partials/tasks.html"
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

    $rootScope.groups=[
        {
            groupname:'分组1',
            tasks:[
                {
                    title:'task1',
                    type:'normal',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['jim','john'],
                    participator:['1','2','3'],
                    publisher:'henry',
                    ddl:'2016-4-3'
                }
            ]
        }
    ]
}]);