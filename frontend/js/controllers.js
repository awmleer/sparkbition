app.controller("ctrl1",function($scope,$rootScope) {
    $scope.items = ["A", "List", "Of", "Items"];
});



app.controller("ctrl_header",function($scope,$rootScope,$location,$http) {
    $scope.userinfo={
        name:'小明'
    };
    $scope.logout=function () {
        //api logout
    }
});



app.controller("ctrl_task",function($scope,$rootScope,$location,$http) {

    /*获取任务*/
    // $http({
    //     url: 'http://120.27.123.112:5001/sparkbition/api/task',
    //     method: 'get',
    //     params: {}
    // }).success(function (data) {
    //     $rootScope.groups=data;
    // }).error(function () {
    //     alert("获取信息失败，请稍后再试");
    // });

    //模型-正在查看的task
    $scope.task_looking={};

    //点击任务弹出模态框
    $scope.show_task_info= function () {
        //显示任务详情
        $scope.task_looking=this.task;
        $("#modal_task").modal();
    };
    
    $scope.test= function () {
        alert("123");
    };
});

app.controller("ctrl_newtask",function($scope,$rootScope,$location,$http) {
    //select的options
    // $scope.groups=[];

    $rootScope.newtask={};
    $rootScope.newtask.group=$rootScope.groups[1];

    // 设置默认的option
    // $rootScope.newtask={
    //     groupname:'主要任务'
    // };
    $scope.loginfo=function () {
        console.log($rootScope.newtask);
    };
    var search=$location.search();
    if (search.groupname) {
        
    }
});