"use strict";

var adaptive = function adaptive() {
  var e = document.createElement("div");
  e.style.overflowY = "scroll", e.style.width = "50px", e.style.height = "50px", e.style.visibility = "hidden", document.body.appendChild(e);
  var t = e.offsetWidth - e.clientWidth;
  document.body.removeChild(e), window_width = document.documentElement.clientWidth + t;

  var s = function s() {
    window_width = document.documentElement.clientWidth + t, fontHtml = window_width / 165, $("html").css({
      "font-size": fontHtml + "px"
    }), window_width < 501 && (fontHtml = window_width / 52, $("html").css({
      "font-size": fontHtml + "px"
    }));
  };

  s(), $(window).resize(function () {
    s();
  });

  var i = function i() {
    $(".JSelemTrans").removeClass("JStrans"), setTimeout(function () {
      $(".JSelemTrans").addClass("JStrans");
    }, 300);
  };

  i(), $(window).resize(function () {
    i();
  });
};

$(window).scroll(function () {
  $(".JSblock").each(function () {
    $(window).scrollTop() > $(this).offset().top - $(window).height() / 2 && $(this).find("._JSanim").addClass("_active");
  });
});

var bodyFix = function bodyFix() {
  scroll = 0;
  var e = !1;
  $(window).scroll(function () {
    if (e) return !1;
    scroll = $(window).scrollTop();
  }), windowFix = function windowFix(t) {
    e = !0, $("body").css({
      position: "fixed",
      top: -t / fontHtml + "rem"
    });
  }, windowFixRemove = function windowFixRemove(t) {
    $("body").css({
      position: "static",
      top: "unset",
      "overflow-y": "scroll"
    }), $("html,body").animate({
      scrollTop: t
    }, 0), e = !1;
  };
},
    doneItem = function doneItem() {
  $(window).scroll(function () {
    $(".JSdone").each(function () {
      var _this = this;

      $(window).scrollTop() > $(this).offset().top && ($(this).find(".JSdoneItemTop").addClass("_active"), setTimeout(function () {
        $(_this).find(".JSdoneItemRight").addClass("_active");
      }, 600));
    });
  });
};

$(window).scroll(function () {
  $(window).scrollTop() >= 10 ? $(".body__menu-fixed").addClass("scroll") : $(".body__menu-fixed").removeClass("scroll");
});

var grGateAnimate = function grGateAnimate() {
  setTimeout(function () {
    $(".sectionQrGateHeader__item").each(function () {
      $(this).addClass("_active");
    });
  }, 500);
},
    handleCasuarn = function handleCasuarn() {
  if ($(".JScasuarnItems").length > 0) {
    var e = function e(_e) {
      var t = $(".JScasuarnItem").outerWidth();
      $(".JScasuarnItems").css({
        transform: "translate(".concat(-t * _e / fontHtml, "rem,0)")
      }), $(".JScasuarnBtn").removeClass("_current"), $(".JScasuarnBtn").eq(_e).addClass("_current"), $(".JScasuarnImage").removeClass("_current"), $(".JScasuarnImage[data-id=\"".concat(_e, "\"]")).addClass("_current");
    };

    $(document).on("click", ".JScasuarnBtn", function () {
      s.index = $(this).index(), e(s.index);
    });
    var t = document.querySelector(".JScasuarnItems"),
        s = {
      startX: 0,
      moveX: 0,
      lastX: 0,
      flag: !1,
      index: 0,
      start: function start(e) {
        this.startX = e.changedTouches ? e.changedTouches[0].pageX : e.pageX, this.flag = !0;
      },
      move: function move(t) {
        if (this.flag) {
          if (this.moveX = this.startX - (t.changedTouches ? t.changedTouches[0].pageX : t.pageX), this.moveX > 30) return this.index == $(".JScasuarnItem").length - 1 || (this.index++, this.flag = !1, e(this.index)), !1;
          if (this.moveX < -30) return 0 == this.index || (this.index--, this.flag = !1, e(this.index)), !1;
        }
      },
      end: function end() {
        this.flag = !1;
      }
    };
    t.addEventListener("mousedown", function (e) {
      s.start(e);
    }), t.addEventListener("mousemove", function (e) {
      s.move(e);
    }), t.addEventListener("mouseup", function () {
      s.end();
    }), t.addEventListener("touchstart", function (e) {
      s.start(e);
    }), t.addEventListener("touchmove", function (e) {
      s.move(e);
    }), t.addEventListener("touchend", function () {
      s.end();
    });

    var i = document.querySelector(".JScasuarnServicesItems"),
        n = {
      startX: 0,
      moveX: 0,
      lastX: 0,
      flag: !1,
      index: 0,
      length: $(".JScasuarnServicesItem").length,
      item: $(".JScasuarnServicesItems").outerWidth() / $(".JScasuarnServicesItem").length,
      full: Math.round($(".JScasuarnServicesBox").outerWidth() / ($(".JScasuarnServicesItems").outerWidth() / $(".JScasuarnServicesItem").length)),
      start: function start(e) {
        this.startX = e.changedTouches ? e.changedTouches[0].pageX : e.pageX, this.flag = !0;
      },
      move: function move(e) {
        if (this.flag) {
          if (this.moveX = this.startX - (e.changedTouches ? e.changedTouches[0].pageX : e.pageX), this.moveX > 30) return this.index == this.length - this.full || ($(".JScasuarnArrow").removeClass("_dis"), this.index == this.length - this.full - 1 && $('.JScasuarnArrow[data-dir="next"]').addClass("_dis"), this.index++, this.flag = !1, o(this.index)), !1;
          if (this.moveX < -30) return 0 == this.index || ($(".JScasuarnArrow").removeClass("_dis"), 1 == this.index && $('.JScasuarnArrow[data-dir="prev"]').addClass("_dis"), this.index--, this.flag = !1, o(this.index)), !1;
        }
      },
      end: function end() {
        this.flag = !1;
      }
    },
        o = function o(e) {
      $(".JScasuarnServicesItems").css({
        transform: "translate(".concat(-e * n.item / fontHtml, "rem,0)")
      });
    };

    $(document).on("click", ".JScasuarnArrow", function () {
      var e = $(this).attr("data-dir");
      Math.round($(".JScasuarnServicesBox").outerWidth() / n.item);

      switch ($(".JScasuarnArrow").removeClass("_dis"), e) {
        case "prev":
          if (0 == n.index) return !1;
          1 == n.index && $(this).addClass("_dis"), n.index--;
          break;

        case "next":
          if (n.index == n.length - n.full) return !1;
          n.index == n.length - n.full - 1 && $(this).addClass("_dis"), n.index++;
      }

      o(n.index);
    }), i.addEventListener("mousedown", function (e) {
      n.start(e);
    }), i.addEventListener("mousemove", function (e) {
      n.move(e);
    }), i.addEventListener("mouseup", function () {
      n.end();
    }), i.addEventListener("touchstart", function (e) {
      n.start(e);
    }), i.addEventListener("touchmove", function (e) {
      n.move(e);
    }), i.addEventListener("touchend", function () {
      n.end();
    });
  }
},
    handleRopaScreen = function handleRopaScreen() {
  $(window).scroll(function () {
    if ($(".JSslid").length > 0) {
      var e = $(".JSslid").outerHeight(),
          t = $(".JSslidItem").outerHeight(),
          s = t / ($(window).height() / 2);

      if ($(window).scrollTop() <= $(".JSslid").offset().top - $(window).height() / 2 && $(".JSslidItem").css({
        transform: "translate3d(0,0,0)"
      }), $(window).scrollTop() > $(".JSslid").offset().top - $(window).height() / 2 && ($(window).scrollTop() - ($(".JSslid").offset().top - $(window).height() / 2)) * s <= t - e) {
        var _e2 = $(window).scrollTop() - ($(".JSslid").offset().top - $(window).height() / 2);

        $(".JSslidItem").css({
          transform: "translate3d(0,-".concat(_e2 * s / fontHtml, "rem,0)")
        });
      }

      ($(window).scrollTop() - ($(".JSslid").offset().top - $(window).height() / 2)) * s >= t - e && $(".JSslidItem").css({
        transform: "translate3d(0,-".concat((t - e) / fontHtml, "rem,0)")
      });
    }
  });
};

var default_placeholder, height_input, curry_selector, css_object;
$(".JSplaceholderAppdate").each(function () {
  default_placeholder = $(this).attr("placeholder"), height_input = parseInt($(this).height()) + parseInt($(this).css("padding")), $(this).wrap("<div class='JSelemTrans inputBox'></div>"), $(this).attr("placeholder", ""), $(this).after("<label class='JSelemTrans inputBox__label'>" + default_placeholder + "</label>"), css_object = $(this).css("margin-top"), $(this).closest(".inputBox").css({
    "margin-top": css_object
  }), css_object = $(this).css("margin-right"), $(this).closest(".inputBox").css({
    "margin-right": css_object
  }), css_object = $(this).css("margin-bottom"), $(this).closest(".inputBox").css({
    "margin-bottom": css_object
  }), css_object = $(this).css("margin-left"), $(this).closest(".inputBox").css({
    "margin-left": css_object
  }), $(this).css({
    margin: "0"
  });
}), $(document).on("click", ".inputBox__label", function () {
  $(this).prev().focus(), $(this).closest(".inputBox").find(".inputBox__error").removeClass("_active");
});

var check_val = function check_val() {
  $(".JSplaceholderAppdate").each(function () {
    curry_selector = $(this).closest(".inputBox").find(".inputBox__label"), 0 != $(this).val() ? (curry_selector.addClass("_active"), $(this).is(":focus") && $(this).closest(".inputBox").find(".inputBox__label").addClass("_active")) : $(this).is(":focus") ? (curry_selector.addClass("_active"), $(this).closest(".inputBox").find(".inputBox__error").removeClass("_active")) : curry_selector.removeClass("_active");
  });
};

setInterval(check_val, 10), $(function () {
  return !1;
});

var menu = function menu() {
  setTimeout(function () {
    $(".JSmenu").addClass("_active"), $(".JSdots").removeClass("_hidden"), $(".JSname").removeClass("_hidden"), $(".JSchat").removeClass("_hidden");
  }, speed), $(".JSmenuOpen").click(function () {
    $(".JSmenuList").fadeIn(10).css({
      display: "flex"
    }), $(".JSmenuOpen").fadeOut(10), $(".JSmenuClose").fadeIn(10), windowFix(scroll);
  }), $(".JSmenuClose").click(function () {
    $(".JSmenuList").fadeOut(10), $(".JSmenuOpen").fadeIn(10), $(".JSmenuClose").fadeOut(10), windowFixRemove(scroll);
  });
},
    menuCase = function menuCase() {
  $(window).scroll(function () {
    $(".JSmenuCaseFix").length > 0 && ($(window).scrollTop() > $(window).height() ? $(".JSmenuCaseFix").addClass("_active") : $(".JSmenuCaseFix").removeClass("_active"));
  });
};

var fontHtml, scroll, windowFix, windowFixRemove, window_width, getDate;
$(".JSnavBtn").click(function () {
  $(".JSnavBox").toggleClass("_active"), $(this).toggleClass("_active");
}), window.onload = function () {
  $(".js-main-loader").remove(), adaptive(), bodyFix(), word(), step(), portfolio(), select(), doneItem(), slider(), quiz(), menu(), sendForm(), taxiSlider(), share(), menuCase(), grGateAnimate(), handleRopaScreen(), handleCasuarn(), $(window).scroll(function (e) {
    if ($(document).scrollTop() < 50 && !window.canScroll) return e.preventDefault(), !1;
  }), $(window).trigger("scroll");
  var e = !0;
  $(window).scroll(function () {
    $(".body__banner").length > 0 && e && $(window).scrollTop() > $("html").outerHeight() / 2 && ($(".body__banner").fadeIn(300).css({
      display: "flex"
    }), e = !1);
  }), $(".body__bannerClose").click(function () {
    $(".body__banner").fadeOut(300);
  }), setTimeout(function () {
    $("[data-src]").each(function () {
      $(this).attr("src", $(this).data("src"));
    });
  }, 10), $(".JSpriceBtn").click(function () {
    $(".body__price[data-price=\"".concat($(this).attr("data-price"), "\"]")).fadeIn(300), windowFix(scroll);
  }), $(".priceBox__close").click(function () {
    $(this).closest(".body__price").fadeOut(300), windowFixRemove(scroll);
  });
  var t = !0;
  setTimeout(function () {
    $(".JScaseCollageItem").addClass("_active"), t = !1;
  }, 2e3), $(window).scroll(function () {
    $(window).scrollTop() > 20 && t && $(".JScaseCollageItem").addClass("_active");
  }), $(".JSpageUp").click(function () {
    $("html,body").animate({
      scrollTop: 0
    }, 1500);
  }), $(".JStoggleShare").click(function () {
    var e = $(".JSshare").attr("data-state");
    "close" == e ? $(".JSshare").fadeIn(300).css({
      display: "flex"
    }) : $(".JSshare").fadeOut(300), "close" == e ? $(".JSshare").attr("data-state", "open") : $(".JSshare").attr("data-state", "close");
  }), $(".input-file").each(function () {
    var e = $(this),
        t = e.next(".js-labelFile"),
        s = t.html();
    e.on("change", function (e) {
      e.target.files[0].size > 15e6 ? (t.addClass("has-error"), $(".error_size_file").css("display", "block")) : (t.removeClass("has-error"), $(".error_size_file").css("display", "none"));
      var i = "";
      e.target.value && (i = e.target.value.split("\\").pop()), i ? t.addClass("has-file").find(".js-fileName").html(i) : t.removeClass("has-file").html(s);
    });
  });
}, $(".JSopenForm").click(function () {
  $(".JSpopup").addClass("_active"), windowFix(scroll);
}), $(".JScloseForm").click(function () {
  $(".JSpopup").removeClass("_active"), windowFixRemove(scroll);
});

var portfolio = function portfolio() {
  if ($(".sectionPortfolio").length > 0) {
    var e = $(".JScase").offset().top,
        t = $(".sectionPortfolio").outerHeight();
    $(window).resize(function () {
      e = $(".JScase").offset().top, t = $(".sectionPortfolio").outerHeight();
    });
    var s = [];
    $(".JScaseBlock").each(function () {
      s.push($(this).attr("data-caseColor"));
    }), $(".JScaseBg").css({
      background: s[0]
    });
    var i = 0;
    $(window).scroll(function () {
      if ($(window).scrollTop() >= e - $(window).height() / 2 ? $(".JScaseBg").addClass("_active") : $(".JScaseBg").removeClass("_active"), $(window).scrollTop() >= e) {
        $(".JScase").removeClass("_abs"), $(".JScase").addClass("_fix");
        var n = $(window).scrollTop() - e,
            o = parseFloat(($(".sectionPortfolio__caseLineInner").outerWidth() - $(".sectionPortfolio__caseImage").outerWidth()) / ($(".sectionPortfolio").outerHeight() - $(window).height()));
        $(window).scrollTop() < t + e - $(window).height() && ($(".JScaseLay").css({
          transform: "translate(-" + n * o / fontHtml + "rem,0)"
        }), $(".JScaseBlock").each(function () {
          $(this).offset().top - $(window).scrollTop() < 2 * $(window).height() / 3 && (i = $(this).index());
        }), $(".JScaseBg").css({
          background: s[i]
        }));
      } else $(".JScase").removeClass("_fix");

      $(window).scrollTop() >= t + e - $(window).height() && ($(".JScase").removeClass("_fix"), $(".JScase").addClass("_abs"), $(".sectionPortfolio__caseLine").css({
        top: (t - $(window).height()) / fontHtml + "rem"
      }));
    });
  }
},
    quiz = function quiz() {
  var e = $(".JSquizItems").length - 2,
      t = 1,
      s = new FormData(),
      i = {};
  $(".JSquizAll").text(e);
  $(".JSquizBtn").click(function () {
    switch ($(this).attr("data-action")) {
      case "prev":
        t--, 1 == t && $('.JSquizBtn[data-action="prev"]').closest(".JSquizBtnWrap").addClass("_hide");
        break;

      case "next":
        var _e3 = !0;

        if ($(".JSquizItems._curry").find(".JSquizElWrap").each(function () {
          switch ($(this).find(".JSquizEl").attr("type")) {
            case "text":
              _e3 *= "" != $(this).find(".JSquizEl").val() || "false" == $(this).find(".JSquizEl").attr("data-require"), "" == $(this).find(".JSquizEl").val() && "true" == $(this).find(".JSquizEl").attr("data-require") ? $(this).find(".JSquizError").text("Это поле обязательно для заполнения!") : $(this).find(".JSquizError").text("");
              break;

            case "radio":
            case "checkbox":
              _e3 *= $(this).find(".JSquizEl:checked").length > 0 || "false" == $(this).find(".JSquizEl").attr("data-require"), 0 == $(this).find(".JSquizEl:checked").length && "true" == $(this).find(".JSquizEl").attr("data-require") ? $(this).find(".JSquizError").text("Это поле обязательно для заполнения!") : $(this).find(".JSquizError").text("");
              break;

            case "file":
              _e3 *= $(this).find(".JSfilesItems").length > 0 || "false" == $(this).find(".JSquizEl").attr("data-require"), 0 == $(this).find(".JSfilesItems").length && "true" == $(this).find(".JSquizEl").attr("data-require") ? $(this).find(".JSquizError").text("Загрузите фото!") : $(this).find(".JSquizError").text("");
          }
        }), !_e3) return !1;
        t++, $('.JSquizBtn[data-action="prev"]').closest(".JSquizBtnWrap").removeClass("_hide");
    }

    !function () {
      switch ($(".JSquizItems").removeClass("_curry"), $(".JSquizItems[data-id=\"".concat(_t, "\"]")).attr("data-type") ? $(".JSquizItems[data-id=\"".concat(_t, "\"][data-type=\"").concat($('input[name="status"]:checked').attr("data-type"), "\"]")).addClass("_curry") : $(".JSquizItems[data-id=\"".concat(_t, "\"]")).addClass("_curry"), $(".JSquizCurry").text(_t), $(".body__quiz").animate({
        scrollTop: 0
      }, 0), _t) {
        case e:
          i = {}, $(".JSquizNav").remove(), $(".JSquizElWrap").find(".JSquizEl").each(function () {
            switch ($(this).attr("type")) {
              case "text":
                i[$(this).attr("name")] = {
                  name: $(this).attr("name"),
                  value: $(this).val()
                };
                break;

              case "radio":
                i[$(this).attr("name")] = {
                  name: $(this).attr("name"),
                  value: $(this).closest(".JSquizElWrap").find(".JSquizEl:checked").val()
                };
                break;

              case "checkbox":
                i[$(this).attr("name")] = {
                  name: $(this).attr("name"),
                  value: ""
                }, $(this).closest(".JSquizElWrap").find(".JSquizEl:checked").each(function () {
                  i[$(this).attr("name")].value += $(this).val() + ".";
                });
            }

            i[$(this).attr("name")].description = $(this).closest(".JSquizElWrap").attr("data-description");
          }), i.atach = [], $(".JSfilesItems").each(function () {
            i.atach.push($(this).attr("data-name"));
          });

          var _t = function (e) {
            for (var t = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], s = ["a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "v", "w", "x", "y", "z"], i = "", n = 0; n < e; n++) {
              if (Math.random(1, 2) < .5) i += t[Math.ceil(10 * Math.random(1, t.length))];else i += s[Math.ceil(10 * Math.random(1, s.length))];
            }

            return i;
          }(10);

          i.referal = "rubedite.ru/referal/".concat(_t), s.append("info", JSON.stringify(i)), $(".JSref").text("rubedite.ru/referal/".concat(_t)), $(".JSref").attr("href", "rubedite.ru/referal/".concat(_t)), console.log(i), $.ajax({
            method: "POST",
            url: "/modules/sendQuiz.php",
            data: s,
            processData: !1,
            contentType: !1,
            success: function success(e) {
              console.log(e);
            }
          });
      }
    }();
  });
  var n = 0;
  $(document).on("change", ".JSquizFile", function () {
    var e = this.files;
    $.each(e, function (t, i) {
      console.log(t), s.append(n, i), n++;
      var o = e[t],
          a = new FileReader();
      a.onload = function (e) {
        var t = i.name.split(".")[i.name.split(".").length - 1];
        -1 != ["jpg", "jpeg", "png"].indexOf(t.toLowerCase()) ? $(".JSquizFiles").append("<div class=\"JSfilesItems quizBox__fileUploadItems\" data-name=\"".concat(i.name, "\">\n                                                ").concat(i.name, " \u2014 ").concat((i.size / 1024).toFixed(1), "kb\n                                                <img src=\"/img/close.svg\" alt=\"\" class=\"quizBox__fileUploadDelete\">\n                                              </div>")) : $(".JSquizElWrap._file").find(".JSquizError").append("".concat(i.name, " \u2014 \u043D\u0435\u0432\u0435\u0440\u043D\u044B\u0439 \u0444\u043E\u0440\u043C\u0430\u0442!<br>"));
      }, a.readAsDataURL(o);
    });
  }), $(document).on("click", ".quizBox__fileUploadDelete", function () {
    $(this).closest(".JSfilesItems").remove();
  }), $(document).on("click focus input keyup", ".JSquizEl", function () {
    $(this).closest(".JSquizElWrap").find(".JSquizError").text("");
  }), $(".JSbtnQuiz").click(function () {
    switch ($(this).attr("data-action")) {
      case "open":
        $(".body__quiz").fadeIn(300), windowFix(scroll);
        break;

      case "close":
        $(".body__quiz").fadeOut(300), windowFixRemove(scroll);
    }
  });
};

var keys = {
  37: 1,
  38: 1,
  39: 1,
  40: 1
};

function preventDefault(e) {
  (e = e || window.event).preventDefault && e.preventDefault(), e.returnValue = !1;
}

function preventDefaultForScrollKeys(e) {
  if (keys[e.keyCode]) return preventDefault(e), !1;
}

function disableScroll() {
  window.addEventListener && window.addEventListener("DOMMouseScroll", preventDefault, !1), document.addEventListener("wheel", preventDefault, {
    passive: !1
  }), window.onwheel = preventDefault, window.onmousewheel = document.onmousewheel = preventDefault, window.ontouchmove = preventDefault, document.onkeydown = preventDefaultForScrollKeys;
}

function enableScroll() {
  window.removeEventListener && window.removeEventListener("DOMMouseScroll", preventDefault, !1), document.removeEventListener("wheel", preventDefault, {
    passive: !1
  }), window.onmousewheel = document.onmousewheel = null, window.onwheel = null, window.ontouchmove = null, document.onkeydown = null;
}

$(".JSscrollItem").click(function () {
  var e,
      t = $(this).attr("data-scroll");
  e = "index" == t ? 0 : $(".JSscrollBlock[data-scroll=\"".concat(t, "\"]")).offset().top, window_width < 500 && ($(".JSmenuList").fadeOut(300), $(".JSmenuOpen").fadeIn(300), $(".JSmenuClose").fadeOut(300), windowFixRemove(scroll)), $("html,body").animate({
    scrollTop: e
  }, 500);
});

var select = function select() {
  $(document).on("click", ".selectBox__view", function () {
    $(this).closest(".selectBox").toggleClass("_active");
  }), $(document).on("click", ".selectBox__dropItems", function () {
    $(this).closest(".selectBox").find(".selectBox__dropItems").removeClass("_curry"), $(this).addClass("_curry"), $(this).closest(".selectBox").removeClass("_active");
    var e = $(this).text().trim(),
        t = $(this).attr("value");
    $(this).closest(".selectBox").find(".selectBox__support").text(e), $(this).closest(".selectBox").attr("data-curryValue", t), $(this).closest(".selectBox").prev("select").find("option").removeAttr("selected"), $(this).closest(".selectBox").prev("select").find("option[value=\"".concat(t, "\"]")).attr("selected", "selected"), console.log($(this).closest(".selectBox").prev("select").find("option:selected").val());
  }), $(document).on("touchend mouseup", function (e) {
    var t = $(".selectBox");
    t.is(e.target) || 0 !== t.has(e.target).length || t.removeClass("_active");
  }), $(".JScustomeSelect").each(function () {
    $(this).fadeOut(0);
    $(this).find("option").length, $(this).attr("data-selectPlaceholder");
    var e = $(this).find("option:selected").text(),
        t = "<div class=\"selectBox\">\n        <div class=\"selectBox__view\">\n            <span class=\"selectBox__support\">\n                ".concat(e, "\n            </span>\n        </div>\n        <div class=\"JSelemTrans selectBox__drop\">");
    $(this).find("option").each(function () {
      var s;
      s = $.map(this.attributes, function (e) {
        return e.name + ' = "' + e.value + '" ';
      });
      var i = "",
          n = "";
      $(this).val() && s.forEach(function (t) {
        i += t, e == t && (n = " _curry");
      }), t += "<div class=\"JSelemTrans selectBox__dropItems ".concat(n, "\" ").concat(i, ">\n            ").concat($(this).text(), "\n        </div>");
    }), t += "</div>\n        </div>", $(this).after(t);
  });
},
    sendForm = function sendForm() {
  $("form").submit(function (e) {
    e.preventDefault();
    var t = $(this),
        s = !1;
    $(".js-labelFile").hasClass("has-error") && (s = !0);
    var i = new FormData(t.get(0));
    var n = $("input[type=file]").prop("files");
    $.each(n, function (e, t) {
      i.append("photo" + e, t);
    }), i["delete"]("photo"), i.append("web_form_submit", "Y"), s || $.ajax({
      url: t.attr("action"),
      data: i,
      method: "POST",
      contentType: !1,
      processData: !1
    }).done(function (e) {
      $('form').get(0).reset();
      $('.js-fileName').text('Скриншот');
      t.find("input").val(""), $(".body__success").fadeIn(300).css({
        display: "flex"
      }), $(".JSpopup").removeClass("_active"), windowFixRemove(scroll);
    });
  }), $(document).on("keyup", function (e) {
    27 != e.keyCode || $(".body__success").fadeOut(300);
    $(".JSpopup").addClass("_active");
  }), $(".body__success").click(function () {
    $(".body__success").fadeOut(300);
    $(".JSpopup").addClass("_active");
  });
},
    share = function share() {
  var e,
      t = {
    title: $("body").attr("data-title"),
    description: $("body").attr("data-description"),
    image: $("body").attr("data-image")
  },
      s = function s(_s, i) {
    switch (_s) {
      case "vk":
        return e = "http://vkontakte.ru/share.php?", e += "url=" + encodeURIComponent(i), e += "&title=" + encodeURIComponent("Rubedite | ".concat(t.title)), e += "&description=" + encodeURIComponent(t.description), e += "&noparse=true", e += "&image=" + encodeURIComponent(t.image), e;

      case "fb":
        return e = "https://www.facebook.com/sharer/sharer.php?", e += "u=" + encodeURIComponent(i), e += "&title=" + encodeURIComponent("Rubedite | ".concat(t.title)), e += "&description=" + encodeURIComponent(t.description), e += "&noparse=true", e += "&image=" + encodeURIComponent(t.image), e;

      case "tw":
        return e = "https://twitter.com/share?", e += "url=" + encodeURIComponent(i), e += "&text=" + encodeURIComponent("Rubedite | ".concat(t.title)), e += "&description=" + encodeURIComponent(t.description), e += "&image=" + encodeURIComponent(t.image), e;

      case "wa":
        return e = "https://api.whatsapp.com/send?", e += "text=" + encodeURIComponent("Rubedite | ".concat(t.title)), e += "&title=" + encodeURIComponent(t.description), e += "&description=" + encodeURIComponent(t.description), e += "&image=" + encodeURIComponent(t.image), e;
    }
  };

  $(".JSshareIcon").each(function () {
    $(this).attr("href", s($(this).attr("data-share"), window.location.href));
  });
};

var sliderStart;

var slider = function slider() {
  var e = {},
      t = 0;
  $(".JSslider").each(function () {
    var s = 1;
    $(this).find(".JSsliderSlid").each(function () {
      $(this).attr("data-sliderIndex", s), s++;
    });
    var i = {};
    $(this).attr("data-index", t), t++, i.name = $(this).attr("data-sliderName"), i.access = $(this).attr("data-sliderAccess"), i.$this = $(this), i.index = parseInt($(this).attr("data-index")), i.currySlid = $(this).find(".JSsliderSlid._curry"), i.timerId = null, i.timerMoveId = null, i.curryIndex = $(this).find(".JSsliderSlid._curry").index(), i.length = $(this).find(".JSsliderSlid").length, i.align = $(this).attr("data-align"), i.speed = parseFloat($(this).attr("data-speed"));

    for (var _e4 = 0; _e4 < i.length; _e4++) {
      $(this).find(".JSdotBox").append('<div class="JSelemTrans JSdot sliderBox__dot">•</div>');
    }

    $(this).find(".JSdot").eq(i.curryIndex).addClass("_curry"), i.indexDot = $(this).find(".JSdot._curry").index(), i.flag = !0, i.deskType = "rem", i.tableType = "vw", i.mobType = "vw", i.widthDesktopStep = parseFloat($(this).attr("data-desktopStep")), i.widthTableStep = parseFloat($(this).attr("data-tableStep")), i.widthMobileStep = parseFloat($(this).attr("data-mobileStep")), window_width > 500 && (i.widthStep = i.widthDesktopStep, i.type = i.deskType), window_width > 0 && window_width < 500 && (i.widthStep = i.widthMobileStep, i.type = i.mobType), i.val = 0, e[$(this).attr("data-index")] = Object.assign({}, i);
  });
  var s,
      i = {
    lastWidth: window_width,
    dot: function dot() {
      switch (e[s].indexDot) {
        case e[s].length:
          e[s].indexDot = 0;
          break;

        case -1:
          e[s].indexDot = e[s].length - 1;
      }
    },
    "return": function _return() {},
    resize: function resize() {
      this.lastWidth > 500 ? window_width < 500 && this["return"]() : window_width > 500 && this["return"]();
    },
    move: function move(t) {
      this.dot(), clearTimeout(e[s].timerMoveId), e[s].timerMoveId = setTimeout(function () {
        e[s].$this.find(".JSsliderLay").addClass("JStrans"), e[s].$this.find(".JSsliderLay").css({
          transform: "translate(" + -e[s].val + e[s].type + ",0)"
        }), e[s].$this.find(".JSsliderSlid").removeClass("_curry"), e[s].$this.find(".JSsliderSlid").eq(e[s].curryIndex + t).addClass("_curry"), e[s].$this.find(".JSdot").removeClass("_curry"), e[s].$this.find(".JSdot").eq(e[s].indexDot).addClass("_curry");
        var i = e[s].$this.find(".JSsliderSlid._curry").attr("data-sliderIndex");

        switch (e[s].$this.find(".JSsliderCounter").text(i), e[s].name) {
          case "why":
            console.log(i), $(".JSwhyImage").removeClass("_active"), $(".JSwhyImage[data-index=\"".concat(parseInt(i) - 1, "\"]")).addClass("_active");
        }
      }, 20);
    },
    clonePos: function clonePos() {
      e[s].$this.find(".JSsliderLay").removeClass("JStrans"), e[s].$this.find(".JSsliderLay").css({
        transform: "translate(" + -e[s].val + e[s].type + ",0)"
      });
    },
    clone: function clone(t) {
      var _this2 = this;

      switch (e[s].flag = !1, clearTimeout(e[s].timerId), e[s].timerId = setTimeout(function () {
        e[s].flag = !0;
      }, e[s].speed + 20), t) {
        case "left":
          e[s].$this.find(".JSsliderSlid").eq(e[s].length - 1).clone(!0).removeClass("_curry").prependTo(e[s].$this.find(".JSsliderLay")), "center" == e[s].align && (e[s].val += e[s].widthStep / 2, setTimeout(function () {
            e[s].$this.find(".JSsliderSlid").eq(e[s].length).remove(), e[s].val += e[s].widthStep / 2, _this2.clonePos();
          }, e[s].speed + 20)), "left" == e[s].align && (e[s].val += e[s].widthStep, setTimeout(function () {
            e[s].$this.find(".JSsliderSlid").eq(e[s].length).remove();
          }, e[s].speed + 20)), this.clonePos();
          break;

        case "right":
          e[s].$this.find(".JSsliderSlid").eq(0).clone(!0).removeClass("_curry").appendTo(e[s].$this.find(".JSsliderLay")), "center" == e[s].align && (e[s].val -= e[s].widthStep / 2, this.clonePos(), setTimeout(function () {
            e[s].$this.find(".JSsliderSlid").eq(0).remove(), e[s].val -= e[s].widthStep / 2, _this2.clonePos();
          }, e[s].speed + 20)), "left" == e[s].align && setTimeout(function () {
            e[s].$this.find(".JSsliderSlid").eq(0).remove(), e[s].val -= e[s].widthStep, _this2.clonePos();
          }, e[s].speed + 20);
      }
    }
  };
  sliderStart = function sliderStart(t, n) {
    if ("mob" == e[t].access && window_width > 500) return !1;
    if (s = t, !e[s].flag) return !1;
    var o,
        a = n;

    switch (i.clone(a), a) {
      case "left":
        e[s].val -= e[s].widthStep, e[s].indexDot--, o = 0;
        break;

      case "right":
        e[s].val += e[s].widthStep, e[s].indexDot++, o = 1;
    }

    i.move(o);
  }, $(".JSsliderBtn").click(function () {
    sliderStart(parseInt($(this).closest(".JSslider").attr("data-index")), $(this).attr("data-dir"));
  });

  var n = 0,
      o = 0,
      a = 0,
      r = 0,
      l = !0,
      d = !1,
      c = !1,
      u = !0,
      h = document.getElementsByClassName("JSslider"),
      f = function f(e) {
    for (var _e5 = 0; _e5 < h.length; _e5++) {
      for (var _t2 = 0; _t2 < h[_e5].getElementsByTagName("img").length; _t2++) {
        h[_e5].getElementsByTagName("img")[_t2].ondragstart = function () {
          return !1;
        };
      }
    }

    u = !1, e.changedTouches ? (n = e.changedTouches[0].pageX, o = e.changedTouches[0].pageY) : (n = e.pageX, o = e.pageY);
  },
      m = function m(e, t) {
    if (!l || u) return !1;
    var s;
    if (e.changedTouches ? (a = n - e.changedTouches[0].pageX, r = o - e.changedTouches[0].pageY) : (a = n - e.pageX, r = o - e.pageY), c && e.preventDefault(), (Math.abs(r) > Math.abs(a) || d) && !c) return d = !0, !1;
    c = !0, e.preventDefault(), a > 30 && (s = "right", sliderStart(parseInt(t.attr("data-index")), s), a = 0, l = !1), a < -30 && (s = "left", sliderStart(parseInt(t.attr("data-index")), s), a = 0, l = !1);
  },
      p = function p() {
    d = !1, c = !1, u = !0, l = !0;
  };

  for (var _e6 = 0; _e6 < h.length; _e6++) {
    h[_e6].addEventListener("touchstart", function (e) {
      f(e);
    }, {
      passive: !1
    }), h[_e6].addEventListener("touchmove", function (e) {
      m(e, $(this));
    }, {
      passive: !1
    }), h[_e6].addEventListener("touchend", function (e) {
      p();
    }, {
      passive: !1
    }), h[_e6].addEventListener("mousedown", function (e) {
      f(e);
    }, {
      passive: !1
    }), h[_e6].addEventListener("mousemove", function (e) {
      m(e, $(this));
    }, {
      passive: !1
    }), h[_e6].addEventListener("mouseup", function (e) {
      p();
    }, {
      passive: !1
    }), h[_e6].ongragstart = function () {
      return !1;
    };
  }

  $(window).resize(function () {
    i.resize();
  });
},
    step = function step() {
  var e = !0;
  $(window).scroll(function () {
    if ($(".sectionProcess").length > 0 && $(window).scrollTop() > $(".sectionProcess").offset().top - $(window).height() / 2) {
      if (!e) return !1;
      e = !1;
      var t = 0,
          s = [],
          i = 0;
      $(".JSstep").each(function () {
        s.push($(this)), t += 100, setTimeout(function () {
          var e;
          s[i].addClass("_active"), e = s[i], setTimeout(function () {
            e.removeClass("_active");
          }, t + 1e3), i++;
        }, t);
      });
    }
  });
},
    taxiSlider = function taxiSlider() {
  var e = {
    length: $(".sectionTaxiPresentation__imagesSliderItems").length,
    current: 0,
    move: function move() {
      var e = this.current;
      $(".JStaxiSliderLayer").each(function () {
        var t = $(this).find(".JStaxiSliderItems").outerWidth();
        $(this).css({
          transform: "translate(".concat(-t * e / fontHtml, "rem,0)")
        }), $(".JStaxiSliderCounter").text(e + 1);
      });
    }
  };
  $(".JStaxiSliderArrow").click(function () {
    switch ($(this).attr("data-dir")) {
      case "left":
        if (0 == e.current) return !1;
        e.current--;
        break;

      case "right":
        if (e.current == e.length - 1) return !1;
        e.current++;
    }

    e.move();
  });
};

$(".JSteamBlock").click(function () {
  $(".JSteamBlock").removeClass("_active"), $(this).addClass("_active");
});
var speed = 0;

var intervalWord,
    speedWord = 0,
    menuShowAfter = 2500,
    word = function word() {
  if ($(".JSwords").length > 0) {
    (function () {
      var e = function e(_e8, t) {
        var s = _e8 - .5 + Math.random() * (t - _e8 + 1);
        return Math.round(Math.abs(s));
      };

      setTimeout(function () {
        $("body").removeClass("_hidden");
      }, menuShowAfter);
      var t = {},
          s = 0,
          i = $(".JSwords").length / 2;
      $(".JSwords").each(function () {
        $(this).attr("data-word");
        $(this).attr("data-num", s), t[s] = {
          str: $(this).attr("data-word"),
          len: $(this).attr("data-word").length,
          "class": $(this).attr("data-class"),
          num: 0
        }, s++;
      });

      for (var _e7 = 0; _e7 < i; _e7++) {
        $(".header__dot").append('<li class="JSelemTrans JSdot header__dotItems"></li>');
      }

      $(".JSdot:nth-child(1)").addClass("_curry"), speed = t[0].len > t[2].len ? speedWord * t[0].len + menuShowAfter : speedWord * t[2].len + menuShowAfter, menu();

      var n = function n(s, i, _n) {
        var o = _n,
            a = 0,
            r = 0,
            l = e(0, o),
            d = [];

        for (d.push(l); a != o;) {
          l = e(0, _n), d.forEach(function (e) {
            e == l && (r = 1);
          }), 0 == r && (d.push(l), a++), r = 0;
        }

        if (speedWord) {
          var _e9 = setInterval(function () {
            var i = d[t[s].num];
            $(".JSwords[data-num=\"".concat(s, "\"] .JSwordsItem:nth-child(").concat(i, ")")).removeClass("_hidden"), t[s].num++, t[s].num === t[s].len + 1 && (clearInterval(_e9), t[s].num = 0);
          }, speedWord);
        } else $(".JSwords[data-num=\"".concat(s, "\"] .JSwordsItem")).removeClass("_hidden");
      },
          o = function o(e, s) {
        var i = t[e].str,
            o = t[e].len,
            a = t[e]["class"],
            r = "";

        for (var _e10 = 0; _e10 < o; _e10++) {
          r += "<span class=\"JSwordsItem ".concat(a, "__item JSelemTrans JStrans _hidden\">").concat(i[_e10], "</span>");
        }

        $(".JSwords[data-num=\"".concat(e, "\"]")).html(r), s ? setTimeout(function () {
          speedWord = 30, n(e, i, o), $("header").removeClass("fixed-wide");
        }, s) : n(e, i, o);
      },
          a = 0,
          r = function r(e, t, s) {
        if (null != e && (a = e), null == t) a++, a === i + 1 && (a = 1);else switch (t) {
          case "left":
            a--, 0 === a && (a = i);
            break;

          case "right":
            a++, a === i + 1 && (a = 1);
        }
        $(".JSwords1 .JSwords").removeClass("_curry"), $(".JSwords1 .JSwords:nth-child(".concat(a, ")")).addClass("_curry"), $(".JSwords2 .JSwords").removeClass("_curry"), $(".JSwords2 .JSwords:nth-child(".concat(a, ")")).addClass("_curry");
        var n = $(".JSwords1 .JSwords:nth-child(".concat(a, ")")).attr("data-num");
        o(n);
        var r = $(".JSwords2 .JSwords:nth-child(".concat(a, ")")).attr("data-num");
        o(r, s), $(".JSdot").removeClass("_curry"), $(".JSdot:nth-child(".concat(a, ")")).addClass("_curry"), a++, a === i + 1 && (a = 1);
      };

      r(a, null, 1e3);
      var l = setInterval(function () {
        r(a, 0);
      }, 1e4);
      $(".JSdot").click(function () {
        var e = $(this).index();
        r(e), clearInterval(l), l = setInterval(function () {
          r(a, 0);
        }, 1e4);
      });

      var d,
          c,
          u,
          h,
          f,
          m,
          p = function p(e) {
        r(a, !1, e), clearInterval(l), l = setInterval(function () {
          r(1);
        }, 1e4);
      },
          S = !0,
          w = document.getElementsByClassName("JSwordSwipe");

      for (var _e11 = 0; _e11 < w.length; _e11++) {
        w[_e11].addEventListener("touchstart", function (e) {
          d = e.changedTouches[0].pageX;
        }), w[_e11].addEventListener("touchmove", function (e) {
          S && (c = d - e.changedTouches[0].pageX, h = Math.abs(u - e.changedTouches[0].pageY), c > 20 && (f = "left", S = !1, p(f)), c < -20 && (f = "right", S = !1, p(f)), (c > 20 || c < -20) && h < 20 && e.preventDefault());
        }, {
          passive: !1
        }), w[_e11].addEventListener("touchend", function (e) {
          c = 0, clearTimeout(m), m = setTimeout(function () {
            S = !0;
          }, 500);
        });
      }
    })();
  }
};