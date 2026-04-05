var $$ = function(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); };

function setStyle(sel, prop, val) {
  $$(sel).forEach(function(el) { el.style[prop] = val; });
}

function colors() {
  setStyle('.short', 'backgroundColor', '');
  setStyle('.long', 'backgroundColor', '');
  if (document.getElementById('colors_box').checked) {
    setStyle('.selected .short', 'backgroundColor', '#DDD5EB');
    setStyle('.selected .long', 'backgroundColor', '#C8DCCB');
  }
}

function feet() {
  $$('.footend').forEach(function(el) { el.style.borderRight = ''; });
  if (document.getElementById('feet_box').checked) {
    $$('.selected .footend').forEach(function(el) {
      el.style.borderRight = '2px dashed blue';
    });
  }
}

function diaereses() {
  if (document.getElementById('diaeresis_box').checked) {
    $$('.selected .diaeresis').forEach(function(el) {
      el.style.borderRight = '2px solid blue';
    });
  }
}

function caesura() {
  $$('.caesura').forEach(function(el) {
    var next = el.nextElementSibling;
    if (next) {
      next.style.borderLeft = '';
      next.style.paddingLeft = '';
      next.style.marginLeft = '';
    }
  });
  if (document.getElementById('caesura_box').checked) {
    $$('.selected .caesura').forEach(function(el) {
      var next = el.nextElementSibling;
      if (next) {
        next.style.borderLeft = 'double 3px red';
        next.style.paddingLeft = '1px';
        next.style.marginLeft = '1px';
      }
    });
  }
}

function scansion() {
  $$('.short, .long').forEach(function(el) { el.classList.remove('scansion'); });
  if (document.getElementById('scansion_box').checked) {
    $$('.selected .short, .selected .long').forEach(function(el) {
      el.classList.add('scansion');
    });
  }
}

function updateVisuals() {
  scansion(); colors(); caesura(); feet(); diaereses();
}

function allLines() {
  return $$('.line');
}

function selectLine(line, direction) {
  $$('.selected').forEach(function(s) { s.classList.remove('selected'); });
  line.classList.add('selected');
  updateVisuals();
  var container = document.querySelector('.greektext');
  var rect = line.getBoundingClientRect();
  var cRect = container.getBoundingClientRect();
  var h = cRect.height;
  var relTop = rect.top - cRect.top;
  if (relTop < h * 0.1 || rect.bottom - cRect.top > h * 0.9) {
    var target = direction === 'up' ? h / 3 : h * 2 / 3;
    container.scrollBy({ top: relTop - target, behavior: 'instant' });
  }
}

function selectnext() {
  var lines = allLines();
  var sel = document.querySelector('.selected');
  if (!sel) return;
  var idx = lines.indexOf(sel);
  if (idx < lines.length - 1) {
    selectLine(lines[idx + 1], 'down');
  }
}

function selectprev() {
  var lines = allLines();
  var sel = document.querySelector('.selected');
  if (!sel) return;
  var idx = lines.indexOf(sel);
  if (idx > 0) {
    selectLine(lines[idx - 1], 'up');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  // Lock inner container width so selected verses don't shift centering
  var inner = document.querySelector('.greektext-inner');
  if (inner) inner.style.width = inner.offsetWidth + 'px';

  $$('.line').forEach(function(el) {
    el.addEventListener('click', function() {
      var wasSelected = el.classList.contains('selected');
      $$('.selected').forEach(function(s) { s.classList.remove('selected'); });
      if (!wasSelected) {
        el.classList.add('selected');
      }
      updateVisuals();
    });
  });

  document.getElementById('colors_box').addEventListener('click', colors);
  document.getElementById('feet_box').addEventListener('click', function() { feet(); diaereses() });
  document.getElementById('diaeresis_box').addEventListener('click', function() { feet(); diaereses() });
  document.getElementById('caesura_box').addEventListener('click', caesura);
  document.getElementById('scansion_box').addEventListener('click', scansion);

  document.addEventListener('keydown', function(e) {
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;
    if (!document.querySelector('.selected')) return;
    e.preventDefault();
    if (e.key === 'ArrowUp') selectprev();
    if (e.key === 'ArrowDown') selectnext();
  });

});
