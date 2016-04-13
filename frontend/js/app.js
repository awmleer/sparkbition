var app = angular.module('myApp', ['ui.router']);


app.config(function($stateProvider, $urlRouterProvider){
    /*路由模块*/
    // $urlRouterProvider.otherwise("/tasks");
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
            index:0,
            tasks:[
                {
                    id:2,
                    title:'完善通讯录aaweeeeg',
                    urgency:'正常',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['jim','john'],
                    participators:['1','2','3'],
                    publisher:'henry',
                    ddl:'1288323623006',
                    base_score:'5',
                    upvoters:['jim','小华']
                },
                {
                    id:3,
                    title:'task2',
                    urgency:'正常',
                    remark:'',
                    tasker_main:'12',
                    tasker_other:['小李','小王'],
                    participators:['1','2','3'],
                    publisher:'小华',
                    ddl:'1289355623006',
                    base_score:3,
                    upvoters:[]
                },
                {
                    id:4,
                    title:'紧急会议',
                    urgency:'紧急',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['smith','harry'],
                    participators:['1','2','3'],
                    publisher:'小明',
                    ddl:'1285978923006',
                    base_score:2,
                    upvoters:['henry']
                }
            ]
        },
        {
            groupname:'技术任务',
            index:1,
            tasks:[
                {
                    id:5,
                    title:'task1',
                    urgency:'火急',
                    remark:'some word here',
                    tasker_main:'henry',
                    tasker_other:['jim','john'],
                    participators:['1','2','3'],
                    publisher:'mary',
                    ddl:'1285978923006',
                    base_score:'5',
                    upvoters:['jim','小华']
                }
            ]
        }
    ]
}]);