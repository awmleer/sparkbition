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
        .state('message', {
            url: "/message",
            templateUrl: "partials/message.html"
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

    

    
    $rootScope.groups=[
        {
            groupname:'主要任务',
            tasks:[
                {
                    title:'完善通讯录',
                    type:'正常',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['jim','john'],
                    participators:['1','2','3'],
                    publisher:'henry',
                    ddl:'1288323623006',
                    score:''
                },
                {
                    title:'task2',
                    type:'正常',
                    remark:'',
                    tasker_main:'12',
                    tasker_other:['小李','小王'],
                    participators:['1','2','3'],
                    publisher:'小华',
                    ddl:'1289355623006'
                },
                {
                    title:'紧急会议',
                    type:'紧急',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['smith','harry'],
                    participators:['1','2','3'],
                    publisher:'小明',
                    ddl:'1285978923006'
                }
            ]
        },
        {
            groupname:'技术任务',
            tasks:[
                {
                    title:'task1',
                    type:'火急',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['jim','john'],
                    participators:['1','2','3'],
                    publisher:'mary',
                    ddl:'2016-4-3'
                }
            ]
        }
    ]
}]);