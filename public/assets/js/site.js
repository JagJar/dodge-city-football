// Local enhancements only. Historical content and ordinary links work without JS.
document.documentElement.classList.add('js');
const nav = document.querySelector('.main-nav');
const menu = document.querySelector('.menu-toggle');
menu?.addEventListener('click', () => {
  const expanded = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(expanded));
  nav.classList.toggle('expanded', expanded);
});
document.querySelectorAll('.submenu-toggle').forEach(button => {
  const setOpen = open => {
    button.setAttribute('aria-expanded', String(open));
    button.parentElement.classList.toggle('open', open);
  };
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    setOpen(open);
  });
  const desktopHover = () => matchMedia('(hover: hover) and (min-width: 601px)').matches;
  button.parentElement.addEventListener('pointerenter', () => { if (desktopHover()) setOpen(true); });
  button.parentElement.addEventListener('pointerleave', () => {
    if (desktopHover() && !button.parentElement.contains(document.activeElement)) setOpen(false);
  });
  button.parentElement.addEventListener('focusout', event => {
    if (!button.parentElement.contains(event.relatedTarget)) setOpen(false);
  });
});
nav?.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  const open = event.target.closest('li.open');
  if (open) {
    const toggle = open.querySelector('.submenu-toggle');
    open.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); toggle.focus();
  } else {
    nav.classList.remove('expanded'); menu.setAttribute('aria-expanded', 'false'); menu.focus();
  }
});
const tabs = [...document.querySelectorAll('[role="tab"]')];
function activateTab(tab, focus = false) {
  tabs.forEach(item => {
    const active = item === tab;
    item.setAttribute('aria-selected', String(active)); item.tabIndex = active ? 0 : -1;
    document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
  });
  if (focus) tab.focus();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activateTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); activateTab(tabs[next], true); }
  });
});
function manualCarousel(container, items, attribute) {
  if (!container || !items.length) return;
  let current = 0;
  container.querySelectorAll(`[${attribute}]`).forEach(button => button.addEventListener('click', () => {
    current = (current + Number(button.getAttribute(attribute)) + items.length) % items.length;
    items.forEach((item, index) => { item.hidden = index !== current; });
  }));
}
manualCarousel(document.querySelector('.ticker'), [...document.querySelectorAll('.ticker>div>a')], 'data-ticker');
manualCarousel(document.querySelector('.sponsor-rotation'), [...document.querySelectorAll('.sponsor-rotation>a')], 'data-sponsor');
const search = document.getElementById('roster-search');
search?.addEventListener('input', () => {
  const query = search.value.trim().toLocaleLowerCase();
  const rows = [...document.querySelectorAll('#roster-table tbody tr')];
  let count = 0;
  rows.forEach(row => { row.hidden = !row.textContent.toLocaleLowerCase().includes(query); if (!row.hidden) count++; });
  document.getElementById('roster-count').textContent = `${count} of ${rows.length} archived player entries`;
  document.getElementById('roster-empty').hidden = count !== 0;
});
