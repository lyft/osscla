/**
 * Common constants
 *
 * An example common module that defines constants.
 */

(function(angular) {
    'use strict';

    angular.module('osscla.common.constants', [])

    .constant('OSSCLA_URLS', {
        USERINFO: 'v1/user/info',
        SIGNATURE: 'v1/signature/:username',
        CLAVERSION: 'v1/current_cla',
        SIGNATURES: 'v1/signatures',
        ORGANIZATIONS: 'v1/organizations'
    })

    .constant('EMAIL_FORMAT', /^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[_a-z0-9A-Z]+(\.[a-z0-9A-Z]+)+/)

    ;

})(window.angular);
