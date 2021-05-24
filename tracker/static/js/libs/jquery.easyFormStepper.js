/**
 * Author: Artem Smirnov <tonakai.personal@gmail.com>
 * easyFormStepper
 * to provide easy interface to step throw form
 * v.001
 */
(function ($) {
  $.easyFormStepper = function (el, options) {
    var defaults = {
      eventSpace: "easyFormStepper",
      questionContainer: "",
      inputSelector: "input",
      buttonNextSelector: "",
      buttonPrevSelector: "",
      buttonSubmitSelector: "",
      buttonCancelSelector: "",
      canSkipValidation: true,
      onClose: function ($element) { return $element; },
      onStart: function ($element) { return $element; },
      onStepStart: function (step, $element) { return [step, $element]; },
      onStepSubmit: function (step, $element) { return [step, $element]; },
      onStepSkip: function () { return true; },
      onStepValidation: function (step, $element, submitted) { return [step, $element, submitted]; },
      onSubmit: function (answers) { return answers; },
      onCancel: function () { return true; },
      transition: function (step, newStep, fn) { return [step, newStep, fn]; }
    };

    var KEY_ESCAPE = 27;
    var KEY_ENTER = 13;

    var plugin = this;
    var current_question = 0;
    var step = false;
    var steps = false;
    var aStepsSkipped = [];

    var $element = $(el);
    var validateStep = function (submitted) {
      if (step === false) { return true; }
      if (!plugin.settings.onStepValidation(step, $element, submitted)) { return plugin.settings.canSkipValidation; }
      return true;
    };
    var hasPrevStep = function () {
      return current_question > 0;
    };

    var canSubmit = function () {
      var elStep = false;
      var i = 0;
      if (aStepsSkipped.length > 0) {
        return false;
      }
      for (i = steps.length - 1; i >= 0; i--) {
        elStep = $(steps[i]);
        if(elStep && !plugin.settings.onStepValidation(elStep, $element, false) ) {
          return false;
        }
      }
      return true;
    };
    var hasNextStep = function () {
      return (steps.length - 1 > current_question);
    };
    var updateButtons = function () {
      $(plugin.settings.buttonNextSelector).prop('disabled', !hasNextStep() || !validateStep(false));
      $(plugin.settings.buttonPrevSelector).prop('disabled', !hasPrevStep());
      $(plugin.settings.buttonSubmitSelector).prop('disabled', !canSubmit());
    };
    var setCurrentStep = function (iStepKey) {
      var $newStep = steps[iStepKey];
      current_question = iStepKey;
      if (!$newStep) {
        return false;
      }
      plugin.settings.transition(step, $newStep, function () {
        plugin.settings.onStepStart($newStep, $element);
      });
      step = $newStep;
      updateButtons();
    };
    var bindEvents = function () {
      //cancels
      $(plugin.settings.buttonCancelSelector).bind("click." + plugin.settings.eventSpace, plugin.cancel);
      $(document).bind("keyup." + plugin.settings.eventSpace, function (ev) {
        if (ev.keyCode === KEY_ESCAPE || ev.which === KEY_ESCAPE) {
          plugin.cancel();
        }
        $(document).unbind('keyup.' + plugin.settings.eventSpace);
      });
      $(plugin.settings.questionContainer).on("keyup." + plugin.settings.eventSpace, plugin.settings.inputSelector, function (ev) {
        updateButtons();
        if (ev.keyCode === KEY_ENTER || ev.which === KEY_ENTER) {
          ev.preventDefault();
          plugin.nextStep();
        }
      });
      //form submit
      $(plugin.settings.buttonSubmitSelector).bind("click." + plugin.settings.eventSpace, plugin.submit);
      $(plugin.settings.buttonNextSelector).bind("click." + plugin.settings.eventSpace, plugin.nextStep);
      $(plugin.settings.buttonPrevSelector).bind("click." + plugin.settings.eventSpace, plugin.prevStep);
    };

    plugin.settings = {};

    plugin.cancel = function () {
      plugin.settings.onCancel();
      plugin.close();
    };

    plugin.submit = function () {
      var answers = [];
      var i = 0;
      for (i = steps.length - 1; i >= 0; i--) {
          $(steps[i]).find(plugin.settings.inputSelector).each(function(){
              answers.push($(this).val());
          });
      }
      plugin.settings.onSubmit(answers.reverse());
      plugin.close();
    };

    plugin.close = function () {
      plugin.settings.onClose($element);
    };

    plugin.nextStep = function () {
      if (!hasNextStep()) {
        if (aStepsSkipped.length === 0) {
          plugin.submit();
        } else {
          setCurrentStep(aStepsSkipped.pop());
        }
        return false;
      }
      if (validateStep(true)) {
        plugin.settings.onStepSubmit();
        setCurrentStep(current_question + 1);
        return true;
      }
      if (!plugin.settings.canSkipValidation) {
        return false;
      }
      plugin.settings.onStepSkip();
      aStepsSkipped.push(current_question);
      setCurrentStep(current_question + 1);
    };

    plugin.prevStep = function () {
      if (current_question === 0) {
        return false;
      }
      setCurrentStep(current_question - 1);
    };


    plugin.init = function () {
      plugin.settings = $.extend({}, defaults, options);
      steps = $element.find(plugin.settings.questionContainer);
      bindEvents();
      current_question = -1;
      plugin.nextStep();
    };

    plugin.init();
    plugin.settings.onStart($element);
  };
  $.fn.easyFormStepper = function (options) {
    return this.each(function () {
      if (undefined === $(this).data('easyFormStepper')) {
        var plugin = new $.easyFormStepper(this, options);
        $(this).data('easyFormStepper', plugin);
      }
    });
  };
})(jQuery);