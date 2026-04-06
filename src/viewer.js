// Copyright (C) 2026 Ioan Andrei Nicolae
// SPDX-License-Identifier: GPL-3.0-only

var $$ = function(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); };

function setStyle(sel, prop, val) {
  $$(sel).forEach(function(el) { el.style[prop] = val; });
}

function toggleState(id) {
  return parseInt(document.getElementById(id).dataset.state || '0');
}

function scope(state) {
  if (state === 2) return '';
  if (state === 1) return '.selected ';
  return null;
}

/* Overlays that need expanded syllable layout to render properly */
var EXPAND_TOGGLES = ['scansion_box', 'colors_box', 'bridges_box', 'homodynia_box',
                      'caesura_box', 'feet_box', 'diaeresis_box'];

function updateExpanded() {
  var needsExpand = EXPAND_TOGGLES.some(function(id) { return toggleState(id) === 2; });
  $$('.line').forEach(function(el) {
    if (needsExpand) {
      el.classList.add('expanded');
    } else {
      el.classList.remove('expanded');
    }
  });
}

function colors() {
  setStyle('.short', 'backgroundColor', '');
  setStyle('.long', 'backgroundColor', '');
  var s = scope(toggleState('colors_box'));
  if (s !== null) {
    setStyle(s + '.short', 'backgroundColor', '#DDD5EB');
    setStyle(s + '.long', 'backgroundColor', '#C8DCCB');
  }
}

function feet() {
  $$('.footend').forEach(function(el) { el.style.borderRight = ''; });
  var s = scope(toggleState('feet_box'));
  if (s !== null) {
    $$(s + '.footend').forEach(function(el) {
      el.style.borderRight = '2px dashed blue';
    });
  }
}

function diaereses() {
  var s = scope(toggleState('diaeresis_box'));
  if (s !== null) {
    $$(s + '.diaeresis').forEach(function(el) {
      el.style.borderRight = '2px solid blue';
    });
  }
}

function bridges() {
  $$('.bridge').forEach(function(el) {
    el.classList.remove('show-bridge');
    el.style.removeProperty('--bridge-w');
    el.style.removeProperty('--bridge-l');
  });
  var s = scope(toggleState('bridges_box'));
  if (s !== null) {
    $$(s + '.bridge').forEach(function(el) {
      var next = el.nextElementSibling;
      if (next) {
        var mid1 = el.offsetLeft + el.offsetWidth / 2;
        var mid2 = next.offsetLeft + next.offsetWidth / 2;
        el.style.setProperty('--bridge-w', (mid2 - mid1) + 'px');
        el.style.setProperty('--bridge-l', (el.offsetWidth / 2) + 'px');
        el.classList.add('show-bridge');
      }
    });
  }
}

function homodynia() {
  $$('.homodynia').forEach(function(el) { el.classList.remove('show-homodynia'); });
  var s = scope(toggleState('homodynia_box'));
  if (s !== null) {
    $$(s + '.homodynia').forEach(function(el) {
      el.classList.add('show-homodynia');
    });
  }
}

function caesura() {
  $$('.caesura, .met-caesura').forEach(function(el) {
    var next = el.nextElementSibling;
    if (next) {
      next.style.borderLeft = '';
      next.style.paddingLeft = '';
      next.style.marginLeft = '';
    }
  });
  var s = scope(toggleState('caesura_box'));
  if (s !== null) {
    $$(s + '.met-caesura').forEach(function(el) {
      var next = el.nextElementSibling;
      if (next) {
        next.style.borderLeft = 'double 3px #999';
        next.style.paddingLeft = '1px';
        next.style.marginLeft = '1px';
      }
    });
    $$(s + '.caesura').forEach(function(el) {
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
  var s = scope(toggleState('scansion_box'));
  if (s !== null) {
    $$(s + '.short, ' + s + '.long').forEach(function(el) {
      el.classList.add('scansion');
    });
  }
}

function updateVisuals() {
  updateExpanded();
  scansion(); colors(); caesura(); feet(); diaereses(); bridges(); homodynia();
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

  // Main button toggles off (0) <-> selected (1)
  $$('.toggle-main').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var group = btn.parentElement;
      var state = parseInt(group.dataset.state || '0');
      group.dataset.state = (state === 0) ? 1 : 0;
      updateVisuals();
    });
  });

  // Small "all" button toggles between current state and all (2)
  $$('.toggle-all').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var group = btn.parentElement;
      var state = parseInt(group.dataset.state || '0');
      group.dataset.state = (state === 2) ? 1 : 2;
      updateVisuals();
    });
  });

  // Legend popup
  var overlay = document.getElementById('legend-overlay');
  document.getElementById('legend_btn').addEventListener('click', function() {
    overlay.classList.remove('hidden');
  });
  document.getElementById('legend-close').addEventListener('click', function() {
    overlay.classList.add('hidden');
  });
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) overlay.classList.add('hidden');
  });

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      overlay.classList.add('hidden');
      return;
    }
    if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;
    if (!document.querySelector('.selected')) return;
    e.preventDefault();
    if (e.key === 'ArrowUp') selectprev();
    if (e.key === 'ArrowDown') selectnext();
  });

});
