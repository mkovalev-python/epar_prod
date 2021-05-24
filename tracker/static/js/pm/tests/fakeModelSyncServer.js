/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 22.10.13
 * Time: 11:57
 */
var fakeServerSyncEnvironment = function(model, callback){
    var realBackboneSync = Backbone.sync,
        fakeServer = fakeModelSyncServerCreator();

    fakeServer.fakeModel = new Backbone.Model(model);
    Backbone.sync = function(method, model, options){
        fakeServer.sync(method, model, options);
    }
    callback();
    Backbone.sync = realBackboneSync;
}

var fakeModelSyncServerCreator = function(){
    this.fakeModel = {};
    this.sync = function(request,model,options){
        if (this.hasOwnProperty(request)){
            this[request](model,options);
        }else{
            throw 'Bad command: '+request;
        }
    }
    this.read = function(model, options){
        console.log('Read from fake server');
        console.log(model);
        console.log(options);
        options.success(JSON.stringify(this.fakeModel.toJSON()));
    }
    this.create = function(model, options){
        console.log('Create on fake server');
        console.log(model);
        console.log(options);
        options.success(JSON.stringify(this.fakeModel.toJSON()));
    }
    this.update = function(model, options){
        console.log('Update on fake server');
        console.log(model);
        console.log(options);
        options.success(JSON.stringify(this.fakeModel.toJSON()));
    }
    this.delete = function(model, options){
        options.success(JSON.stringify(this.fakeModel.toJSON()));
    }
    return this;
}