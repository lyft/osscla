/**
 * common $resources for osscla
 */
(function(angular) {
    'use strict';

    angular.module('osscla.common.services.UserInfo', [
        'ngResource',
        'osscla.common.constants'
    ])

    /**
     * Email address for currently logged-in user.
     */
    .factory('common.UserInfo', ['$resource', 'OSSCLA_URLS', function($resource, OSSCLA_URLS) {
        return $resource(OSSCLA_URLS.USERINFO);
    }])

    ;

})(window.angular);
