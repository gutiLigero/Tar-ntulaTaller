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
    if (!res.ok) throw new Error(data.detail || "Authentication error");

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
    if (!res.ok) throw new Error(data.detail || "Orientation failed");

    alert(data.message);
    switchAuthTab("login");
  } catch (err) {
    alert(err.message);
  }
}

function logout() {
  localStorage.clear();
  location.reload();
}

function setupAppView() {
  document.getElementById("app-container").classList.remove("hidden");
  document.getElementById("user-badge").innerText = `ID: ${currentUser.nombre} (${currentUser.rol})`;
  
  if (currentUser.rol === "admin") {
    document.getElementById("admin-tab-btn").classList.remove("hidden");
  }
  loadCatalog();
  loadArchive();
}

function switchMainTab(tab) {
  document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
  document.querySelectorAll(".tab-section").forEach(s => s.classList.add("hidden"));

  if (tab === "procurement") document.getElementById("procurement-section").classList.remove("hidden");
  else if (tab === "processing") document.getElementById("processing-section").classList.remove("hidden");
  else if (tab === "archive") { document.getElementById("archive-section").classList.remove("hidden"); loadArchive(); }
  else if (tab === "admin") { document.getElementById("admin-section").classList.remove("hidden"); loadAdminOrders(); }
  
  event.target.classList.add("active");
}

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
      row.innerHTML = `
        <div>
          <strong style="color:#074D39; font-family:'IBM Plex Mono'; font-size:15px;">${prod.nombre_producto}</strong>
          <p style="color:#7A8B94; font-family:'IBM Plex Mono'; font-size:13px;">$ ${price.toLocaleString()} COP</p>
        </div>
        <button class="btn-lumon" onclick="addToCart(${prod.id}, '${prod.nombre_producto}', ${price})">Requisition</button>
      `;
      container.appendChild(row);
    });
  } catch (err) {
    console.error("Failed to load catalog", err);
  }
}

function addToCart(id, name, price) {
  if (cart[id]) cart[id].cantidad += 1;
  else cart[id] = { id, nombre: name, precio: price, cantidad: 1 };
  
  renderCart();
  showToast(`Item secured: ${name}`);
}

function toggleCartDrawer() {
  document.getElementById("cart-drawer").classList.toggle("open");
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
    container.innerHTML = `<p class="empty-state">Receptacle is empty.</p>`;
  } else {
    items.forEach(item => {
      totalCount += item.cantidad;
      const subtotal = item.precio * item.cantidad;
      totalPrice += subtotal;

      const div = document.createElement("div");
      div.style.marginBottom = "10px";
      div.innerHTML = `
        <strong>${item.cantidad}x ${item.nombre}</strong><br>
        <span style="color:#7A8B94;">$ ${subtotal.toLocaleString()} COP</span>
      `;
      container.appendChild(div);
    });
  }

  counter.innerText = totalCount;
  totalEl.innerText = `$ ${totalPrice.toLocaleString()} COP`;
}

async function checkoutWhatsApp() {
  const items = Object.values(cart);
  if (items.length === 0) return alert("Receptacle is empty.");

  try {
    await fetch(`${API_BASE_URL}/orders/cart`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ items })
    });

    let msg = "Tarántula - Optics & Design Division\nApproved Requisition:\n\n";
    let total = 0;
    items.forEach(it => {
      msg += `▪️ ${it.cantidad}x ${it.nombre}\n`;
      total += it.precio * it.cantidad;
    });
    msg += `\n*Total Allocation:* $ ${total.toLocaleString()} COP\n\nPlease provide transfer coordinates.`;

    cart = {};
    renderCart();
    toggleCartDrawer();
    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank");
  } catch (err) {
    alert("Error logging purchase.");
  }
}

async function handleLabSubmit(e) {
  e.preventDefault();
  const payload = {
    tipo_servicio: document.getElementById("lab-type").value,
    cantidad: parseInt(document.getElementById("lab-qty").value),
    observaciones: document.getElementById("lab-obs").value
  };

  try {
    const res = await fetch(`${API_BASE_URL}/orders/lab`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    alert(data.message);
    document.getElementById("lab-obs").value = "";
  } catch (err) {
    alert("Submission error.");
  }
}

async function loadArchive() {
  try {
    const res = await fetch(`${API_BASE_URL}/orders/my-orders`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const orders = await res.json();
    const container = document.getElementById("archive-container");
    container.innerHTML = "";

    if (orders.length === 0) {
      container.innerHTML = "<p>No data nodes available in your archive.</p>";
      return;
    }

    orders.forEach(o => {
      const card = document.createElement("div");
      card.className = "order-card";
      card.innerHTML = `
        <div>
          <strong>Directive #${o.id} - ${o.item_solicitado} (x${o.cantidad})</strong>
          <p>Status: ${o.estado}</p>
        </div>
        <div>
          ${o.link_descarga ? `<a href="${o.link_descarga}" target="_blank" class="btn-outline">EXTRACT NODE</a>` : '<span style="color:#7A8B94; font-size:12px;">Refining...</span>'}
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
      tr.innerHTML = `
        <td>${o.id}</td>
        <td>${o.nombre}<br><small>${o.email}<br>${o.telefono || '-'}</small></td>
        <td>${o.item_solicitado}</td>
        <td>${o.cantidad}</td>
        <td>
          <select id="status-${o.id}">
            <option value="Recibido en taller" ${o.estado === 'Recibido en taller' ? 'selected' : ''}>Recibido en taller</option>
            <option value="En Proceso Químico" ${o.estado === 'En Proceso Químico' ? 'selected' : ''}>En Proceso Químico</option>
            <option value="Escaneándose" ${o.estado === 'Escaneándose' ? 'selected' : ''}>Escaneándose</option>
            <option value="Listo (Archivos Subidos)" ${o.estado === 'Listo (Archivos Subidos)' ? 'selected' : ''}>Listo (Archivos Subidos)</option>
          </select>
        </td>
        <td><input type="text" id="link-${o.id}" value="${o.link_descarga || ''}" placeholder="Download link" style="width:100px;" /></td>
        <td><button class="btn-outline" onclick="commitAdminUpdate(${o.id})">Commit</button></td>
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
    if (res.ok) showToast(`Directive #${id} committed.`);
  } catch (err) {
    alert("Error updating order.");
  }
}
