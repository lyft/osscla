(function(angular) {
    'use strict';

    angular.module('osscla.common.controllers.SignatureCtrl', [
        'ngResource',
        'ui.bootstrap',
        'osscla.common'
    ])

    /*
     * Main controller
     */
    .controller('common.SignatureCtrl', [
        '$scope',
        '$log',
        'common.Signatures',
        function ManageCertsCtrl($scope, $log, Signatures) {
            Signatures.get().$promise.then(function(signatures){
                $scope.signatures = signatures.signatures;
            });
    }])

    ;
}(window.angular));
