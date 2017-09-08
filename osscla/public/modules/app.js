(function(angular) {
'use strict';

    angular.module('ossclaApp', [
        // external libs
        'ngRoute',

        // load routes
        'osscla.routes'
    ])

    /*
     * Main controller
     */
    .controller('OssclaMainCtrl', [
        '$scope',
        '$http',
        '$log',
        'common.UserInfo',
        'common.ClaVersion',
        function OssclaMainCtrl($scope, $http, $log, UserInfo, ClaVersion) {
            UserInfo.get().$promise.then(function(user){
                $scope.user = user;
                $http.defaults.xsrfCookieName = user.xsrf_cookie_name;
            });
            ClaVersion.get().$promise.then(function(claVersion){
                $scope.claVersion = claVersion.cla_version;
                $scope.claUrl = 'clas/' + $scope.claVersion;
            });
    }])

    ;

})(window.angular);
