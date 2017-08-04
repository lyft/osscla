/**
 * common $resources for osscla
 */
(function(angular) {
    'use strict';

    angular.module('osscla.common.services.Signature', [
        'ngResource',
        'osscla.common.constants'
    ])

    .factory('common.Signature', ['$resource', 'OSSCLA_URLS', function($resource, OSSCLA_URLS) {
        return $resource(OSSCLA_URLS.SIGNATURE, {username: '@username'}, {
            put: {method: 'PUT', isArray: false}
        });
    }])

    .factory('common.Signatures', ['$resource', 'OSSCLA_URLS', function($resource, OSSCLA_URLS) {
        return $resource(OSSCLA_URLS.SIGNATURES);
    }])

    ;

})(window.angular);
