/**
 * common $resources for osscla
 */
(function(angular) {
    'use strict';

    angular.module('osscla.common.services.Cla', [
        'ngResource',
        'osscla.common.constants'
    ])

    .factory('common.ClaVersion', ['$resource', 'OSSCLA_URLS', function($resource, OSSCLA_URLS) {
        return $resource(OSSCLA_URLS.CLAVERSION);
    }])

    ;

})(window.angular);
