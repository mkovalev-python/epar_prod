function getElementsByAttr(prnt, attr, val) {
    var result = new Array();
    var i;
    var j;
    var tempObj;
    var subRes;
    for (i = 0; i < prnt.childNodes.length; i++) {
        tempObj = prnt.childNodes[i];
        if (tempObj.getAttribute) {
            if (tempObj.getAttribute(attr) == val) {
                result.push(tempObj);
            }
        }
        subRes = getElementsByAttr(tempObj, attr, val);
        for (j in subRes) {
            result.push(subRes[j]);
        }
    }
    return result;
}
function getElementsByClass(prnt, val) {
    var result = [],
        i,
        j,
        tempObj,
        subRes;

    for (i = 0; i < prnt.childNodes.length; i++) {
        tempObj = prnt.childNodes[i];
        if (tempObj.getAttribute) {
            if (tempObj.className == val) {

                result.push(tempObj);
            }
        }

        subRes = getElementsByClass(tempObj, val);
        for (j in subRes) {
            result.push(subRes[j]);
        }
    }
    return result;
}

function getElementsByTagName(prnt, val) {
    var result = new Array();
    var i;
    var j;
    var tempObj;
    var subRes;
    for (i = 0; i < prnt.childNodes.length; i++) {
        tempObj = prnt.childNodes[i];
        if (tempObj.getAttribute) {
            if (tempObj.tagName == val) {

                result.push(tempObj);
            }
        }

        subRes = getElementsByTagName(tempObj, val);
        for (j in subRes) {
            result.push(subRes[j]);
        }
    }
    return result;
}

function setOpacity(obj, val) {
    if (typeof obj.style.opacity == 'string') {
        obj.style.opacity = val;
    }
    else {
        val *= 100;
        obj.style.filter = "progid:DXImageTransform.Microsoft.Alpha(opacity=" + val + ")";
    }
}
function TabBlock(_link, _content, _defaultDisplay, _altDisplay) {
    var lnk = document.getElementById(_link);
    var cont = document.getElementById(_content);
    var defDspl = _defaultDisplay;
    var altDspl = _altDisplay;
    if (lnk == null || cont == null) {
        return false;
    }

    cont.style.display = defDspl;
    lnk.onclick = _lnkClickHandler;

    function _lnkClickHandler() {
        if (cont.style.display == defDspl) {
            cont.style.display = altDspl;
        }
        else {
            cont.style.display = defDspl;
        }
    }
}