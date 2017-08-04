/**
 * common $resources for osscla
 */
(function(angular) {
    'use strict';

    angular.module('osscla.common.services.Organization', [
        'ngResource',
        'osscla.common.constants'
    ])

    .factory('common.Organizations', ['$resource', 'OSSCLA_URLS', function($resource, OSSCLA_URLS) {
        return $resource(OSSCLA_URLS.ORGANIZATIONS, {
        });
    }])

    ;

})(window.angular);
