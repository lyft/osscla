// Generated on 2014-11-03 using generator-angular 0.9.8
'use strict';

module.exports = function (grunt) {

  // Load grunt tasks automatically
  require('load-grunt-tasks')(grunt);

  grunt.loadNpmTasks('grunt-contrib-compass');

  // Time how long tasks take. Can help when optimizing build times
  require('time-grunt')(grunt);

  // Configurable paths for the application
  var appConfig = {
    app: require('./bower.json').appPath
  };

  // Define the configuration for all the tasks
  grunt.initConfig({

    // Project settings
    project: appConfig,

    // Watches files for changes and runs tasks based on the changed files
    watch: {
      bower: {
        files: ['bower.json'],
        tasks: ['bower:install', 'wiredep', 'compass:app']
      },
      js: {
        files: ['<%= project.app %>/modules/**/*.js'],
        tasks: ['newer:jshint:all']
      },
      jsTest: {
        files: ['<%= project.app %>/modules/**/*.js'],
        tasks: ['test']
      },
      compass: {
        files: ['<%= project.app %>/{modules,styles}/**/*.{scss,sass}'],
        tasks: ['compass:app']
      },
      gruntfile: {
        files: ['Gruntfile.js']
      }
    },

    bower: {
      options: {
        targetDir: '<%= project.app %>/bower_components',
        copy: false
      },
      install: {
        options: {
          bowerOptions: {
            production: true
          }
        }
      }
    },

    compass: {
      options: {
        sassDir: '<%= project.app %>/styles',
        cssDir: '<%= project.app %>/styles',
        generatedImagesDir: '<%= project.app %>/images/generated',
        imagesDir: [
            '<%= project.app %>/images',
        ],
        javascriptsDir: '<%= project.app %>/scripts',
        fontsDir: '<%= project.app %>/styles/fonts',
        importPath: [
            '<%= project.app %>/bower_components',
            '<%= project.app %>/modules'
        ],
        httpImagesPath: '/images',
        httpGeneratedImagesPath: '/images/generated',
        httpFontsPath: '/styles/fonts',
        relativeAssets: true,
        assetCacheBuster: false,
        outputStyle: 'expanded',
        debugInfo: true
      },
      clean: {
        options: {
          debugInfo: false,
          clean: true
        }
      },
      app: {
        options: {
          outputStyle: 'expanded',
          debugInfo: true
        }
      },
      test: {
      }
    },

    // Make sure code styles are up to par and there are no obvious mistakes
    jshint: {
      options: {
        jshintrc: '.jshintrc',
        reporter: require('jshint-stylish')
      },
      all: {
        src: [
          'Gruntfile.js',
          '<%= project.app %>/modules/**/*.js'
        ]
      },
      test: {
        options: {
          jshintrc: 'test/.jshintrc'
        },
        src: ['test/spec/**/*.js']
      }
    },

    // Automatically inject Bower components
    wiredep: {
      app: {
        src: ['<%= project.app %>/index.html'],
        ignorePath:  /\.\.\//,
        fileTypes: {
          html: {
            replace: {
              js: '<script src="{{filePath}}"></script>'
            }
          }
        }
      }
    },

    // Automatically inject app components
    injector: {
      options: {
        ignorePath: '<%= project.app %>',
        relative: true,
        addRootSlash: false,
        destFile:'<%= project.app %>/index.html'
      },
      scripts: {
        src: [
            '<%= project.app %>/js/**/*.js',
            '<%= project.app %>/modules/**/*.js'
        ]
      },
      styles: {
        src: [
            '<%= project.app %>/styles/**/*.css',
            '<%= project.app %>/bower_components/angular/angular-csp.css',
            '<%= project.app %>/bower_components/angular-bootstrap/ui-bootstrap-csp.css'
        ]
      }
    },

    // Test settings
    karma: {
      unit: {
        configFile: 'test/karma.conf.js',
        singleRun: true
      },
      ci: {
        configFile: 'test/karma.conf.js',
        reporters: ['progress', 'junit'],
        singleRun: true
      }
    }
  });

  grunt.registerTask('test', [
    'newer:jshint:all',
    'karma:unit'
  ]);

  grunt.registerTask('testci', [
    'newer:jshint:all',
    'karma:ci'
  ]);

  grunt.registerTask('build', [
    'bower:install',
    'compass:clean',
    'compass:app',
    'wiredep',
    'injector'
  ]);

  grunt.registerTask('dev', [
    'newer:jshint',
    'compass:app',
    'build'
  ]);

  grunt.registerTask('default', [
    'newer:jshint',
    'test'
  ]);
};
