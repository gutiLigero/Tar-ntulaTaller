const API_BASE_URL = "https://backend-tarantula.onrender.com"; 
const WHATSAPP_NUMBER = "573148565655";

let token = localStorage.getItem("tarantula_token");
let currentUser = JSON.parse(localStorage.getItem("tarantula_user") || "null");
let cart = {};

document.addEventListener("DOMContentLoaded", () => {
  if (token && currentUser) {
    setupAppView();
  } else {
    document.getElementById("auth-modal").classList.remove("hidden");
  }
});

function showToast(msg) {
  const t = document.getElementById("toast");
  t.innerText = msg;
  t.style.display = "block";
  setTimeout(() => { t.style.display = "none"; }, 3000);
}

// --- AUTENTICACIÓN ---
function switchAuthTab(tab) {
  document.getElementById("tab-btn-login").classList.toggle("active", tab === "login");
  document.getElementById("tab-btn-register").classList.toggle("active", tab === "register");
  document.getElementById("login-form").classList.toggle("hidden", tab !== "login");
  document.getElementById("register-form").classList.toggle("hidden", tab !== "register");
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error de autenticación.");

    token = data.access_token;
    currentUser = data.user;
    localStorage.setItem("tarantula_token", token);
    localStorage.setItem("tarantula_user", JSON.stringify(currentUser));
    
    document.getElementById("auth-modal").classList.add("hidden");
    setupAppView();
  } catch (err) {
    alert(err.message);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const payload = {
    nombre: document.getElementById("reg-name").value,
    email: document.getElementById("reg-email").value,
    telefono: document.getElementById("reg-phone").value,
    password: document.getElementById("reg-password").value
  };

  try {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Error en el registro.");

    alert("Cuenta creada con éxito. Ya puedes iniciar sesión.");
    switchAuthTab("login");
  } catch (err) {
    alert(err.message);
  }
}

function logout() {
  localStorage.clear();
  location.reload();
}

// --- VISTAS PRINCIPALES ---
function setupAppView() {
  document.getElementById("app-container").classList.remove("hidden");
  document.getElementById("user-badge").innerText = `HOLA, ${currentUser.nombre.toUpperCase()}`;
  
  if (currentUser.rol === "admin") {
    document.getElementById("admin-tab-btn").classList.remove("hidden");
  }
  loadCatalog();
  loadArchive();
}

function switchMainTab(tab) {
  document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-section").forEach(s => s.classList.add("hidden"));

  if (tab === "catalog") document.getElementById("catalog-section").classList.remove("hidden");
  else if (tab === "pickup") document.getElementById("pickup-section").classList.remove("hidden");
  else if (tab === "archive") { document.getElementById("archive-section").classList.remove("hidden"); loadArchive(); }
  else if (tab === "admin") { document.getElementById("admin-section").classList.remove("hidden"); loadAdminOrders(); }
  
  event.target.classList.add("active");
}

// --- CATÁLOGO Y CARRITO ---
async function loadCatalog() {
  try {
    const res = await fetch(`${API_BASE_URL}/catalog`);
    const catalogData = await res.json();
    const container = document.getElementById("catalog-container");
    container.innerHTML = "";

    catalogData.forEach(prod => {
      const price = parseFloat(prod.precio) || 0;
      const row = document.createElement("div");
      row.className = "product-row";
      // NOTA: Se añadieron comillas simples alrededor de '${prod.id}' para que JS lo lea como texto
      row.innerHTML = `
        <div>
          <strong style="color:var(--t-red); font-family:'Archivo Black'; font-size:1.1rem; text-transform:uppercase;">${prod.nombre_producto}</strong>
          <p style="font-weight: 600; margin-top:5px;">$ ${price.toLocaleString()} COP</p>
        </div>
        <button class="btn-secondary" style="margin-left: 10px;" onclick="addToCart('${prod.id}', '${prod.nombre_producto}', ${price})">AGREGAR</button>
      `;
      container.appendChild(row);
    });
  } catch (err) {
    console.error("Error cargando el catálogo", err);
  }
}

function toggleCartDrawer() {
  document.getElementById("cart-drawer").classList.toggle("open");
}

function addDevService(serviceName) {
  const price = serviceName.includes("B/N") ? 25000 : 20000;
  const serviceId = serviceName.includes("B/N") ? 9002 : 9001; 
  addToCart(serviceId, serviceName + " + Digitalizado", price);
}

function addToCart(id, name, price) {
  if (cart[id]) cart[id].cantidad += 1;
  else cart[id] = { id, nombre: name, precio: price, cantidad: 1 };
  
  renderCart();
  showToast(`AGREGADO: ${name}`);
}

function renderCart() {
  const container = document.getElementById("drawer-items");
  const counter = document.getElementById("cart-counter");
  const totalEl = document.getElementById("drawer-total");
  container.innerHTML = "";

  let totalCount = 0;
  let totalPrice = 0;
  const items = Object.values(cart);
  
  if (items.length === 0) {
    container.innerHTML = `<p style="font-weight:600;">El carrito está vacío.</p>`;
  } else {
    items.forEach(item => {
      totalCount += item.cantidad;
      const subtotal = item.precio * item.cantidad;
      totalPrice += subtotal;

      const div = document.createElement("div");
      div.style.borderBottom = "2px solid var(--t-red)";
      div.style.paddingBottom = "10px";
      div.style.marginBottom = "10px";
      div.innerHTML = `
        <strong style="color:var(--t-red); font-family:'Archivo Black';">${item.cantidad}x ${item.nombre}</strong><br>
        <span style="font-weight:600;">$ ${subtotal.toLocaleString()} COP</span>
      `;
      container.appendChild(div);
    });
  }

  counter.innerText = totalCount;
  totalEl.innerText = `$ ${totalPrice.toLocaleString()} COP`;
}

async function checkoutWhatsApp() {
  const items = Object.values(cart);
  if (items.length === 0) return alert("El carrito está vacío.");

  try {
    await fetch(`${API_BASE_URL}/orders/cart`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ items })
    });

    let msg = "🕸️ *TARÁNTULA TALLER - NUEVO PEDIDO* 🕸️\n\nHola, quiero confirmar el siguiente pedido:\n\n";
    let total = 0;
    items.forEach(it => {
      msg += `▪️ ${it.cantidad}x ${it.nombre}\n`;
      total += it.precio * it.cantidad;
    });
    msg += `\n*Total a pagar:* $ ${total.toLocaleString()} COP\n\nQuedo atento para coordinar el pago y la entrega.`;

    cart = {};
    renderCart();
    toggleCartDrawer();
    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank");
  } catch (err) {
    alert("Error procesando el pedido.");
  }
}

// --- DOMICILIOS Y GOOGLE CALENDAR ---
async function schedulePickup(e) {
  e.preventDefault();
  
  const address = document.getElementById("pickup-address").value;
  const date = document.getElementById("pickup-date").value;
  const time = document.getElementById("pickup-time").value;
  const notes = document.getElementById("pickup-notes").value;
  
  const dateTimeStr = `${date} a las ${time}`;
  const fullNotes = `Dirección: ${address} | Fecha: ${dateTimeStr} | Detalles: ${notes}`;

  try {
    await fetch(`${API_BASE_URL}/orders/lab`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ 
        tipo_servicio: "Recogida a Domicilio", 
        cantidad: 1, 
        observaciones: fullNotes 
      })
    });
    
    showToast("¡DOMICILIO AGENDADO!");
    
    const timeline = document.getElementById("timeline-container");
    if(timeline.innerHTML.includes("No hay")) timeline.innerHTML = "";
    
    const card = document.createElement("div");
    card.className = "pickup-card";
    card.innerHTML = `
      <div>
        <h4 style="color:var(--t-red); font-family:'Archivo Black'; font-size:1.2rem; margin-bottom:5px;">RECOGIDA PROGRAMADA</h4>
        <p><strong>Día:</strong> ${date}</p>
        <p><strong>Lugar:</strong> ${address}</p>
      </div>
      <button class="btn-secondary" style="margin-left: 10px;" onclick="generateGCalLink('${date}', '${time}', '${address}', '${notes}')">
        + GOOGLE CALENDAR
      </button>
    `;
    timeline.prepend(card);
    document.getElementById("pickup-form").reset();

  } catch (err) {
    alert("Error al agendar la recogida.");
  }
}

function generateGCalLink(dateStr, timeStr, address, notes) {
  const cleanDate = dateStr.replace(/-/g, '');
  const cleanTime = timeStr.replace(/:/g, '') + '00';
  
  const hour = parseInt(timeStr.split(':')[0]);
  const endHour = (hour + 1).toString().padStart(2, '0');
  const cleanEndTime = `${endHour}${timeStr.split(':')[1]}00`;

  const dates = `${cleanDate}T${cleanTime}/${cleanDate}T${cleanEndTime}`;
  const title = encodeURIComponent("Tarántula Taller - Recogida de Rollos");
  const details = encodeURIComponent(`Detalles de recogida: ${notes}\n\nRecuerda tener los rollos listos.`);
  const location = encodeURIComponent(address);
  
  const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dates}&details=${details}&location=${location}`;
  window.open(url, '_blank');
}

// --- ARCHIVO Y ADMIN ---
async function loadArchive() {
  try {
    const res = await fetch(`${API_BASE_URL}/orders/my-orders`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const orders = await res.json();
    const container = document.getElementById("archive-container");
    container.innerHTML = "";

    if (orders.length === 0) {
      container.innerHTML = "<p style='font-weight:600;'>No tienes pedidos recientes.</p>";
      return;
    }

    orders.forEach(o => {
      const card = document.createElement("div");
      card.className = "order-card";
      card.innerHTML = `
        <div>
          <strong style="font-family:'Archivo Black'; color:var(--t-red);">ORDEN #${o.id} - ${o.item_solicitado} (x${o.cantidad})</strong>
          <p style="margin-top:5px; font-weight:600;">Estado: ${o.estado}</p>
        </div>
        <div>
          ${o.link_descarga ? `<a href="${o.link_descarga}" target="_blank" class="btn-secondary" style="text-decoration:none;">DESCARGAR SCANS</a>` : '<span style="font-weight:600; color:var(--t-red);">En proceso...</span>'}
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error(err);
  }
}

async function loadAdminOrders() {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/orders`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const orders = await res.json();
    const tbody = document.getElementById("admin-orders-tbody");
    tbody.innerHTML = "";

    orders.forEach(o => {
      const tr = document.createElement("tr");
      tr.style.borderBottom = "2px solid var(--t-red)";
      tr.innerHTML = `
        <td style="padding:10px; border-right:2px solid var(--t-red);"><strong>#${o.id}</strong></td>
        <td style="padding:10px; border-right:2px solid var(--t-red);">${o.nombre}<br><small>${o.telefono || '-'}</small></td>
        <td style="padding:10px; border-right:2px solid var(--t-red);"><strong>${o.item_solicitado}</strong> (x${o.cantidad})<br><small>${o.tipo_servicio}</small></td>
        <td style="padding:10px; border-right:2px solid var(--t-red);">
          <select id="status-${o.id}" style="margin:0; padding:5px; width:100%;">
            <option value="Recibido en taller" ${o.estado === 'Recibido en taller' ? 'selected' : ''}>Recibido en taller</option>
            <option value="En Proceso Químico" ${o.estado === 'En Proceso Químico' ? 'selected' : ''}>En Proceso Químico</option>
            <option value="Escaneándose" ${o.estado === 'Escaneándose' ? 'selected' : ''}>Escaneándose</option>
            <option value="Listo (Archivos Subidos)" ${o.estado === 'Listo (Archivos Subidos)' ? 'selected' : ''}>Listo (Archivos Subidos)</option>
          </select>
        </td>
        <td style="padding:10px; border-right:2px solid var(--t-red);">
          <input type="text" id="link-${o.id}" value="${o.link_descarga || ''}" placeholder="Link Drive" style="margin:0; padding:5px; width:100px;" />
        </td>
        <td style="padding:10px;">
          <button class="btn-primary" style="padding: 5px 10px;" onclick="commitAdminUpdate(${o.id})">GUARDAR</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
  }
}

async function commitAdminUpdate(id) {
  const nuevo_estado = document.getElementById(`status-${id}`).value;
  const link_descarga = document.getElementById(`link-${id}`).value;

  try {
    const res = await fetch(`${API_BASE_URL}/admin/orders/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ nuevo_estado, link_descarga })
    });
    if (res.ok) showToast(`ORDEN #${id} ACTUALIZADA.`);
  } catch (err) {
    alert("Error al actualizar la orden.");
  }
}
