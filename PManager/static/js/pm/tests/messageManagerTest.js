/**
 * Created with PyCharm.
 * User: Gvammer
 * Date: 21.10.13
 * Time: 22:43
 */

(function($){
    $(function(){
        var mess, view, taskMessagesManager;
        taskMessagesManager = new messageListManager($('.js-commentsContainer'));
        const MESSAGE_ID = 4354;
        test( "Message model init", function() {
            mess = new taskMessageClass({
                'id':MESSAGE_ID,
                'text':'test',
                'date':'08.09.2013',
                'author':{
                    'id':67,
                    'name':'alex',
                    'last_name':'vaneev',
                    'username':'lala'
                }
            });
            ok( mess.id == MESSAGE_ID, "Модель создана успешно!" );
        });
        setTimeout(function(){
            test( "Message view init", function() {
                view = new taskMessageViewClass({
                    'model':mess,
                    'templateHTML':taskMessagesManager.messageTpl
                });
                var tpl = view.template(view.model.toJSON());
                mess.view = view;

                ok( tpl.length > 0, "Шаблон сообщения не должен быть пуст!" );
                ok( tpl.regexIndexOf(/\#[A-z0-_]+\#/) == -1, "Все ключи шаблонов должны быть заданы!" );
                ok( tpl.regexIndexOf('undefined') == -1, "Среди ключей шаблонов не должно быть undefined!" );
                ok( view.render() != false, "Render не должен возвращать False!" );
                ok( view.$el.data('id'), "Элемент шаблона должен иметь содержать data-id!" );

                fakeServerSyncEnvironment({
                    'text':'test text'
                }, function(){
                    test('Connection with fake server', function() {
                        ok(true, 'Выполнение в тестовой среде.');
                        var t = this,
                            newText = 'save to fake server';

                        mess.getFromServer(function(data){
                            equal.call(t, data.text, 'test text' , 'Получение от фэйкового сервера прошло успешно');
                        });
                        mess.set('text', newText);
                        mess.save();
                    });
                });
                mess.getFromServer(function(data){
                    console.log('data start');
                    console.log(data);
                    console.log('data end');
                    test('Message list', function(){
                        var t = this;
                        ok( data, "Получение от сервера прошло успешно" );
                        taskMessagesManager.messageList.push(mess);
                        var lastModel = taskMessagesManager.messageList.at(taskMessagesManager.messageList.length - 1);
                        ok( taskMessagesManager.$commentsContainer.find('.js-taskMessage:last').data('id') == MESSAGE_ID,
                            "При добавлении элемента в коллекцию, он должен добавляться в конец списка комментариев!" );

                        lastModel.view.render();
                        ok(taskMessagesManager.$commentsContainer.find('.js-taskMessage:last')
                            .find('.js-taskMessageText').text().indexOf(data.text) > -1,
                            "Рендеринг комментария после изменения прошел успешно!");


                        taskMessagesManager.messageList.remove(MESSAGE_ID);
                        ok(taskMessagesManager.$commentsContainer.find('.js-taskMessage:last').data('id') != MESSAGE_ID,
                            "Удаление комментария прошло успешно!");

                        lastModel.set('id', null);

                        lastModel.saveToServer(function(data){
                            if (lastModel.get('id'))
                                console.log('Сохранение на сервере прошло успешно: '+lastModel.get('id')+'!');
                            lastModel.destroy({
                                success: function(model, response) {
                                    if (response == 'Message has been deleted')
                                        console.log('Удаление комментария на сервере прошло успешно!')
                                },
                                error: function(model, data){
                                    console.log('Ошибка удаления комментария');
                                }
                            });
                        });
                    });
                })
            });
        }, 3000);
    });
})(jQuery);

String.prototype.regexIndexOf = function(regex, startpos) {
    var indexOf = this.substring(startpos || 0).search(regex);
    return (indexOf >= 0) ? (indexOf + (startpos || 0)) : indexOf;
}