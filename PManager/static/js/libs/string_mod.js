/**
 * Created by tracker_maker on 25.07.15.
 */
String.prototype.RE = function() {
    return this.replace(/([\$\^\*\(\)\+\[\]\-\{\}\|\.\/\?\\])/g, '\\$1');
};
String.prototype.KeybdConv = (function(){
    var Table = {}, i, L, c,
        en = 'qwertyuiop[]asdfghjkl;\'zxcvbnm,.QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>',
        ru = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ';

    for (i = 0, L = en.length; i < L; i++) {
        c = ru.charAt(i);
        Table[Table[c] = en.charAt(i)] = c;
    }

    var F = function(a) {
        return Table.hasOwnProperty(a) ? Table[a] : a;
    };

    var re = new RegExp("[" + en.RE() + ru.RE() + "]", "g");
    return function() {
        return this.replace(re, F);
    };
})();