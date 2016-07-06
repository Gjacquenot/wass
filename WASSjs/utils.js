
(function(global){
    
    var Q = require('q');
    var kue = require('kue');

    module.exports.fix_path = function( name ) {

        if( name[ name.length - 1] !== '/' )
            name = name + "/";

        return name;
    }

    /**
     * # Deletes a file or a directory in a recursive way 
     * (ie. if path is a directory, deleteRecursive is called 
     * on each contained element 
     */
    module.exports.deleteRecursive = function(path) {
        var fs = require('fs');
        if( fs.existsSync(path) ) {
            
            if( fs.lstatSync( path ).isDirectory() ) {
                fs.readdirSync(path).forEach(function(file,index){
                    var curPath = path + "/" + file;
                    module.exports.deleteRecursive(curPath);
                });
                fs.rmdirSync(path);
            } else {
                fs.unlinkSync(path);
            }
        }
    };

    /**
     * # Set all active <jobname> jobs to inactive
     */ 
    module.exports.deactivate_all_active = function( jobname ) {
        var def = Q.defer();

        require('kue').Job.rangeByType(jobname, 'active', 0, -1, 'asc', function (err, selectedJobs) {
            console.log("Reverting %d old (%s) active jobs to inactive", selectedJobs.length, jobname);
            selectedJobs.forEach(function (job) {
                job.remove();//temp
            });
            def.resolve();
        });

        return def.promise;
    }


    /**
     * # Set all active <jobname> jobs to inactive
     */ 
    module.exports.get_active_jobs = function( jobname ) {
        var deferred = Q.defer();
        require('kue').Job.rangeByType(jobname, 'active', 0, -1, 'asc', function (err, selectedJobs) {
            deferred.resolve( selectedJobs );
        });
        return deferred.promise;
    }


    /**
     * # Removes all the completed <jobname> jobs
     */
    module.exports.remove_all_completed = function( jobname ) {
        var def = Q.defer();

        require('kue').Job.rangeByType( jobname, 'complete', 0, -1, 'asc', function (err, selectedJobs) {
            console.log("Purging %d old (%s) completed jobs", selectedJobs.length, jobname );
            selectedJobs.forEach(function (job) {
                job.remove();
            });
            def.resolve();
        });

        return def.promise;
    }


    /**
     * # Removes all the failed <jobname> jobs
     */
    module.exports.remove_all_failed = function( jobname ) {

        var def = Q.defer();

        require('kue').Job.rangeByType( jobname, 'failed', 0, -1, 'asc', function (err, selectedJobs) {
            console.log("Purging %d old (%s) failed jobs", selectedJobs.length, jobname );
            selectedJobs.forEach(function (job) {
                job.remove();
            });
            def.resolve();
        });

        return def.promise;
    }

})(this);
