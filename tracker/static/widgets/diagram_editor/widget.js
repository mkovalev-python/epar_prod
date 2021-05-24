$(function () {
    var visio = (function() {
        joint.shapes.devs.rectWithPorts =
            joint.shapes.basic.Generic
                .extend(_.extend({}, joint.shapes.basic.PortsModelInterface, {

               markup: '<g class="rotatable"><g class="scalable"><rect class="body"/></g><text class="label"/><g class="inPorts"/><g class="outPorts"/></g>',
               portMarkup: '<g class="port port<%= id %>"><circle class="port-body"/></g>',

               defaults: joint.util.deepSupplement({

                   type: 'devs.rectWithPorts',
                   size: { width: 1, height: 1 },

                   inPorts: [],
                   outPorts: [],

                   attrs: {
                        '.': { magnet: false },
                       '.body': {
                           width: 150, height: 250,
                           stroke: 'black'
                       },
                       '.port-body': {
                           r: 7,
                           magnet: true,
                           stroke: 'black'
                       },
                       '.label': {
                                   'ref-x': 10,
                                   'ref-y': .2,
                                    text: 'Активность',
                                    fill: '#fefefe',
                                    'font-size': 24,
                                    'font-weight': 'bold',
                                    'font-variant': 'small-caps'
                        },
            //           '.label': { text: 'Model', 'ref-x': 10, 'ref-y': .2, 'ref': '.body' },

                       // CHANGED: find better positions for port labels
                       '.inPorts .port-label': { dy:-30, x: 4, fill: 'black' },
                       '.outPorts .port-label':{ dy: 15, x: 4, fill: 'black' }
                       //
                   }

               }, joint.shapes.basic.Generic.prototype.defaults),

               getPortAttrs: function(portName, index, total, selector, type) {

                   var attrs = {};

                   var portClass = 'port' + index;
                   var portSelector = selector + '>.' + portClass;
                   var portLabelSelector = portSelector + '>.port-label';
                   var portBodySelector = portSelector + '>.port-body';

                   attrs[portLabelSelector] = { text: portName };
                   attrs[portBodySelector] = { port: { id: portName || _.uniqueId(type) , type: type } };

                   // CHANGED: swap x and y ports coordinates ('ref-y' => 'ref-x')

                   if ((index+1) <= total/2) {
                       attrs[portSelector] = { ref: '.body', 'ref-x': (index + 0.5) * (1 / (Math.floor(total / 2) || 1)) };
                       if (selector === '.outPorts') { attrs[portSelector]['ref-dy'] = 0; }
                   } else {
                       attrs[portSelector] = { ref: '.body', 'ref-y': (index - (Math.floor(total / 2) || 1) + 0.5) * (1 / (Math.floor(total / 2) || 1)) };
                       if (selector === '.outPorts') { attrs[portSelector]['ref-dx'] = 0; }
                   }

                   // ('ref-dx' => 'ref-dy')

                   //
                   return attrs;
               }
            }));
        joint.shapes.devs.Condition =
            joint.shapes.basic.Generic
                .extend(_.extend({}, joint.shapes.basic.PortsModelInterface, {

               markup: '<g class="rotatable"><g class="scalable"><path/></g><text/><g class="inPorts"/><g class="outPorts"/></g>',
               portMarkup: '<g class="port port<%= id %>"><circle class="port-body"/></g>',

               defaults: joint.util.deepSupplement({

                   type: 'devs.Condition',
                   size: { width: 1, height: 1 },

                   inPorts: [],
                   outPorts: [],

                   attrs: {
                       'path': { d: 'M 30 0 L 60 30 30 60 0 30 z' },
                        '.': { magnet: false },
                       '.body': {
                           width: 150, height: 250,
                           stroke: 'black'
                       },
                       '.port-body': {
                           r: 7,
                           magnet: true,
                           stroke: 'black'
                       },
                       '.label': {
                                   'ref-x': 10,
                                   'ref-y': .2,
                                    text: 'Активность',
                                    fill: '#fefefe',
                                    'font-size': 24,
                                    'font-weight': 'bold',
                                    'font-variant': 'small-caps'
                        },
            //           '.label': { text: 'Model', 'ref-x': 10, 'ref-y': .2, 'ref': '.body' },

                       // CHANGED: find better positions for port labels
                       '.inPorts .port-label': { dy:-30, x: 4, fill: 'black' },
                       '.outPorts .port-label':{ dy: 15, x: 4, fill: 'black' }
                       //
                   }

               }, joint.shapes.basic.Path.prototype.defaults),

               getPortAttrs: function(portName, index, total, selector, type) {

                   var attrs = {};

                   var portClass = 'port' + index;
                   var portSelector = selector + '>.' + portClass;
                   var portLabelSelector = portSelector + '>.port-label';
                   var portBodySelector = portSelector + '>.port-body';

                   attrs[portLabelSelector] = { text: portName };
                   attrs[portBodySelector] = { port: { id: portName || _.uniqueId(type) , type: type } };

                   // CHANGED: swap x and y ports coordinates ('ref-y' => 'ref-x')

                   if ((index+1) <= total/2) {
                       attrs[portSelector] = { ref: '.body', 'ref-x': (index + 0.5) * (1 / (Math.floor(total / 2) || 1)) };
                       if (selector === '.outPorts') { attrs[portSelector]['ref-dy'] = 0; }
                   } else {
                       attrs[portSelector] = { ref: '.body', 'ref-y': (index - (Math.floor(total / 2) || 1) + 0.5) * (1 / (Math.floor(total / 2) || 1)) };
                       if (selector === '.outPorts') { attrs[portSelector]['ref-dx'] = 0; }
                   }

                   // ('ref-dx' => 'ref-dy')

                   //
                   return attrs;
               }
            }));


        joint.shapes.devs.rectWithPortsView = joint.shapes.devs.ModelView;
        joint.shapes.devs.ConditionView = joint.shapes.devs.ModelView;

        this.baseFigures = [
            new joint.shapes.devs.rectWithPorts({
                clonable: true,
                position: { x: 200, y: 50 },
                connector: { name: 'rounded' },
                size: { width: 150, height: 70 },
                inPorts: ['a', 'b'],
                outPorts: ['c','d'],
                attrs: {
                    rect: {
                        fill: {
                            type: 'linearGradient',
                            stops: [
                                { offset: '0%', color: '#45484d' },
                                { offset: '100%', color: '#000000' }
                            ],
                            attrs: { x1: '0%', y1: '0%', x2: '0%', y2: '100%' }
                        }
                    },
                    text: {
                        text: 'Активность',
                        fill: '#fefefe',
                        'font-size': 18,
                        'font-weight': 'bold',
                        'font-variant': 'small-caps'
                    }
                }
            }),
            new joint.shapes.devs.Condition({
                clonable: true,
                position: { x: 200, y: 150 },
                connector: { name: 'rounded' },
                size: { width: 150, height: 70 },
                inPorts: ['a1', 'b1'],
                outPorts: ['c1','d1'],
                attrs: {
                    path: {
                        d: 'M 75 0 L 150 30 75 60 0 30 z' ,
                        fill: {
                            type: 'linearGradient',
                            stops: [
                                { offset: '0%', color: '#45484d' },
                                { offset: '100%', color: '#000000' }
                            ],
                            attrs: { x1: '0%', y1: '0%', x2: '0%', y2: '100%' }
                        }
                    },
                    text: {
                        text: 'Активность',
                        fill: '#fefefe',
                        'font-size': 18,
                        'font-weight': 'bold',
                        'font-variant': 'small-caps'
                    }
                }
            }),
            new joint.shapes.devs.rectWithPorts({
                clonable: true,
                position: { x: 200, y: 250 },
                connector: { name: 'rounded' },
                size: { width: 150, height: 70 },
                inPorts: ['a', 'b'],
                outPorts: ['c','d'],
                attrs: {
                    rect: {
                        fill: {
                            type: 'linearGradient',
                            stops: [
                                { offset: '0%', color: '#45484d' },
                                { offset: '100%', color: '#000000' }
                            ],
                            attrs: { x1: '0%', y1: '0%', x2: '0%', y2: '100%' }
                        }
                    },
                    text: {
                        text: 'Активность',
                        fill: '#fefefe',
                        'font-size': 18,
                        'font-weight': 'bold',
                        'font-variant': 'small-caps'
                    }
                }
            }),
        ];

        var graph = new joint.dia.Graph;
        var i;


        var paper = new joint.dia.Paper({
            el: $('.js-paper'),
            width: 1000,
            height: 600,
            gridSize: 10,
            model: graph
        });

        var sourceContainer = new joint.shapes.basic.Rect({
            position: { x: 5, y: 5 },
            size: { width: 200, height: 600 },
            attrs: {
                rect: {
                    stroke: 'blue',
                    fill: 'none'
                }
            }
        });



        for (i in this.baseFigures) {
            graph.addCell(this.baseFigures[i].position(20, 30 + i * (this.baseFigures[i].get('size')['height'] + 30)));
        }

        graph.addCells([
                sourceContainer.clone()
            ]
        );

        paper.on('cell:pointerdown', function(cellView, evt, x, y) {
            if (cellView.model.get('clonable'))
                if (!cellView.model.get('cloned')) {
                    var clone = cellView.model.clone();
                    cellView.model.set('cloned', clone);
                }
        });
        graph.on('change:position', function (cell) {

            // has an obstacle been moved? Then reroute the link.
//            if (_.contains(obstacles, cell)) paper.findViewByModel(link).update();

            if (cell.get('cloned')) {
                var clone = cell.get('cloned');
                graph.addCell(clone);
                cell.set('clonable', false);
                cell.set('cloned', false);
            }

        });


//        $('.router-switch').on('click', function (evt) {
//
//            var router = $(evt.target).data('router');
//            var connector = $(evt.target).data('connector');
//
//            if (router) {
//                link.set('router', { name: router });
//            } else {
//                link.unset('router');
//            }
//
//            link.set('connector', { name: connector });
//        });

        return this;
    })();
});