(function(angular) {
    'use strict';


    /**
     * This module requires all common services.
     *
     * It mainly provides a convenient way to import all common services by only
     * requiring a dependency on a single module.
     *
     */
    angular.module('osscla.common.services', [
        // Keep this list sorted alphabetically!
        'osscla.common.services.Cla',
        'osscla.common.services.NavService',
        'osscla.common.services.Organization',
        'osscla.common.services.Signature',
        'osscla.common.services.UserInfo'
    ])
    ;
}(angular));
