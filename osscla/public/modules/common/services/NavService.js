(function(angular) {
    'use strict';

    angular.module('osscla.common.services.NavService', [])

    .service('common.NavService', [
        '$rootScope',
        function($rootScope) {
            var _this = this;
            this.viewLocation = '';

            $rootScope.$on('$stateChangeSuccess', function(evt, state) {
                if(state.data) {
                    _this.viewLocation = state.data.viewLocation;
                }
            });

            this.getViewLocation = function() {
                return _this.viewLocation;
            };

        }])

    ;

})(window.angular);
