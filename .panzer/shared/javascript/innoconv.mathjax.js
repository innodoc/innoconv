/*************************************************************
 *
 *  innoconv.mathjax.js
 *
 *  Implements the \num command inspired by the siunitx package. It uses
 *  dot or comma as decimal marker depending on the HTML lang attribute.
 *
 *  We allow \num{0.23} and \num{0,23} to define decimal fractions.
 *
 *  Use \decmarker to output the decimal marker.
 *
 */

 MathJax.Extension.innoconv = {};

MathJax.Hub.Register.StartupHook("TeX Jax Ready", function() {
  var TEX = MathJax.InputJax.TeX;
  var TEXDEF = TEX.Definitions;
  var MML = MathJax.ElementJax.mml;

  var decimalMarker;
  if (document.documentElement.lang.startsWith('de')) {
    decimalMarker = MML.mo(',');
  } else {
    decimalMarker = MML.mo('.');
  }

  TEXDEF.Add({
    macros: {
      decmarker: 'DecimalMarker',
      num: 'Num',
    }
  }, null, true);

  TEX.Parse.Augment({
    DecimalMarker: function(name) {
      this.Push(decimalMarker);
    },
    Num: function(name) {
      var arg = this.GetArgument(name);
      var match = arg.match(/^(\d+)[,.](\d*)$/);
      if (!match) {
        TEX.Error(["Could not parse argument in %1: %2", name, arg]);
      }
      this.Push(
        MML.mn(match[1]),
        MML.mrow(decimalMarker).With({class: 'MJX-TeXAtom-ORD'}),
        MML.mn(match[2])
      );
    }
  });

  MathJax.Hub.Startup.signal.Post("TeX innoconv Ready")
});

MathJax.Ajax.loadComplete("[innoconv]innoconv.mathjax.js");
