let currentPage = 1; let pageCount = 1; let debounceTimer;
const $ = (id) => document.getElementById(id);
const currency = (value) => new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'USD' }).format(Number(value));
function message(text) { $('message').textContent = text; }
async function loadProducts() {
  const params = new URLSearchParams({ page: String(currentPage), pageSize: '20', sort: 'created_at', direction: 'desc' });
  if ($('search').value.trim()) params.set('q', $('search').value.trim());
  if ($('category').value) params.set('category', $('category').value);
  $('product-rows').innerHTML = '<tr><td colspan="5">Cargando productos…</td></tr>';
  try {
    const response = await fetch(`/api/products?${params}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudieron cargar productos.');
    pageCount = Math.max(1, data.pages);
    $('product-rows').innerHTML = data.items.map(p => `<tr><td><strong>${escapeHtml(p.name)}</strong><br><small>${escapeHtml(p.sku)}</small></td><td>${escapeHtml(p.category)}</td><td class="right">${currency(p.price)}</td><td class="right">${p.stock < 10 ? `<strong style="color:#9a6500">${p.stock}</strong>` : p.stock}</td><td class="right"><button class="button secondary" data-delete="${p.id}">Archivar</button></td></tr>`).join('') || '<tr><td colspan="5">No hay productos con esos filtros.</td></tr>';
    $('summary').textContent = `${data.total.toLocaleString('es-MX')} productos · consulta ${data.queryMs} ms`;
    $('page-label').textContent = `Página ${currentPage} de ${pageCount}`;
    $('prev').disabled = currentPage <= 1; $('next').disabled = currentPage >= pageCount;
  } catch (error) { $('product-rows').innerHTML = ''; message(error.message); }
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char])); }
$('search').addEventListener('input', () => { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { currentPage = 1; loadProducts(); }, 250); });
$('category').addEventListener('change', () => { currentPage = 1; loadProducts(); });
$('prev').addEventListener('click', () => { if (currentPage > 1) { currentPage--; loadProducts(); } });
$('next').addEventListener('click', () => { if (currentPage < pageCount) { currentPage++; loadProducts(); } });
$('product-rows').addEventListener('click', async event => {
  const button = event.target.closest('[data-delete]'); if (!button) return;
  if (!confirm('¿Archivar este producto? Se conservará en la base de datos.')) return;
  const response = await fetch(`/api/products/${button.dataset.delete}`, { method: 'DELETE' });
  const data = await response.json();
  if (!response.ok) { message(data.error || 'No se pudo archivar.'); return; }
  message('Producto archivado correctamente.'); loadProducts();
});
$('product-form').addEventListener('submit', async event => {
  event.preventDefault(); message('');
  const form = new FormData(event.currentTarget);
  const payload = Object.fromEntries(form.entries());
  payload.price = Number(payload.price); payload.stock = Number(payload.stock);
  const response = await fetch('/api/products', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const data = await response.json();
  if (!response.ok) { message(typeof data.error === 'string' ? data.error : Object.values(data.error || {}).join(' ')); return; }
  event.currentTarget.reset(); message('Producto creado correctamente.'); currentPage = 1; loadProducts();
});
$('bulk').addEventListener('click', async () => {
  const category = $('category').value || prompt('Escribe la categoría exacta para actualizar:', 'Electrónica');
  if (!category) return;
  const percentText = prompt('Porcentaje de ajuste (ej. 10 o -5):', '10');
  if (percentText === null) return;
  const percent = Number(percentText);
  if (!Number.isFinite(percent) || percent < -90 || percent > 500) { message('Ingresa un porcentaje entre -90 y 500.'); return; }
  const response = await fetch('/api/products/bulk-price', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ category, percent }) });
  const data = await response.json();
  message(response.ok ? `Precios actualizados: ${data.updated} producto(s).` : data.error || 'No se pudo actualizar.');
  loadProducts();
});
loadProducts();
