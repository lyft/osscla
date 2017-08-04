(function(angular) {
    'use strict';

    angular.module('osscla.common.controllers.CCLACtrl', [
        'ngResource',
        'ui.bootstrap',
        'xeditable',
        'ngTagsInput',
        'ui.select',
        'osscla.common'
    ])

    .controller('common.CCLACtrl', [
        '$scope',
        '$stateParams',
        '$location',
        '$log',
        '$q',
        'EMAIL_FORMAT',
        'common.Organizations',
        'common.Signature',
        function CCLACtrl($scope, $stateParams, $location, $log, $q, EMAIL_FORMAT, Organizations, Signature) {
            Organizations.get().$promise.then(function(orgs) {
                $scope.fetchedOrgs = orgs.orgs;
            }, function() {
                $scope.fetchedOrgs = [];
                $log.log('Failed to fetch orgs.');
            });

            $scope.signature = {
                username: '',
                emails: [],
                orgs: [],
                admin_update: true
            };

            $scope.cancel = function() {
                $location.path('/signature_list');
            };

            $scope.putSignature = function() {
                var _signature = angular.copy($scope.signature),
                    deferred = $q.defer(),
                    validEmail = true;
                angular.forEach($scope.signature.emails, function(item) {
                    if (!EMAIL_FORMAT.test(item.text) || item.text.indexOf('@') === -1) {
                        $scope.saveError = item.text + ' is an invalid email address format.';
                        validEmail = false;
                    }
                });
                if (!validEmail) {
                    deferred.reject();
                    return deferred.promise;
                }
                _signature.emails = [];
                angular.forEach($scope.signature.emails, function(email) {
                    _signature.emails.push(email.text);
                });
                Signature.put({'username': _signature.username}, _signature).$promise.then(function(signature) {
                    deferred.resolve();
                    $location.path('/signature_list');
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
