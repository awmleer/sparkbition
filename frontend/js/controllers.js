app.controller("ctrl1",function($scope,$rootScope) {
    $scope.items = ["A", "List", "Of", "Items"];
});




app.controller("ctrl_header",function($scope,$rootScope,$location,$http) {
    /*获取用户基本信息*/
    $http({
        url: 'api/userinfo',
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.userinfo=data;
    }).error(function () {
        alert("获取用户个人信息失败，请稍后再试");
    });

    //TEMP
    // $rootScope.userinfo={
    //     name:'小明'
    // };

    $scope.logout=function () {
        //api logout
        $http({
            url: 'api/logout',
            method: 'get',
            params: {}
        }).success(function (data) {
            if (data == 'success') {
                location.href="login.html";
            }
        }).error(function () {
            alert("获取信息失败，请稍后再试");
        });
    }
});



app.controller("ctrl_task",function($scope,$rootScope,$location,$http) {
    /*获取当前时间*/
    $scope.now=Date.parse( new Date());
    //TEMP
    // console.log($scope.now);

    /*获取任务*/
    $http({
        url: 'api/task',
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.groups=data;
    }).error(function () {
        alert("获取任务信息失败，请稍后再试");
    });


    //模型-正在查看的task
    $scope.task_looking={};

    //点击任务弹出模态框
    $scope.show_task_info= function () {
        $scope.set_base_score_showing=false;
        //显示任务详情
        $scope.task_looking=this.task;
        $("#modal_task").modal();
    };


    /*完成任务*/
    $scope.complete_task= function (task_id) {
        if (confirm("确定要完成这项任务吗？")) {

            $http({
                url: 'api/complete_task',
                method: 'get',
                params: {task_id:task_id}
            }).success(function (data) {
                for(var i=0;i<$rootScope.groups.length;i++){
                    for(var j=0;j<$rootScope.groups[i].tasks.length;j++){
                        if($rootScope.groups[i].tasks[j]['id'] ==task_id){
                            $rootScope.groups[i].tasks[j]['status'] = 1;//把status改成1
                            $rootScope.groups[i].tasks[j]['finishtime'] = data.finishtime;//设置finishtime
                        }
                    }
                }
                $("#modal_task").modal('hide');//关闭模态框
            }).error(function () {
                alert("获取信息失败，请稍后再试");
            });

        }
    };


    /*删除任务*/
    $scope.delete_task= function (task_id) {
        if (confirm("确定要删除这项任务吗？")) {

            $http({
                url: 'api/delete_task',
                method: 'get',
                params: {task_id:task_id}
            }).success(function (data) {
                if (data == 'success') {
                    for(var i=0;i<$rootScope.groups.length;i++){
                        for(var j=0;j<$rootScope.groups[i].tasks.length;j++){
                            if($rootScope.groups[i].tasks[j]['id'] ==task_id){
                                $rootScope.groups[i].tasks.splice(j);//删除该task
                            }
                        }
                    }
                    $("#modal_task").modal('hide');//关闭模态框
                }else if (date == 'not allowed') {
                    alert("您没有权限");
                }
            }).error(function () {
                alert("获取信息失败，请稍后再试");
            });

        }
    };
    
    $scope.set_base_score_showing=false;
    /*设置基础分*/
    $scope.set_base_score= function (task_id) {
        $http({
            url: 'api/set_base_score',
            method: 'get',
            params: {task_id: task_id,base_score:$scope.task_looking.base_score}
        }).success(function (data) {
            if (data == 'success') {
                $scope.set_base_score_showing=false;
                alert('设置成功');
            }
        }).error(function () {
            alert("获取信息失败，请稍后再试");
        });
    };
    $scope.show_set_base_score= function () {
        $scope.set_base_score_showing=true;
    };
    
    $scope.test= function () {
        alert(this.task.completed);
    };
});



app.controller("ctrl_newtask",function($scope,$rootScope,$location,$http) {
    //select的options
    // $scope.groups=[];

    $rootScope.newtask={
        'tasker_other':[],
        'participators':[]
    };

    //获取分组列表
    // $http({
    //     url: 'api/group_list',
    //     method: 'get',
    //     params: {}
    // }).success(function (data) {
    //     $rootScope.group_list=data;
    // }).error(function () {
    //     alert("获取分组列表失败，请稍后再试");
    // });
    $rootScope.group_list=['主要任务','技术任务'];
    $rootScope.newtask.group=$rootScope.group_list[0];

    $rootScope.newtask.urgency="正常";

    //获取全部成员列表
    // $http({
    //     url: 'api/crew_list',
    //     method: 'get',
    //     params: {}
    // }).success(function (data) {
    //     $rootScope.crew_list=data;
    // }).error(function () {
    //     alert("获取成员列表失败，请稍后再试");
    // });
    $rootScope.crew_list=['小明','test','hh','AA'];
    $rootScope.newtask.tasker_main=$rootScope.userinfo.username;

    // // 设置默认的option
    // $rootScope.newtask={
    //     groupname:'主要任务'
    // };
    $scope.loginfo=function () {
        console.log($rootScope.newtask);
    };
    
    $scope.add_tasker_other= function (crew) {
        $rootScope.newtask.tasker_other.push(crew);
        $("#add_tasker_other").modal('hide');
    };
    
    $scope.remove_tasker_other= function (crew) {
        $rootScope.newtask.tasker_other.remove(crew);
    };

    $scope.add_participator= function (crew) {
        $rootScope.newtask.participators.push(crew);
        $("#add_participator").modal('hide');
    };

    $scope.remove_participator= function (crew) {
        $rootScope.newtask.participators.remove(crew);
    };
    
    $scope.new_task= function () {
        console.log(JSON.stringify($rootScope.newtask));
        $http({
            url: 'api/new_task',
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify($rootScope.newtask)
        }).success(function () {
            alert("添加任务成功");
            location.hash='#/task';
        }).error(function () {
            alert("获取信息失败，请稍后再试");
        });
    }
});