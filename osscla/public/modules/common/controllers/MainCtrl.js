(function(angular) {
    'use strict';

    angular.module('osscla.common.controllers.MainCtrl', [
        'ngResource',
        'ui.bootstrap',
        'xeditable',
        'osscla.common',
    ])

    /*
     * Main controller
     */
    .controller('common.MainCtrl', [
        '$scope',
        '$log',
        '$q',
        'common.Signature',
        function MainCtrl($scope, $log, $q, Signature) {
            $scope.signatures = {};
            $scope.$log = $log;
            Signature.get({'username': $scope.user.username}).$promise.then(function(signature){
                $scope.signature = signature.signature;
                if (!$scope.signature) {
                    $scope.missingSignature = true;
                }
                if ($scope.signature.cla_version != $scope.claVersion){
                    $scope.signatureOutOfDate = true;
                }
            }, function(res) {
                if (res.status === 500) {
                    $scope.saveError = 'Unexpected error finding signature, please reload page.';
                    $log.error(res);
                }
            });

    }])

    ;
}(window.angular));
