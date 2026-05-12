/**
 * GRUPO DEWILL - WEB APP LOGIC
 */

// ========== PRODUCT DATA ==========
const products = [
    {
        id: 1,
        name: "Casco de Seguridad MSA V-Gard",
        category: "seguridad",
        description: "Casco de ala frontal con suspensión de trinquete. Alta resistencia a impactos y diseño ergonómico.",
        image: "assets/product_safety.png",
        specs: ["Material: Polietileno de alta densidad", "Norma: ANSI Z89.1", "Talla: Ajustable"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 2,
        name: "Botas de Seguridad Dielectricas",
        category: "seguridad",
        description: "Botas de cuero con puntera de composite. Resistentes a descargas eléctricas y aceites.",
        image: "assets/product_safety.png",
        specs: ["Puntera: Composite", "Suela: Antideslizante", "Protección: 18kV"],
        docs: [{ name: "Certificación.pdf", link: "#" }]
    },
    {
        id: 3,
        name: "Juego de Llaves Mixtas Stanley",
        category: "herramientas",
        description: "Set de 12 piezas de llaves combinadas (milimétricas). Acero cromo vanadio de alta calidad.",
        image: "assets/product_tools.png",
        specs: ["Piezas: 12", "Acabado: Cromo mate", "Medidas: 8-24mm"],
        docs: [{ name: "Manual de Uso.pdf", link: "#" }]
    },
    {
        id: 4,
        name: "Taladro Percutor Bosch Professional",
        category: "herramientas",
        description: "Potente taladro para perforación en concreto, metal y madera. Motor de alto rendimiento.",
        image: "assets/product_tools.png",
        specs: ["Potencia: 750W", "Velocidad: Variable", "Peso: 1.8kg"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 5,
        name: "Limpiador Desengrasante Industrial",
        category: "limpieza",
        description: "Solución concentrada para remover grasas pesadas en maquinaria y pisos industriales.",
        image: "assets/product_cleaning.png",
        specs: ["Presentación: Galón/Bidón", "pH: Alcalino", "Biodegradable: Sí"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },
    {
        id: 6,
        name: "Kit de Absorción de Derrames",
        category: "limpieza",
        description: "Kit completo para control de derrames de hidrocarburos y químicos en planta.",
        image: "assets/product_cleaning.png",
        specs: ["Capacidad: 20 Galones", "Incluye: Paños, Cordones, EPP"],
        docs: [{ name: "Guía de Respuesta.pdf", link: "#" }]
    },
    {
        id: 7,
        name: "Cable Eléctrico Indeco NMT",
        category: "electrico",
        description: "Cable para instalaciones eléctricas industriales y domésticas. Alta conductividad.",
        image: "assets/product_electrical.png",
        specs: ["Calibre: 12 AWG", "Tensión: 600V", "Colores: Rojo, Negro, Verde"],
        docs: [{ name: "Especificaciones.pdf", link: "#" }]
    },
    {
        id: 8,
        name: "Tablero Eléctrico IP65",
        category: "electrico",
        description: "Caja de distribución metálica con protección contra polvo y agua. Ideal para exteriores.",
        image: "assets/product_electrical.png",
        specs: ["Material: Acero Inoxidable", "Grado: IP65", "Medidas: 400x300x200mm"],
        docs: [{ name: "Plano.pdf", link: "#" }]
    }
];

// ========== STATE MANAGEMENT ==========
let quoteList = JSON.parse(localStorage.getItem('dewill_quote')) || [];
let currentFilter = 'all';

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    renderProducts();
    updateQuoteUI();
    setupEventListeners();
    initHeroAnimations();
});

function setupEventListeners() {
    // Scroll event for navbar
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ========== PRODUCT RENDERING ==========
function renderProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    grid.innerHTML = '';
    
    const filteredProducts = currentFilter === 'all' 
        ? products 
        : products.filter(p => p.category === currentFilter);

    filteredProducts.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card animate-fade-up';
        card.innerHTML = `
            <div class="product-img-wrap">
                <img src="${product.image}" alt="${product.name}">
                <span class="product-category-tag">${product.category}</span>
            </div>
            <div class="product-info">
                <h3>${product.name}</h3>
                <p class="product-desc">${product.description}</p>
                <div class="product-actions">
                    <button class="btn-icon" onclick="openProductModal(${product.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-add" onclick="addToQuote(${product.id})">
                        <i class="fas fa-plus"></i> Cotizar
                    </button>
                </div>
            </div>
        `;
        grid.appendChild(card);
    });
}

function filterProducts(category, btn) {
    currentFilter = category;
    
    // Update active button UI
    if (btn) {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    }
    
    renderProducts();
    
    // Scroll to products section if not already there
    const section = document.getElementById('productos');
    section.scrollIntoView({ behavior: 'smooth' });
}

// ========== QUOTE LOGIC ==========
function addToQuote(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    const exists = quoteList.find(item => item.id === productId);
    if (exists) {
        exists.quantity = (exists.quantity || 1) + 1;
        saveQuote();
        updateQuoteUI();
        showToast(`Cantidad aumentada: ${exists.quantity}`, 'success');
        return;
    }

    const newItem = { ...product, quantity: 1 };
    quoteList.push(newItem);
    saveQuote();
    updateQuoteUI();
    showToast('Agregado a la lista de cotización', 'success');
}

function updateQuantity(productId, delta) {
    const item = quoteList.find(p => p.id === productId);
    if (!item) return;

    item.quantity = (item.quantity || 1) + delta;
    if (item.quantity < 1) item.quantity = 1;
    
    saveQuote();
    updateQuoteUI();
}

function removeFromQuote(productId) {
    quoteList = quoteList.filter(item => item.id !== productId);
    saveQuote();
    updateQuoteUI();
}

function clearQuote() {
    if (confirm('¿Estás seguro de limpiar toda la lista?')) {
        quoteList = [];
        saveQuote();
        updateQuoteUI();
    }
}

function saveQuote() {
    localStorage.setItem('dewill_quote', JSON.stringify(quoteList));
}

function updateQuoteUI() {
    const badge = document.getElementById('cartBadge');
    const quoteItems = document.getElementById('quoteItems');
    const quoteEmpty = document.getElementById('quoteEmpty');
    const quoteFooter = document.getElementById('quoteFooter');
    const totalCount = document.getElementById('quoteTotalCount');

    badge.innerText = quoteList.length;
    totalCount.innerText = quoteList.length;

    if (quoteList.length === 0) {
        quoteEmpty.style.display = 'block';
        quoteItems.style.display = 'none';
        quoteFooter.style.display = 'none';
    } else {
        quoteEmpty.style.display = 'none';
        quoteItems.style.display = 'block';
        quoteFooter.style.display = 'flex';

        quoteItems.innerHTML = '';
        quoteList.forEach(item => {
            const div = document.createElement('div');
            div.className = 'quote-item';
            div.innerHTML = `
                <img src="${item.image}" class="quote-item-img">
                <div class="quote-item-info">
                    <h4>${item.name}</h4>
                    <div class="quote-item-controls">
                        <div class="quantity-selector">
                            <button class="qty-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
                            <span class="qty-val">${item.quantity || 1}</span>
                            <button class="qty-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                        </div>
                        <button class="btn-remove" onclick="removeFromQuote(${item.id})" title="Eliminar">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </div>
                </div>
            `;
            quoteItems.appendChild(div);
        });
    }
}

function toggleQuotePanel() {
    const panel = document.getElementById('quotePanel');
    const overlay = document.getElementById('quoteOverlay');
    panel.classList.toggle('open');
    overlay.classList.toggle('open');
}

function sendQuoteToWhatsApp() {
    if (quoteList.length === 0) return;

    let message = "Hola Grupo Dewill, me gustaría solicitar una cotización para los siguientes productos:\n\n";
    quoteList.forEach((item, index) => {
        message += `${index + 1}. [Cant: ${item.quantity || 1}] ${item.name}\n`;
    });
    message += "\nPor favor, envíenme los precios y tiempos de entrega. ¡Gracias!";

    const encodedMessage = encodeURIComponent(message);
    window.open(`https://wa.me/51977585654?text=${encodedMessage}`, '_blank');
}

// ========== MODAL LOGIC ==========
let currentModalProductId = null;

function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    currentModalProductId = productId;
    
    document.getElementById('modalProductImage').src = product.image;
    document.getElementById('modalCategory').innerText = product.category;
    document.getElementById('modalTitle').innerText = product.name;
    document.getElementById('modalDescription').innerText = product.description;

    // Specs
    const specsList = document.getElementById('modalSpecs');
    specsList.innerHTML = '<h4><i class="fas fa-list-check"></i> Especificaciones</h4>';
    const ul = document.createElement('ul');
    product.specs.forEach(spec => {
        const li = document.createElement('li');
        li.innerText = spec;
        ul.appendChild(li);
    });
    specsList.appendChild(ul);

    // Docs
    const docsList = document.getElementById('modalDocuments');
    docsList.innerHTML = '';
    product.docs.forEach(doc => {
        const a = document.createElement('a');
        a.href = doc.link;
        a.className = 'btn-outline-sm';
        a.innerHTML = `<i class="fas fa-file-pdf"></i> ${doc.name}`;
        docsList.appendChild(a);
    });

    // WhatsApp Link
    const waLink = document.getElementById('modalWhatsAppLink');
    const waMsg = `Hola Grupo Dewill, solicito información sobre: ${product.name}`;
    waLink.href = `https://wa.me/51977585654?text=${encodeURIComponent(waMsg)}`;

    document.getElementById('productModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeProductModal() {
    document.getElementById('productModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function addToQuoteFromModal() {
    if (currentModalProductId) {
        addToQuote(currentModalProductId);
        closeProductModal();
    }
}

// ========== UTILS ==========
function showToast(message, type = 'success') {
    // Basic implementation of a toast if needed, or just console for now
    console.log(`[${type}] ${message}`);
    // You could implement a small div toast here
}

function initHeroAnimations() {
    // Particles or simple intersection observers
    const options = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-up');
                observer.unobserve(entry.target);
            }
        });
    }, options);

    document.querySelectorAll('.section-header, .glass-card, .why-card').forEach(el => {
        observer.observe(el);
    });
}
