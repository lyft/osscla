(function(angular) {
    'use strict';

    angular.module('osscla.common.controllers.SignClaCtrl', [
        'ngResource',
        'ui.bootstrap',
        'xeditable',
        'osscla.common',
    ])

    .controller('common.SignClaCtrl', [
        '$scope',
        '$stateParams',
        '$location',
        '$log',
        '$q',
        'common.Signature',
        function SignClaCtrl($scope, $stateParams, $location, $log, $q, Signature) {
            $scope.userAgreed = false;

            $scope.cancel = function() {
                $location.path('/signature');
            };

            $scope.putSignature = function() {
                var deferred = $q.defer();$
                if (!$scope.userAgreed) {
                    $scope.saveError = 'You must click "I agree" to sign the CLA.';
                    return $scope.saveError;
                }
                Signature.put({'username': $scope.user.username}).$promise.then(function(signature) {
                    deferred.resolve();
                    $scope.signature = signature.signature;
                    $location.path('/signature');
                }, function(res) {
                    if (res.status === 500) {
                        $scope.saveError = 'Unexpected server error.';
                        $log.error(res);
                    } else {
                        $scope.saveError = res.data.error;
                    }
                    deferred.reject();
                });
                return deferred.promise;
            };

    }])

    ;
}(window.angular));
