app.controller("ctrl_header",function($scope,$rootScope,$location,$http) {
    /*获取用户基本信息*/
    $http({
        url: 'api/userinfo',
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.userinfo=data;
    }).error(function (data,status) {
        if (status == 401) {//如果是unauthorized
            alert("您还没有登录");
            location.href="login.html";//就跳转到登录页面
        }else{
            alert("获取用户个人信息失败，请稍后再试");
        }
    });


    /*APP多页面通用信息的获取*/
    // 获取分组列表
    $http({
        url: 'api/group_list',
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.group_list=data;
    }).error(function () {
        alert("获取分组列表失败，请稍后再试");
    });
    //获取全部成员列表
    $http({
        url: 'api/crew_list',
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.crew_list=data;
    }).error(function () {
        alert("获取成员列表失败，请稍后再试");
    });


    /*退出登录*/
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


    /*获取任务*/
    //获取任务前，先清空数据模型
    $rootScope.groups=[];
    //先判断是任务板状态还是我的任务状态
    var request_url;
    if ($location.path().substr(0, 6) == '/tasks') {
        request_url='api/task';
    }else if ($location.path().substr(0, 7) == '/mytask') {
        request_url='api/mytask';
    }
    $http({
        url: request_url,
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.groups=data;
    }).error(function () {
        alert("获取任务信息失败，请稍后再试");
    });


    //初始化模型-正在查看的task
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
                if (data == "not allowed") {
                    alert("您没有权限完成该任务");
                }else {
                    //查找这个任务
                    for(var i=0;i<$rootScope.groups.length;i++){
                        for(var j=0;j<$rootScope.groups[i].tasks.length;j++){
                            if($rootScope.groups[i].tasks[j]['id'] ==task_id){
                                $rootScope.groups[i].tasks[j]['status'] = 1;//把status改成1
                                $rootScope.groups[i].tasks[j]['finishtime'] = data.finishtime;//设置finishtime
                            }
                        }
                    }
                }
                $("#modal_task").modal('hide');//关闭模态框
            }).error(function () {
                alert("获取信息失败，请稍后再试");
            });

        }
    };

    /*重做任务*/
    $scope.redo_task= function (task_id) {
        if (confirm("确定要重做这项任务吗？")) {

            $http({
                url: 'api/redo_task',
                method: 'get',
                params: {task_id:task_id}
            }).success(function (data) {
                if (data == "not allowed") {
                    alert("您没有权限重做该任务");
                }else {
                    //查找这个任务
                    for(var i=0;i<$rootScope.groups.length;i++){
                        for(var j=0;j<$rootScope.groups[i].tasks.length;j++){
                            if($rootScope.groups[i].tasks[j]['id'] ==task_id){
                                $rootScope.groups[i].tasks[j]['status'] = 0;//把status改成0
                                $rootScope.groups[i].tasks[j]['finishtime'] = '';//回滚finishtime
                            }
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
                }else if (data == 'not allowed') {
                    alert("您没有权限");
                }
            }).error(function () {
                alert("操作失败，请稍后再试");
            });

        }
    };

    /*设置基础分*/
    $scope.set_base_score_showing=false;
    $scope.set_base_score= function (task_id) {
        $http({
            url: 'api/set_base_score',
            method: 'get',
            params: {task_id: task_id,base_score:$scope.task_looking.base_score}
        }).success(function (data) {
            if (data == 'success') {
                $scope.set_base_score_showing=false;
                alert('设置成功');
            }else if (data == 'not allowed') {
                alert("无法设置");
            }
        }).error(function () {
            alert("操作失败，请稍后再试");
        });
    };
    $scope.show_set_base_score= function () {
        $scope.set_base_score_showing=true;
    };



    /*修改任务*/
    $scope.modify_task= function () {
        $rootScope.task_modifying=$scope.task_looking;
        //先触发关闭模态框的事件，然后注册一个事件绑定，等待其完全消失后做页面跳转，同时消除事件监听
        $("#modal_task").modal('hide').on('hidden.bs.modal', function () {
            $("#modal_task").off('hidden.bs.modal');
            location.hash='#/modifytask';
        });
    };


    /*对任务点赞*/
    $scope.upvote= function (task_id) {
        $http({
            url: 'api/upvote',
            method: 'get',
            params: {task_id: task_id}
        }).success(function (data) {
            if (data == 'success') {
                //点赞成功
                for(var i=0;i<$rootScope.groups.length;i++){
                    for(var j=0;j<$rootScope.groups[i].tasks.length;j++){
                        if($rootScope.groups[i].tasks[j]['id'] ==task_id){
                            $rootScope.groups[i].tasks[j].upvoters.push($rootScope.userinfo.username);//把该用户添加进upvoters列表
                        }
                    }
                }
                alert("支持成功");
            }else if (data == 'not allowed') {
                alert("现在还不能支持或您没有支持的权限");
            }else if (data == 'already') {
                alert("您已经支持过了");
            }
        }).error(function () {
            alert("操作失败，请稍后再试");
        });
    };



    /*归档任务*/
    $scope.archive_task= function (task_id) {
        
        if (window.confirm("归档后任务不会显示在任务板上，是否归档？")) {
            $http({
                url: 'api/archive_task',
                method: 'get',
                params: {task_id: task_id}
            }).success(function (data) {
                if (data == 'success') {
                    for(var i=0;i<$rootScope.groups.length;i++){
                        for(var j=0;j<$rootScope.groups[i].tasks.length;j++){
                            if($rootScope.groups[i].tasks[j]['id'] ==task_id){
                                $rootScope.groups[i].tasks.splice(j,1);//删除该task
                            }
                        }
                    }
                    $("#modal_task").modal('hide')//关闭模态框
                }else if (data == 'not allowed') {
                    alert("不能归档");
                }
            }).error(function () {
                alert("操作失败，请稍后再试");
            });
        }
        
    };

});



app.controller("ctrl_newtask",function($scope,$rootScope,$location,$http) {

    /*初始化newtask对象*/
    $rootScope.newtask={
        'tasker_other':[],
        'participators':[],
        'remark':''
    };
    $rootScope.newtask.group=$rootScope.group_list[0];
    $rootScope.newtask.urgency="正常";
    $rootScope.newtask.tasker_main=$rootScope.userinfo.username;



    //TEMP
    $scope.loginfo=function () {
        console.log($rootScope.newtask);
    };


    /*模态框选择成员*/
    //这部分的代码和modify_task的类似（$rootScope.newtask/task_modifying这里不一样）
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

    /*提交*/
    $scope.new_task= function () {
        console.log(JSON.stringify($rootScope.newtask));//TEMP
        $http({
            url: 'api/new_task',
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify($rootScope.newtask)
        }).success(function () {
            alert("添加任务成功");
            location.hash='#/tasks';
        }).error(function () {
            alert("提交失败，请稍后再试");
        });
    }
});



app.controller('ctrl_modifytask',function($scope,$rootScope,$location,$http){

    /*模态框选择成员*/
    //这部分的代码和new_task的类似（$rootScope.newtask/task_modifying这里不一样）
    $scope.add_tasker_other= function (crew) {
        $rootScope.task_modifying.tasker_other.push(crew);
        $("#add_tasker_other").modal('hide');
    };
    $scope.remove_tasker_other= function (crew) {
        $rootScope.task_modifying.tasker_other.remove(crew);
    };
    $scope.add_participator= function (crew) {
        $rootScope.task_modifying.participators.push(crew);
        $("#add_participator").modal('hide');
    };
    $scope.remove_participator= function (crew) {
        $rootScope.task_modifying.participators.remove(crew);
    };

    /*提交修改*/
    $scope.modify_submit= function () {
        console.log(JSON.stringify($rootScope.task_modifying));//TEMP
        $http({
            url: 'api/modify_task',
            method: 'post',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify($rootScope.task_modifying)
        }).success(function (data) {
            if (data == "not allowed") {
                alert("您没有权限");
            }else if (data == "success") {
                alert("修改任务成功");
            }
            location.hash='#/tasks';
        }).error(function () {
            alert("提交失败，请稍后再试");
        });
    };
});





app.controller('ctrl_mytask',function($scope,$rootScope,$location,$http){
    $http({
        url: 'api/mytask',
        method: 'get',
        params: {}
    }).success(function (data) {
        $rootScope.mytask=data;
    }).error(function () {
        alert("获取我的任务列表失败，请稍后再试");
    });
    $rootScope.mytask={
        published:[
            {
                "finishtime":"",
                "publisher":"henry",
                "remark":"some word changed",
                "group":"主要任务",
                "upvoters":[
                    "jim",
                    "小华"
                ],
                "title":"完善通讯录改一改啊改一改",
                "base_score":"5",
                "participators":[
                    "1"
                ],
                "tasker_other":[
                    "jim"
                ],
                "status":0,
                "tasker_main":"AA",
                "ddl":1288323623006,
                "_id":{
                    "$oid":"5719e7408cdd2389ccee2546"
                },
                "id":2,
                "urgency":"正常"
            },
            {
                "finishtime":1461342043796,
                "publisher":"henry",
                "remark":"some word changed",
                "group":"主要任务",
                "upvoters":[
                    "jim",
                    "小华"
                ],
                "title":"完善通讯录",
                "base_score":2,
                "participators":[
                    "1",
                    "2",
                    "3"
                ],
                "tasker_other":[
                    "jim",
                    "john"
                ],
                "status":1,
                "tasker_main":"AA",
                "ddl":1288323623006,
                "_id":{
                    "$oid":"5719e7668cdd2389ccee2548"
                },
                "id":4,
                "urgency":"正常"
            }
        ],
        charged:[],
        participated:[]
    };
});



app.controller('ctrl_statistic',function($scope,$rootScope,$http){
    Chart.defaults.global.colours=[ '#4D5360', '#00ADF9', '#DCDCDC', '#46BFBD', '#FDB45C', '#949FB1', '#4D5360'];
    Chart.defaults.global.scaleBeginAtZero=true;

    $scope.personal={
        score:{
            all:0,
            month:0,
            week:0,
            chart:{
                labels:["六", "五", "四", "三", "二", "一", "零"],
                data:[
                    [0, 0, 0, 0, 0, 0, 0]
                ]
            }
        },
        number:{
            all:0,
            month:0,
            week:0,
            chart:{
                labels:["六", "五", "四", "三", "二", "一", "零"],
                data:[
                    [0, 0, 0, 0, 0, 0, 0]
                ]
            }
        },
        average:{
            all:0,
            month:0,
            week:0,
            chart:{
                labels:["六", "五", "四", "三", "二", "一", "零"],
                data:[
                    [0, 0, 0, 0, 0, 0, 0]
                ]
            }
        }
    };

    $http({
        url: 'api/statistic/personal',
        method: 'get',
        params: {}
    }).success(function (data) {
        $scope.personal=data;
    }).error(function () {
        alert("获取个人统计数据失败");
    });

    $http({
        url: 'api/statistic/ranking',
        method: 'get',
        params: {}
    }).success(function (data) {
        $scope.ranking=data;
    }).error(function () {
        alert("获取信息失败，请稍后再试");
    });
    
});


app.controller('ctrl_changepwd', function ($scope, $rootScope, $location, $http) {
    $scope.submit_change = function () {
        if ($scope.new_password != $scope.new_password2) {
            alert("两次密码不同，请重新输入");
        } else {
            $http({
                url: "api/change_password",
                method: 'get',
                params: {old_password: $scope.old_password, new_password: $scope.new_password}
            }).success(function (data) {
                if (data == 'success') {
                    alert("修改密码成功，请重新登录");
                    location.href = 'login.html';
                } else if (data == 'wrong old password') {
                    alert("密码错误，请重新输入")
                }
            })
        }
    };
});


app.controller('ctrl_userinfo',function($scope,$rootScope,$location,$http){
    $http({
        url:'api/userinfo',
        method:'get',
        params:{}
    }).success(function(data){
        $rootScope.userinfo=data;
    }).error(function(){
        alert("获取用户个人信息失败，请稍后再试")
    });
});