(function (undefined) {
  // Common JS // require JS
  var _, Backbone, exports;
  if (typeof window === 'undefined' || typeof require === 'function') {
    _ = require('underscore');
    Backbone = require('backbone');
    exports = Backbone;
    if (module) module.exports = exports;
  } else {
    _ = this._;
    Backbone = this.Backbone;
    exports = this;
  }


/*!
 * backbone.iobind - Backbone.sync replacement
 * Copyright(c) 2011 Jake Luer <jake@alogicalparadox.com>
 * MIT Licensed
 */


/**
 * # Backbone.sync
 *
 * Replaces default Backbone.sync function with socket.io transport
 *
 * ### Assumptions
 *
 * Currently expects active socket to be located at `window.socket`,
 * `Backbone.socket` or the sync'ed model own socket.
 * See inline comments if you want to change it.
 * ### Server Side
 *
 *     socket.on('todos:create', function (data, fn) {
 *      ...
 *      fn(null, todo);
 *     });
 *     socket.on('todos:read', ... );
 *     socket.on('todos:update', ... );
 *     socket.on('todos:delete', ... );
 *
 * @name sync
 */
Backbone.sync = function (method, model, options) {
  var getUrl = function (object) {
    if (!(object && object.url)) return null;
    return _.isFunction(object.url) ? object.url() : object.url;
  };

  var cmd = getUrl(model).split('/')
    , namespace = (cmd[0] !== '') ? cmd[0] : cmd[1]; // if leading slash, ignore

  var params = _.extend({
    req: namespace + ':' + method
  }, options);

  if ( !params.data && model ) {
    params.data = model.toJSON() || {};
  }

  // If your socket.io connection exists on a different var, change here:
  var io = baseConnector.socket;

  io.send(namespace + ':' + method, params.data, function (data) {
      options.success(data);

//      if (err) {
//        //TODO:заменить на success (функции передается в первом аргументе ответ сервера)
//      options.error(err);
//    } else {
//      options.success(data);
//    }
  });
};


})();