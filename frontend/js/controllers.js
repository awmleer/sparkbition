myApp.controller("ctrl1",function($scope,$rootScope) {
    $scope.items = ["A", "List", "Of", "Items"];
});

myApp.controller("ctrl_header",function($scope,$rootScope,$location) {
    $scope.ale= function () {
        alert($location.path());
    }
});