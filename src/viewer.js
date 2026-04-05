var $$ = function(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); };

function setStyle(sel, prop, val) {
  $$(sel).forEach(function(el) { el.style[prop] = val; });
}

function colors() {
  setStyle('.short', 'backgroundColor', '');
  setStyle('.long', 'backgroundColor', '');
  if (document.getElementById('colors_box').checked) {
    setStyle('.selected .short', 'backgroundColor', '#F5D9BC');
    setStyle('.selected .long', 'backgroundColor', '#C8DCE3');
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
  if (document.getElementById('colors_box').checked) {
    setStyle('.selected .short', 'backgroundColor', '#F5D9BC');
    setStyle('.selected .long', 'backgroundColor', '#C8DCE3');
  }
}

function updateVisuals() {
  scansion(); colors(); caesura(); feet();
}

function selectnext() {
  var sel = document.querySelector('.selected');
  if (sel && sel.nextElementSibling) {
    sel.nextElementSibling.classList.add('selected');
    sel.classList.remove('selected');
    updateVisuals();
  }
}

function selectprev() {
  var sel = document.querySelector('.selected');
  if (sel && sel.previousElementSibling) {
    sel.previousElementSibling.classList.add('selected');
    sel.classList.remove('selected');
    updateVisuals();
  }
}

document.addEventListener('DOMContentLoaded', function() {
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
  document.getElementById('feet_box').addEventListener('click', feet);
  document.getElementById('caesura_box').addEventListener('click', caesura);
  document.getElementById('scansion_box').addEventListener('click', scansion);

  document.addEventListener('keyup', function(e) {
    if (e.key === 'ArrowUp') selectprev();
    if (e.key === 'ArrowDown') selectnext();
  });

  // Propagate .speech class to siblings until .newpara
  $$('.speech').forEach(function(el) {
    var next = el.nextElementSibling;
    while (next && !next.classList.contains('newpara')) {
      next.classList.add('speech');
      next = next.nextElementSibling;
    }
  });

});
