const boardMessage = document.getElementById('board-message');
const zones = [...document.querySelectorAll('.dropzone')];
let draggedCard = null; let originalStatus = null;
function say(text) { boardMessage.textContent = text; }
function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char])); }
function createCard(item) {
  const card = document.createElement('article');
  card.className = 'task-card'; card.draggable = true; card.dataset.id = item.id; card.dataset.status = item.status;
  card.innerHTML = `<div class="task-meta"><span>${escapeHtml(item.kind)}</span><span>${escapeHtml(item.priority)}</span></div><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.details || 'Sin detalles adicionales.')}</p><p style="margin-top:12px;font-size:9px">ID · ${item.id}</p>`;
  card.addEventListener('dragstart', event => { draggedCard = card; originalStatus = card.dataset.status; card.classList.add('dragging'); event.dataTransfer.setData('text/plain', String(item.id)); event.dataTransfer.effectAllowed = 'move'; });
  card.addEventListener('dragend', () => { card.classList.remove('dragging'); zones.forEach(zone => zone.classList.remove('over')); draggedCard = null; });
  return card;
}
function updateCounts() { document.querySelectorAll('.kanban-column').forEach(column => { column.querySelector('header span').textContent = column.querySelectorAll('.task-card').length; }); }
async function load() {
  const response = await fetch('/api/operations'); const items = await response.json();
  if (!response.ok) { say(items.error || 'No se pudieron cargar tareas.'); return; }
  zones.forEach(zone => zone.replaceChildren());
  items.forEach(item => { const zone = zones.find(z => z.dataset.status === item.status); if (zone) zone.appendChild(createCard(item)); });
  updateCounts();
}
zones.forEach(zone => {
  zone.addEventListener('dragover', event => { event.preventDefault(); zone.classList.add('over'); event.dataTransfer.dropEffect = 'move'; });
  zone.addEventListener('dragleave', event => { if (!zone.contains(event.relatedTarget)) zone.classList.remove('over'); });
  zone.addEventListener('drop', async event => {
    event.preventDefault(); zone.classList.remove('over');
    if (!draggedCard || draggedCard.dataset.status === zone.dataset.status) return;
    const card = draggedCard; const oldStatus = originalStatus; const newStatus = zone.dataset.status;
    zone.appendChild(card); card.dataset.status = newStatus; updateCounts(); say('Guardando cambio…');
    try {
      const response = await fetch('/api/operations', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: Number(card.dataset.id), status: newStatus }) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Error al guardar.');
      say('Cambio guardado en PostgreSQL.');
    } catch (error) {
      const oldZone = zones.find(z => z.dataset.status === oldStatus); oldZone.appendChild(card); card.dataset.status = oldStatus; updateCounts();
      say(`${error.message} Se restauró el estado anterior.`);
    }
  });
});
load().catch(() => say('Error de conexión al cargar el tablero.'));
