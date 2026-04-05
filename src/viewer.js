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
  setStyle('.short', 'background', '');
  setStyle('.long', 'background', '');
  if (document.getElementById('scansion_box').checked) {
    $$('.selected .short').forEach(function(el) {
      el.style.background = 'transparent url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KPHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjAiIHk9IjAiIHdpZHRoPSI2MCIgaGVpZ2h0PSI0MS4zNzkiIHZpZXdCb3g9IjAsIDAsIDYwLCA0MS4zNzkiPgogIDxnIGlkPSJMYXllcl8xIj4KICAgIDxwYXRoIGQ9Ik0yLjQwOSw3LjM4NyBMMi4yNDMsNy44NDMgTDEuODM0LDkuMTE4IEwxLjQ3NiwxMC41MDcgTDEuMjE0LDExLjg3OSBMMS4wNDgsMTMuMjI4IEwwLjk3NiwxNC41NDUgTDAuOTkyLDE1LjgyOCBMMS4wOTQsMTcuMDcgTDEuMjc1LDE4LjI3MiBMMS41MjksMTkuNDI5IEwxLjg1MiwyMC41NDIgTDIuMjM4LDIxLjYxMiBMMi42ODIsMjIuNjM3IEwzLjE3OSwyMy42MjMgTDMuNzI1LDI0LjU2NyBMNC4zMTcsMjUuNDczIEw0Ljk1LDI2LjM0MyBMNS42MjIsMjcuMTc2IEw2LjMzMSwyNy45NzggTDcuMDczLDI4Ljc0NyBMNy44NDYsMjkuNDg1IEw4LjY0OSwzMC4xOTQgTDkuNDgsMzAuODc0IEwxMC4zMzUsMzEuNTI3IEwxMS4yMTUsMzIuMTUzIEwxMi4xMTgsMzIuNzUzIEwxMy4wNCwzMy4zMjggTDEzLjk4MSwzMy44NzYgTDE1LjM5OCwzNC42MzkgTDE3LjM0OSwzNS41OCBMMTkuMzc4LDM2LjQ0MSBMMjEuNDQzLDM3LjIwNiBMMjMuNTM1LDM3Ljg3NyBMMjUuNjQxLDM4LjQ1MiBMMjcuNzUyLDM4LjkzMSBMMjkuODYsMzkuMzE0IEwzMS45NTYsMzkuNTk2IEwzMy41NTIsMzkuNzQ1IEwzNC42MjUsMzkuODEgTDM1LjY1NywzOS44NDUgTDM2LjY4NCwzOS44NTIgTDM3LjcwNiwzOS44MjkgTDM4LjcyMiwzOS43NzYgTDM5LjczNywzOS42OSBMNDAuNzQ3LDM5LjU2OSBMNDEuNzU5LDM5LjQxIEw0Mi43NzMsMzkuMjA5IEw0My43OTMsMzguOTYxIEw0NC44MjMsMzguNjYgTDQ1Ljg2NiwzOC4yOTYgTDQ2LjkyNywzNy44NTkgTDQ4LjAwOCwzNy4zMzUgTDQ5LjExLDM2LjcwNyBMNTAuMjI0LDM1Ljk2IEw1MS4zMzksMzUuMDc2IEw1Mi4wNjUsMzQuNDE3IEw1Mi4wNjUsMzQuNDE3IEM1Mi4xODQsMzQuMzAzIDUyLjMsMzQuMTg2IDUyLjQxNCwzNC4wNjcgTDUyLjQxNCwzNC4wNjcgTDUyLjU4MywzMy44OTEgTDUzLjM2MywzMi45OTYgTDU0LjE1NCwzMS45NDkgTDU0LjgxOCwzMC45MzMgTDU1LjM4MywyOS45NSBMNTUuODcxLDI4Ljk5MyBMNTYuMjk4LDI4LjA1NyBMNTYuNjc5LDI3LjEzNiBMNTcuMTU3LDI1LjgzMyBMNTcuNzE0LDI0LjA3NCBMNTguMTk4LDIyLjI3OSBMNTguNjA3LDIwLjUwNSBMNTguOTUyLDE4Ljc2MyBMNTkuMjQyLDE3LjA2MiBMNTkuNDg0LDE1LjQxOCBMNTkuNjc5LDEzLjg0OCBMNTkuODMzLDEyLjM3IEw1OS45MjMsMTEuMzE0IEw1OS45NzIsMTAuNjQxIEw2MC4wMSwxMC4wMTYgTDYwLjAzOCw5LjQyNSBMNjAuMDU4LDguODY2IEw2MC4wNjksOC4zMzkgTDYwLjA3MSw4LjA1NCBMNjAuMDcxLDguMDU0IEM2MC4wOSw0LjI5OSA1Ni45NCwyLjEyNyA1My4wMzUsMy4yMDIgQzQ5LjEzLDQuMjc3IDQ1Ljk0OCw4LjE5MiA0NS45MjksMTEuOTQ2IEM0NS45MjksMTEuOTQ2IDQ1LjkyOSwxMS45NDYgNDUuOTI5LDExLjk0NiBMNDUuOTI5LDEyLjA1IEw0NS45MjQsMTIuMzcxIEw0NS45MTIsMTIuNzQ3IEw0NS44OTIsMTMuMTc1IEw0NS44NjQsMTMuNjQyIEw0NS44MywxNC4xMzEgTDQ1Ljc2MywxNC45MzUgTDQ1LjY0MywxNi4xMiBMNDUuNDg5LDE3LjM4IEw0NS4zMDIsMTguNjggTDQ1LjA4MywxOS45OSBMNDQuODM0LDIxLjI3NSBMNDQuNTYyLDIyLjQ5NiBMNDQuMjc0LDIzLjYxMSBMNDMuOTY2LDI0LjYzMSBMNDMuNzMzLDI1LjI5NiBMNDMuNjA4LDI1LjYxOSBMNDMuNTA2LDI1Ljg2NiBMNDMuNDM5LDI2LjAyNSBMNDMuNDIyLDI2LjA4NSBMNDMuNDgsMjYuMDMyIEw0My42MzcsMjUuODYzIEw0My43NTcsMjUuNzUzIEw0My41ODYsMjUuOTMzIEw0My45MzUsMjUuNTgzIEw0NC4yNjcsMjUuMyBMNDQuNTMxLDI1LjEyNyBMNDQuNzEsMjUuMDM3IEw0NC43OTcsMjUuMDEyIEw0NC43ODcsMjUuMDM4IEw0NC42ODUsMjUuMDk4IEw0NC40OTUsMjUuMTc5IEw0NC4yMjcsMjUuMjcgTDQzLjg4NiwyNS4zNjMgTDQzLjQ4MSwyNS40NTIgTDQzLjAxOCwyNS41MzMgTDQyLjUwMiwyNS42MDEgTDQxLjk0MywyNS42NTQgTDQxLjMzOSwyNS42OTEgTDQwLjcsMjUuNzEgTDQwLjAyOCwyNS43MSBMMzkuMzI2LDI1LjY5IEwzOC42MzYsMjUuNjUzIEwzNy41MzUsMjUuNTU5IEwzNS45NTksMjUuMzU3IEwzNC4zMzQsMjUuMDcyIEwzMi42NzksMjQuNzA1IEwzMS4wMTMsMjQuMjYgTDI5LjM1NSwyMy43MzggTDI3LjcyLDIzLjE0MiBMMjYuMTI2LDIyLjQ3NyBMMjQuNTYsMjEuNzMyIEwyMy40MjYsMjEuMTI3IEwyMi43MTMsMjAuNzE1IEwyMi4wMjQsMjAuMjkgTDIxLjM2LDE5Ljg1NCBMMjAuNzIzLDE5LjQwNSBMMjAuMTE0LDE4Ljk0NyBMMTkuNTM1LDE4LjQ3OSBMMTguOTg4LDE4LjAwNCBMMTguNDc2LDE3LjUyMyBMMTcuOTk3LDE3LjAzNyBMMTcuNTU1LDE2LjU1IEwxNy4xNSwxNi4wNiBMMTYuNzgzLDE1LjU3MiBMMTYuNDU0LDE1LjA4NyBMMTYuMTY0LDE0LjYwNyBMMTUuOTEyLDE0LjEzNiBMMTUuNjk3LDEzLjY3MyBMMTUuNTE4LDEzLjIyMiBMMTUuMzc0LDEyLjc4NCBMMTUuMjYzLDEyLjM1OSBMMTUuMTgzLDExLjk0OCBMMTUuMTMxLDExLjU0NyBMMTUuMTA1LDExLjE1OSBMMTUuMTA2LDEwLjc3NCBMMTUuMTMyLDEwLjM5MyBMMTUuMTg0LDEwLjAwOCBMMTUuMjY0LDkuNjExIEwxNS40MjMsOS4wNzQgTDE1LjU5MSw4LjYxMyBDMTcuMDA1LDQuNzIyIDE1LjIwMSwxLjI5NCAxMS41NjEsMC45NTYgQzcuOTIxLDAuNjE3IDMuODIzLDMuNDk2IDIuNDA5LDcuMzg3IEwyLjQwOSw3LjM4NyIgZmlsbD0iIzAwMDAwMCIvPgogIDwvZz4KPC9zdmc+Cg==) no-repeat center top';
      el.style.backgroundSize = '0.75em';
    });
    $$('.selected .long').forEach(function(el) {
      el.style.background = 'transparent url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPCFET0NUWVBFIHN2ZyBQVUJMSUMgIi0vL1czQy8vRFREIFNWRyAxLjEvL0VOIiAiaHR0cDovL3d3dy53My5vcmcvR3JhcGhpY3MvU1ZHLzEuMS9EVEQvc3ZnMTEuZHRkIj4KPHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjAiIHk9IjAiIHdpZHRoPSI2MCIgaGVpZ2h0PSI0MS4zNzkiIHZpZXdCb3g9IjAsIDAsIDYwLCA0MS4zNzkiPgogIDxnIGlkPSJMYXllcl8xIj4KICAgIDxwYXRoIGQ9Ik0wLjk1NCwyMC45NzkgTDEuNzUxLDIxLjEyMSBMMy40NTcsMjEuMzkzIEw2LjAyOSwyMS43MjYgTDkuNDYsMjIuMDM1IEwxMi45MDQsMjIuMjA1IEwxNi4zMjQsMjIuMjU0IEwxOS43MTYsMjIuMTk5IEwyMy4wNzUsMjIuMDYxIEwyNi40LDIxLjg1OCBMMzEuMywyMS40NzcgTDM3LjczOSwyMC45MTMgTDQyLjQ3LDIwLjUyNSBMNDUuNTUsMjAuMzE2IEw0OC42MDQsMjAuMTYzIEw1MS42MiwyMC4wOCBMNTMuMDY3LDIwLjA3MSBMNTMuMDY3LDIwLjA3MSBDNTYuODI0LDIwLjA0NCA2MC43MzUsMTYuODU2IDYxLjgwMiwxMi45NTEgQzYyLjg2OSw5LjA0NiA2MC42ODksNS45MDIgNTYuOTMzLDUuOTI5IEM1Ni45MzMsNS45MjkgNTYuOTMzLDUuOTI5IDU2LjkzMyw1LjkyOSBMNTUuMjE0LDUuOTQzIEw1MS44OTMsNi4wMzggTDQ4LjYwMiw2LjIwNSBMNDUuMzI5LDYuNDI4IEw0MC41MTksNi44MjMgTDM0LjIxNSw3LjM3NiBMMjkuNTQ0LDcuNzQxIEwyNi40ODQsNy45MyBMMjMuNDU1LDguMDU5IEwyMC40NTUsOC4xMTMgTDE3LjQ4Miw4LjA3OCBMMTQuNTMxLDcuOTQxIEwxMS41NjYsNy42ODMgTDkuMzQxLDcuNCBMNy44NDgsNy4xNjQgTDcuMDQ2LDcuMDIxIEMzLjUyMSw2LjM5MyAtMC43LDkuMDA5IC0yLjM4MiwxMi44NjMgQy00LjA2NCwxNi43MTggLTIuNTcsMjAuMzUxIDAuOTU0LDIwLjk3OSBMMC45NTQsMjAuOTc5IiBmaWxsPSIjMDAwMDAwIi8+CiAgICA8cGF0aCBkPSJNMjg1LjgyNSw2Mi4wNzQgTDI4NS44MjQsNjIuMDc0IEwyODUuODI0LDYyLjA3NCBDMjg2LjQ1Nyw2Mi4wNzUgMjg4Ljg0LDU4LjAxMyAyOTEuMTQ2LDUzLjAwMiBDMjkzLjQ1Miw0Ny45OTEgMjk0LjgwOSw0My45MjcgMjk0LjE3Niw0My45MjYgTDI5NC4xNzUsNDMuOTI2IEMyOTQuMTc1LDQzLjkyNiAyOTQuMTc1LDQzLjkyNiAyOTQuMTc1LDQzLjkyNiBDMjkzLjU0MSw0My45MjcgMjkxLjE1OCw0Ny45OSAyODguODUyLDUzLjAwMSBDMjg2LjU0Niw1OC4wMTMgMjg1LjE5MSw2Mi4wNzUgMjg1LjgyNSw2Mi4wNzQgTDI4NS44MjUsNjIuMDc0IiBmaWxsPSIjMDAwMDAwIi8+CiAgPC9nPgo8L3N2Zz4K) no-repeat center top';
      el.style.backgroundSize = '1em';
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
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
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
