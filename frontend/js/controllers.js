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
    // /*获取任务分组*/
    // $http({
    //     url: 'http://120.27.123.112:5001/sparkbition/api/test',
    //     method: 'get',
    //     params: {}
    // }).success(function (data) {
    //     $rootScope.groups=data;
    // }).error(function () {
    //     alert("获取信息失败，请稍后再试");
    // });
});