const search = document.querySelector('input[type="search"]');
const cards = [...document.querySelectorAll('.card')];
search.addEventListener('input', () => {
  const term = search.value.trim().toLowerCase();
  cards.forEach(card => card.hidden = !card.textContent.toLowerCase().includes(term));
  document.querySelector('.empty').hidden = cards.some(card => !card.hidden);
  document.querySelector('blockquote').hidden = Boolean(term);
});
const now = new Date();
document.querySelector('#date').textContent = new Intl.DateTimeFormat('en-GB', {weekday:'short',day:'numeric',month:'short',year:'numeric'}).format(now).toUpperCase();
document.querySelector('#date').dateTime = now.toISOString().slice(0,10);
const hour = now.getHours();
document.querySelector('.greeting').textContent = `Good ${hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening'}, Paolo`;
const theme = document.querySelector('.theme');
function setTheme(light) {
  document.body.classList.toggle('light',light);
  theme.setAttribute('aria-label', `Switch to ${light ? 'dark' : 'light'} theme`);
  theme.textContent = light ? '☾' : '☀';
}
try { setTheme(localStorage.getItem('analytics-theme') === 'light'); } catch {}
theme.addEventListener('click', () => {
  const light = !document.body.classList.contains('light');
  setTheme(light);
  try { localStorage.setItem('analytics-theme',light ? 'light' : 'dark'); } catch {}
});
async function refreshStatus() {
  try {
    const response = await fetch('/api/status', {cache:'no-store'});
    if (!response.ok) throw new Error('Status unavailable');
    const states = await response.json();
    for (const card of cards) {
      const state = states.find(item => item.id === card.dataset.id);
      const status = card.querySelector('.status');
      status.classList.remove('online','offline');
      if (!state) { status.querySelector('.status-label').textContent = 'Status unavailable'; continue; }
      status.classList.add(state.online ? 'online' : 'offline');
      status.querySelector('.status-label').textContent = state.online ? 'Online' : 'Offline';
      card.querySelector('a').href = state.url;
    }
  } catch {
    cards.forEach(card => {
      const status = card.querySelector('.status');
      status.classList.remove('online','offline');
      status.querySelector('.status-label').textContent = 'Status unavailable';
    });
  }
}
refreshStatus();
setInterval(refreshStatus, 30000);
