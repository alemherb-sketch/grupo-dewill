/**
 * GRUPO DEWILL - WEB APP LOGIC
 */

const products = [
    // ===== PINTURAS DECORATIVAS =====
    {
        id: 1,
        name: "Sellador CPP",
        category: "pinturas",
        description: "Sellador acrílico para interiores y exteriores. Base ideal para acabados de calidad.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Sellador Acrílico", "Aplicación: Interior/Exterior", "Rendimiento: 40-50 m²/gal"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 2,
        name: "Temple Fino Sinolit CPP",
        category: "pinturas",
        description: "Temple fino de alta calidad para acabados interiores lisos y uniformes.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Temple Fino", "Aplicación: Interior", "Acabado: Mate"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 3,
        name: "Temple Majestad",
        category: "pinturas",
        description: "Temple económico de buena cobertura para proyectos de gran escala.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Temple Estándar", "Aplicación: Interior", "Presentación: 25 kg"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 4,
        name: "Satinado CPP",
        category: "pinturas",
        description: "Pintura látex satinada lavable de excelente resistencia al frote húmedo.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Látex Satinado", "Acabado: Satinado", "Resistencia: Alta al lavado"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 5,
        name: "Duralatex CPP",
        category: "pinturas",
        description: "Látex acrílico de alta durabilidad para interiores y exteriores. Gran cubrimiento.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Látex Acrílico", "Aplicación: Interior/Exterior", "Rendimiento: 45-55 m²/gal"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 6,
        name: "Latex Pato CPP",
        category: "pinturas",
        description: "Pintura látex económica de buena calidad. Ideal para proyectos con presupuesto ajustado.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Látex Económico", "Aplicación: Interior/Exterior", "Acabado: Mate"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 7,
        name: "Supermate Vencedor",
        category: "pinturas",
        description: "Pintura mate premium de máxima cobertura y excelente rendimiento por galón.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Látex Mate", "Acabado: Mate Premium", "Rendimiento: 50-60 m²/gal"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 8,
        name: "Masterlast Anypsa",
        category: "pinturas",
        description: "Pintura acrílica de alto rendimiento con tecnología anti-hongos y bacterias.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Acrílico Anti-hongos", "Aplicación: Interior/Exterior", "Tecnología: Antibacterial"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 9,
        name: "X3 Gloss Anypsa (Esmalte)",
        category: "pinturas",
        description: "Esmalte sintético de alto brillo para superficies metálicas y de madera.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Esmalte Sintético", "Acabado: Alto Brillo", "Superficies: Metal/Madera"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 10,
        name: "Pintura para Pizarra Anypsa",
        category: "pinturas",
        description: "Pintura especial que convierte cualquier superficie en pizarra acrílica reutilizable.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Pintura Especial", "Uso: Pizarras", "Colores: Negro/Verde"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 11,
        name: "Pintura Fluorescente Anypsa",
        category: "pinturas",
        description: "Pintura de alta visibilidad con pigmentos fluorescentes para señalización y decoración.",
        image: "assets/product_paint.png",
        specs: ["Tipo: Fluorescente", "Uso: Señalización/Decoración", "Visibilidad: Alta"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },

    // ===== PINTURAS DE TRÁFICO =====
    {
        id: 12,
        name: "Pintura para Tráfico Maestro",
        category: "trafico",
        description: "Pintura acrílica para demarcación vial de alta resistencia al desgaste vehicular.",
        image: "assets/product_traffic.png",
        specs: ["Tipo: Acrílica de Tráfico", "Colores: Amarillo/Blanco", "Norma: MTC"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 13,
        name: "Pintura para Tráfico Tamsa",
        category: "trafico",
        description: "Pintura de señalización vial de secado rápido para carreteras y estacionamientos.",
        image: "assets/product_traffic.png",
        specs: ["Tipo: Tráfico Rápido Secado", "Aplicación: Vial", "Durabilidad: Alta"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },

    // ===== EPÓXICOS =====
    {
        id: 14,
        name: "Juego Epóxico Bonn Zincromato",
        category: "epoxicos",
        description: "Sistema epóxico anticorrosivo de dos componentes para protección de estructuras metálicas.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Epóxico 2 Componentes", "Uso: Anticorrosivo", "Base: Zincromato"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 15,
        name: "Juego Epóxico JET POX 2000",
        category: "epoxicos",
        description: "Recubrimiento epóxico de alto espesor para ambientes industriales severos y marinos.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Epóxico Alto Espesor", "Uso: Industrial/Marino", "Resistencia: Química"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 16,
        name: "Juego Epóxico JET 70 MP",
        category: "epoxicos",
        description: "Epóxico multipropósito de alta performance para pisos industriales y estructuras.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Epóxico Multipropósito", "Uso: Pisos/Estructuras", "Acabado: Semi-brillante"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 17,
        name: "Juego Epóxico Anticorrosivo JET 62 ZP",
        category: "epoxicos",
        description: "Primer epóxico rico en zinc para máxima protección anticorrosiva en acero.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Primer Epóxico", "Base: Rico en Zinc", "Protección: Catódica"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 18,
        name: "Juego Epóxico Poliuretano JETHANE 500",
        category: "epoxicos",
        description: "Acabado poliuretano de alto brillo y excelente retención de color. Resistente a UV.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Poliuretano", "Acabado: Alto Brillo", "Resistencia: UV"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 19,
        name: "Juego Epóxico Poliuretano JETHANE 650 HS",
        category: "epoxicos",
        description: "Poliuretano de altos sólidos para acabados de máxima durabilidad industrial.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Poliuretano HS", "Sólidos: Alto contenido", "Uso: Industrial pesado"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 20,
        name: "Barniz Epóxico Alta Duración Anypsa",
        category: "epoxicos",
        description: "Barniz epóxico transparente de dos componentes. Ideal para pisos y superficies de concreto.",
        image: "assets/product_epoxy.png",
        specs: ["Tipo: Barniz Epóxico", "Acabado: Transparente", "Uso: Pisos de concreto"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },

    // ===== SOLVENTES =====
    {
        id: 21,
        name: "Thinner Automotriz A3m",
        category: "solventes",
        description: "Thinner de alta pureza para dilución de pinturas automotrices y lacas.",
        image: "assets/product_thinner.png",
        specs: ["Tipo: Automotriz", "Pureza: Alta", "Uso: Pinturas automotrices"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },
    {
        id: 22,
        name: "Thinner Estándar Expert",
        category: "solventes",
        description: "Solvente de uso general para dilución de esmaltes y pinturas sintéticas.",
        image: "assets/product_thinner.png",
        specs: ["Tipo: Estándar", "Uso: General", "Compatibilidad: Esmaltes/Sintéticos"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },
    {
        id: 23,
        name: "Thinner Acrílico Expert",
        category: "solventes",
        description: "Diluyente especializado para pinturas acrílicas automotrices y de uso industrial.",
        image: "assets/product_thinner.png",
        specs: ["Tipo: Acrílico", "Uso: Automotriz/Industrial", "Evaporación: Media"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },
    {
        id: 24,
        name: "Thinner Acrílico MS1 CMC",
        category: "solventes",
        description: "Thinner acrílico de secado medio para sistemas de pintura base-barniz.",
        image: "assets/product_thinner.png",
        specs: ["Tipo: Acrílico MS1", "Secado: Medio", "Sistema: Base-Barniz"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },
    {
        id: 25,
        name: "Thinner Acrílico Premium CPP",
        category: "solventes",
        description: "Solvente acrílico premium de alta calidad con excelente poder de dilución.",
        image: "assets/product_thinner.png",
        specs: ["Tipo: Acrílico Premium", "Calidad: Premium", "Poder Solvente: Alto"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },
    {
        id: 26,
        name: "Maestrazo Thinner Acrílico",
        category: "solventes",
        description: "Thinner acrílico económico de buen rendimiento para proyectos de gran volumen.",
        image: "assets/product_thinner.png",
        specs: ["Tipo: Acrílico Económico", "Uso: Alto Volumen", "Presentación: Galón/Cilindro"],
        docs: [{ name: "Hoja de Seguridad.pdf", link: "#" }]
    },

    // ===== ACCESORIOS =====
    {
        id: 27,
        name: "Rodillo Peluche Blanco Toretto",
        category: "accesorios",
        description: "Rodillo de peluche blanco profesional para acabados finos en interiores.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Peluche Blanco", "Uso: Interiores", "Acabado: Fino"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 28,
        name: "Rodillo Antigoteo B y P Soprin",
        category: "accesorios",
        description: "Rodillo con tecnología anti-goteo para trabajo limpio y eficiente.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Antigoteo", "Tecnología: Anti-salpicaduras", "Marca: Soprin"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 29,
        name: "Rodillo Peluche Carnero Toretto",
        category: "accesorios",
        description: "Rodillo de fibra de carnero para superficies rugosas y texturadas.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Peluche Carnero", "Uso: Superficies rugosas", "Durabilidad: Alta"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 30,
        name: "Rodillo Espuma Profesional Goya",
        category: "accesorios",
        description: "Rodillo de espuma de alta densidad para acabados ultralisos en esmaltes.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Espuma HD", "Acabado: Ultra liso", "Uso: Esmaltes"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 31,
        name: "Espátula Multiusos ATLAS 4\"",
        category: "accesorios",
        description: "Espátula profesional de acero inoxidable para empaste, rasqueteo y resane.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Multiusos", "Material: Acero Inoxidable", "Tamaño: 4 pulgadas"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 32,
        name: "Espátula Atlas Angular",
        category: "accesorios",
        description: "Espátula angular de precisión para acabados en esquinas y bordes.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Angular", "Uso: Esquinas y bordes", "Material: Acero"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 33,
        name: "Brocha Tumi Nylon",
        category: "accesorios",
        description: "Brocha profesional de filamentos de nylon para todo tipo de pinturas.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Brocha Profesional", "Filamento: Nylon", "Uso: Universal"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 34,
        name: "Spray ABRO Colores Metálicos Premium",
        category: "accesorios",
        description: "Pintura en spray con acabado metálico premium para decoración y retoques.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Spray Metálico", "Acabado: Premium", "Marca: ABRO"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 35,
        name: "Spray ABRO Colores Fluorescentes",
        category: "accesorios",
        description: "Spray de alta visibilidad con colores fluorescentes para señalización rápida.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Spray Fluorescente", "Uso: Señalización", "Marca: ABRO"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    },
    {
        id: 36,
        name: "Spray C&A Colores",
        category: "accesorios",
        description: "Spray multicolor de secado rápido para proyectos de pintura y decoración.",
        image: "assets/product_accessories.png",
        specs: ["Tipo: Spray Multicolor", "Secado: Rápido", "Uso: Pintura/Decoración"],
        docs: [{ name: "Ficha Técnica.pdf", link: "#" }]
    }
];


// ========== STATE MANAGEMENT ==========
let quoteList = JSON.parse(localStorage.getItem('dewill_quote')) || [];
let currentFilter = 'all';
let searchQuery = '';

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', () => {
    // Check URL params for category filter (e.g., productos.html?cat=pinturas)
    const params = new URLSearchParams(window.location.search);
    const catParam = params.get('cat');
    if (catParam && ['pinturas', 'epoxicos', 'solventes', 'trafico', 'accesorios'].includes(catParam)) {
        currentFilter = catParam;
        // Activate the right filter button
        setTimeout(() => {
            const btns = document.querySelectorAll('.filter-btn');
            btns.forEach(b => {
                b.classList.remove('active');
                if (b.dataset.category === catParam) b.classList.add('active');
            });
        }, 100);
    }

    // Only render products client-side if we are on the static page
    // The server-rendered Flask products page has products-grid-new class
    const grid = document.getElementById('productsGrid');
    if (grid && !grid.classList.contains('products-grid-new')) {
        renderProducts();
    }
    updateQuoteUI();
    setupEventListeners();
    initHeroAnimations();
});

function setupEventListeners() {
    // Scroll event for navbar
    window.addEventListener('scroll', () => {
        const navbar = document.getElementById('navbar');
        if (!navbar) return;
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// ========== SEARCH ==========
function searchProducts(query) {
    searchQuery = query.toLowerCase().trim();
    renderProducts();
}

// ========== PRODUCT RENDERING ==========
function renderProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    grid.innerHTML = '';
    
    let filteredProducts = currentFilter === 'all' 
        ? products 
        : products.filter(p => p.category === currentFilter);

    // Apply search filter
    if (searchQuery) {
        filteredProducts = filteredProducts.filter(p =>
            p.name.toLowerCase().includes(searchQuery) ||
            p.description.toLowerCase().includes(searchQuery) ||
            p.category.toLowerCase().includes(searchQuery)
        );
    }

    // Update count display
    const countEl = document.getElementById('countNumber');
    if (countEl) countEl.innerText = filteredProducts.length;

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
function addToQuote(productId, productName = null, productImage = null, color = null, quantity = 1, presentation = null, code = null) {
    // Las paginas de Flask pasan el nombre y la imagen del producto de la base; la lista estatica de arriba
    // es solo para la pagina de demostracion (sus ids 1-36 coinciden con productos reales de la base)
    let product = !productName && typeof products !== 'undefined' ? products.find(p => p.id === productId) : null;

    if (!product && productName) {
        product = {
            id: productId,
            name: productName,
            image: productImage || '/static/assets/product_paint.png',
            category: 'general',
            description: ''
        };
    }
    
    if (!product) return;

    // Match by ID, color, and presentation to support distinct variants
    const exists = quoteList.find(item => item.id === productId && item.color === color && item.presentation === presentation);
    if (exists) {
        exists.quantity = (exists.quantity || 1) + (quantity || 1);
        saveQuote();
        updateQuoteUI();
        showToast(`Cantidad aumentada: ${exists.quantity}`, 'success');
        return;
    }

    const newItem = { 
        ...product, 
        quantity: quantity || 1,
        color: color,
        presentation: presentation,
        code: code   // Codigo (Excel) de la presentacion y el color elegidos; el servidor lo vuelve a calcular al recibir la solicitud
    };

    // Keep image paths relative to static folder neat under Flask
    if (newItem.image && !newItem.image.startsWith('/') && !newItem.image.startsWith('http')) {
        if (newItem.image.startsWith('static/')) {
            newItem.image = '/' + newItem.image;
        } else {
            newItem.image = '/static/' + newItem.image;
        }
    }

    quoteList.push(newItem);
    saveQuote();
    updateQuoteUI();
    showToast('Agregado a la lista de cotización', 'success');
}

function updateQuantity(index, delta) {
    const item = quoteList[index];
    if (!item) return;

    item.quantity = (item.quantity || 1) + delta;
    if (item.quantity < 1) item.quantity = 1;
    
    saveQuote();
    updateQuoteUI();
}

function removeFromQuote(index) {
    quoteList.splice(index, 1);
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

    const infoForm = document.getElementById('clientInfoForm');
    if (quoteList.length === 0) {
        quoteEmpty.style.display = 'block';
        quoteItems.style.display = 'none';
        quoteFooter.style.display = 'none';
        if (infoForm) infoForm.style.display = 'none';
        document.getElementById('btnCart').classList.remove('has-items-alert');
    } else {
        quoteEmpty.style.display = 'none';
        quoteItems.style.display = 'block';
        quoteFooter.style.display = 'flex';
        if (infoForm) infoForm.style.display = 'block';
        document.getElementById('btnCart').classList.add('has-items-alert');

        quoteItems.innerHTML = '';
        quoteList.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'quote-item';
            
            let extraInfo = '';
            if (item.presentation) {
                extraInfo += `<span style="display:block; font-size:0.8rem; color:#666; margin-top:2px;">Pres: <strong>${item.presentation}</strong></span>`;
            }
            if (item.color) {
                // If color is a hex code or color name, we can show a small dot
                const isHex = /^#[0-9A-F]{6}$/i.test(item.color);
                const dot = isHex ? `<span style="background-color:${item.color}; display:inline-block; width:12px; height:12px; border-radius:50%; border:1px solid #ccc; vertical-align:middle; margin-left:4px;"></span>` : '';
                extraInfo += `<span style="display:block; font-size:0.8rem; color:#666; margin-top:2px;">Color: <strong>${item.color}</strong>${dot}</span>`;
            }
            if (item.code) {
                extraInfo += `<span style="display:block; font-size:0.8rem; color:#666; margin-top:2px;">Código: <strong>${item.code}</strong></span>`;
            }

            div.innerHTML = `
                <img src="${item.image || '/static/assets/product_paint.png'}" class="quote-item-img" onerror="this.src='/static/assets/product_paint.png'">
                <div class="quote-item-info">
                    <h4 style="margin-bottom: 4px;">${item.name}</h4>
                    ${extraInfo}
                    <div class="quote-item-controls" style="margin-top: 8px;">
                        <div class="quantity-selector">
                            <button class="qty-btn" onclick="updateQuantity(${index}, -1)"><i class="fas fa-minus"></i></button>
                            <span class="qty-val">${item.quantity || 1}</span>
                            <button class="qty-btn" onclick="updateQuantity(${index}, 1)"><i class="fas fa-plus"></i></button>
                        </div>
                        <button class="btn-remove" onclick="removeFromQuote(${index})" title="Eliminar">
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

// Codigo (Excel) de la presentacion y el color elegidos: la combinacion exacta y, si no existe, la mas general.
// codes: [{p: id de la presentacion o null, c: color en mayusculas o '', code}]
function findVariantCode(codes, presId, colorName) {
    const color = (colorName || '').trim().toUpperCase();
    const find = (p, c) => { const v = codes.find(x => x.p === p && x.c === c); return v ? v.code : null; };
    return find(presId, color) ?? find(presId, '') ?? find(null, color) ?? find(null, '');
}

// ========== SELECTOR DE COTIZACION (tarjetas del catalogo) ==========
// COTIZAR, los colores y las presentaciones de una tarjeta abren este selector con las opciones del producto
// (/api/producto/<id>/opciones); lo que se toca en la tarjeta llega ya elegido. Un producto sin presentaciones
// ni colores se agrega directo, como antes.
const quoteOptionsCache = new Map();
const quoteOptionsState = { product: null, presId: null, color: null, trigger: null };
const SAFE_HEX_RE = /^#[0-9a-f]{3,8}$/i;

function escapeHTML(value) {
    return String(value ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function sameColorName(a, b) {
    return (a || '').trim().toUpperCase() === (b || '').trim().toUpperCase();
}

function loadQuoteOptions(productId) {
    if (!quoteOptionsCache.has(productId)) {
        const request = fetch(`/api/producto/${productId}/opciones`)
            .then(res => { if (!res.ok) throw new Error(`HTTP ${res.status}`); return res.json(); })
            .catch(err => { quoteOptionsCache.delete(productId); throw err; });
        quoteOptionsCache.set(productId, request);
    }
    return quoteOptionsCache.get(productId);
}

// Colores de la presentacion elegida (sin presentaciones: los del producto)
function quoteOptionColors() {
    const { product, presId } = quoteOptionsState;
    if (!product.presentations.length) return product.colors;
    const pres = product.presentations.find(p => p.id === presId);
    return pres ? pres.colors : [];
}

document.addEventListener('click', e => {
    const control = e.target.closest('.premium-product-card [data-quote-open], .premium-product-card [data-quote-color], .premium-product-card [data-quote-pres]');
    if (control) openQuoteOptions(control.closest('.premium-product-card'), control);
});

async function openQuoteOptions(card, control) {
    const productId = parseInt(card.dataset.productId, 10);
    const btn = card.querySelector('.pcr-btn-quote');
    if (btn.getAttribute('aria-busy') === 'true') return;
    const originalHTML = btn.innerHTML;
    btn.setAttribute('aria-busy', 'true');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> COTIZAR';

    let product;
    try {
        product = await loadQuoteOptions(productId);
    } catch (err) {
        console.error('Error loading quote options:', err);
        showToast('No se pudieron cargar las opciones del producto. Inténtalo de nuevo.', 'error');
        return;
    } finally {
        btn.removeAttribute('aria-busy');
        btn.innerHTML = originalHTML;
    }

    if (!product.presentations.length && !product.colors.length) {
        addToQuote(product.id, product.name, product.image, null, 1, null, findVariantCode(product.codes, null, ''));
        return;
    }

    // Presentacion inicial: la tocada en la tarjeta; si se toco un color, la primera que lo tenga; si no, la primera
    const presetPres = parseInt(control.dataset.quotePres, 10);
    const presetColor = control.dataset.quoteColor || '';
    let presId = null;
    if (product.presentations.length) {
        const pres = product.presentations.find(p => p.id === presetPres)
            || (presetColor && product.presentations.find(p => p.colors.some(c => sameColorName(c.name, presetColor))))
            || product.presentations[0];
        presId = pres.id;
    }
    Object.assign(quoteOptionsState, { product, presId, color: null, trigger: control });
    quoteOptionsState.color = presetColor ? quoteOptionColors().find(c => sameColorName(c.name, presetColor)) || null : null;

    document.getElementById('qoImage').src = '/static/' + product.image;
    document.getElementById('qoImage').alt = product.name;
    document.getElementById('qoBrand').textContent = product.brand;
    document.getElementById('qoTitle').textContent = product.name;
    document.getElementById('qoQty').value = 1;
    document.getElementById('qoPresSection').hidden = !product.presentations.length;
    document.getElementById('qoPresentations').innerHTML = product.presentations.map(p =>
        `<button type="button" class="pres-btn" data-pres-id="${p.id}">${escapeHTML(p.name)}</button>`).join('');
    renderQuoteOptions();

    document.body.classList.add('qo-open');
    document.getElementById('quoteOptionsOverlay').classList.add('open');
    const dialog = document.getElementById('quoteOptions');
    dialog.classList.add('open');
    dialog.querySelector('.qo-body').scrollTop = 0;
    // el color tocado en la tarjeta puede estar al final de la lista
    const presetSwatch = dialog.querySelector('.qo-swatch.selected');
    if (presetSwatch) presetSwatch.scrollIntoView({ block: 'nearest' });
    const firstControl = dialog.querySelector('.pres-btn.selected') || dialog.querySelector('.qo-swatch') || dialog.querySelector('#qoAdd');
    firstControl.focus({ preventScroll: true });
}

// Pinta la presentacion y el color elegidos, los colores de esa presentacion y el codigo de la variante
function renderQuoteOptions() {
    const { product, presId, color } = quoteOptionsState;
    document.querySelectorAll('#qoPresentations .pres-btn').forEach(b => {
        const selected = parseInt(b.dataset.presId, 10) === presId;
        b.classList.toggle('selected', selected);
        b.setAttribute('aria-pressed', String(selected));
    });

    const colors = quoteOptionColors();
    document.getElementById('qoColorSection').hidden = !colors.length;
    document.getElementById('qoColorSearchWrap').hidden = colors.length <= 12;
    document.getElementById('qoColorSearch').value = '';
    document.getElementById('qoColorsEmpty').hidden = true;
    document.getElementById('qoColors').innerHTML = colors.map((c, i) => {
        const hex = SAFE_HEX_RE.test(c.hex_code || '') ? c.hex_code : '#cccccc';
        const selected = color && sameColorName(c.name, color.name);
        return `<button type="button" class="qo-swatch${selected ? ' selected' : ''}" data-index="${i}" aria-pressed="${selected}"
                    title="${escapeHTML(c.label)}" aria-label="${escapeHTML(c.label)}">
                    <span class="qo-swatch-dot" style="background:${hex}"></span>
                    ${c.code ? `<span class="qo-swatch-code">#${escapeHTML(c.code)}</span>` : ''}
                </button>`;
    }).join('');
    renderQuoteOptionsCode();
}

// Nombre del color elegido y codigo de la variante (sin codigo cargado, el SKU general del producto)
function renderQuoteOptionsCode() {
    const { product, presId, color } = quoteOptionsState;
    showQuoteColorName(color);
    const code = findVariantCode(product.codes, presId, color ? color.name : '');
    const codeLine = document.getElementById('qoCode');
    codeLine.textContent = code ? `Código: ${code}` : (product.sku ? `SKU: ${product.sku}` : '');
    codeLine.hidden = !codeLine.textContent;
    document.getElementById('qoError').textContent = '';
}

// preview: el color bajo el cursor, que aun no esta elegido
function showQuoteColorName(color, preview = false) {
    const name = document.getElementById('qoColorName');
    name.textContent = color ? color.label : 'Elige un color';
    name.classList.toggle('is-empty', !color);
    name.classList.toggle('is-preview', preview);
}

function closeQuoteOptions() {
    const dialog = document.getElementById('quoteOptions');
    if (!dialog.classList.contains('open')) return;
    dialog.classList.remove('open');
    document.getElementById('quoteOptionsOverlay').classList.remove('open');
    document.body.classList.remove('qo-open');
    const trigger = quoteOptionsState.trigger;
    if (trigger && document.contains(trigger)) trigger.focus({ preventScroll: true });
}

function addFromQuoteOptions(thenSend) {
    const { product, presId, color } = quoteOptionsState;
    if (quoteOptionColors().length && !color) {
        document.getElementById('qoError').textContent = 'Elige un color para cotizar.';
        document.getElementById('qoColorSection').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return;
    }
    const pres = product.presentations.find(p => p.id === presId);
    const qtyInput = document.getElementById('qoQty');
    const quantity = Math.min(9999, Math.max(1, parseInt(qtyInput.value, 10) || 1));
    // el color viaja con su codigo ('AMARILLO LIMON #41'), igual que desde la ficha del producto
    addToQuote(product.id, product.name, product.image, color ? color.label : null, quantity,
               pres ? pres.name : null, findVariantCode(product.codes, presId, color ? color.name : ''));
    closeQuoteOptions();
    // "Agregar y enviar" abre Mi Cotización, donde el cliente completa sus datos y envía la solicitud al panel
    if (thenSend && !document.getElementById('quotePanel').classList.contains('open')) toggleQuotePanel();
}

document.addEventListener('DOMContentLoaded', () => {
    const dialog = document.getElementById('quoteOptions');
    if (!dialog) return;
    const colorsGrid = document.getElementById('qoColors');
    const qtyInput = document.getElementById('qoQty');

    document.querySelectorAll('[data-qo-close]').forEach(el => el.addEventListener('click', closeQuoteOptions));
    document.getElementById('qoAdd').addEventListener('click', () => addFromQuoteOptions(false));
    document.getElementById('qoAddSend').addEventListener('click', () => addFromQuoteOptions(true));

    document.getElementById('qoPresentations').addEventListener('click', e => {
        const btn = e.target.closest('.pres-btn');
        if (!btn) return;
        quoteOptionsState.presId = parseInt(btn.dataset.presId, 10);
        // el color elegido se conserva si la nueva presentacion tambien lo tiene
        const color = quoteOptionsState.color;
        quoteOptionsState.color = color ? quoteOptionColors().find(c => sameColorName(c.name, color.name)) || null : null;
        renderQuoteOptions();
    });

    colorsGrid.addEventListener('click', e => {
        const swatch = e.target.closest('.qo-swatch');
        if (!swatch) return;
        quoteOptionsState.color = quoteOptionColors()[parseInt(swatch.dataset.index, 10)];
        colorsGrid.querySelectorAll('.qo-swatch').forEach(s => {
            s.classList.toggle('selected', s === swatch);
            s.setAttribute('aria-pressed', String(s === swatch));
        });
        renderQuoteOptionsCode();
    });
    // Al pasar el cursor por un color se lee su nombre; al salir vuelve el elegido
    colorsGrid.addEventListener('mouseover', e => {
        const swatch = e.target.closest('.qo-swatch');
        if (swatch) showQuoteColorName(quoteOptionColors()[parseInt(swatch.dataset.index, 10)], !swatch.classList.contains('selected'));
    });
    colorsGrid.addEventListener('mouseleave', () => showQuoteColorName(quoteOptionsState.color));

    document.getElementById('qoColorSearch').addEventListener('input', e => {
        const normalize = s => (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
        const term = normalize(e.target.value);
        const colors = quoteOptionColors();
        let visible = 0;
        colorsGrid.querySelectorAll('.qo-swatch').forEach(s => {
            const show = !term || normalize(colors[parseInt(s.dataset.index, 10)].label).includes(term);
            s.hidden = !show;
            if (show) visible++;
        });
        document.getElementById('qoColorsEmpty').hidden = visible > 0;
    });
    // Enter en el buscador de colores no debe hacer nada mas
    document.getElementById('qoColorSearch').addEventListener('keydown', e => { if (e.key === 'Enter') e.preventDefault(); });

    dialog.querySelectorAll('[data-qo-step]').forEach(btn => btn.addEventListener('click', () => {
        const next = (parseInt(qtyInput.value, 10) || 1) + parseInt(btn.dataset.qoStep, 10);
        qtyInput.value = Math.min(9999, Math.max(1, next));
    }));
    qtyInput.addEventListener('change', () => {
        qtyInput.value = Math.min(9999, Math.max(1, parseInt(qtyInput.value, 10) || 1));
    });

    // Escape cierra; Tab no sale del selector mientras esta abierto
    document.addEventListener('keydown', e => {
        if (!dialog.classList.contains('open')) return;
        if (e.key === 'Escape') {
            closeQuoteOptions();
        } else if (e.key === 'Tab') {
            const focusable = Array.from(dialog.querySelectorAll('button, input')).filter(el => !el.hidden && el.offsetParent !== null);
            const first = focusable[0], last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
    });
});

// ========== QUOTE CLIENT FORM ==========
// DNI/RUC y celular son obligatorios; correo y mensaje, opcionales. El servidor aplica las mismas reglas.
const QUOTE_DOCUMENT_RE = /^(\d{8}|\d{11})$/;
const QUOTE_MOBILE_RE = /^9\d{8}$/;
const QUOTE_EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function onlyDigits(value) {
    return (value || '').replace(/\D/g, '');
}

function normalizeMobile(value) {
    let digits = onlyDigits(value);
    if (digits.length === 11 && digits.startsWith('51')) digits = digits.slice(2);   // +51 987 654 321
    return digits;
}

function readQuoteClient() {
    const read = id => (document.getElementById(id)?.value || '').trim();
    return {
        name: read('clientName'),
        document: onlyDigits(read('clientDocument')),
        company: read('clientCompany'),
        phone: normalizeMobile(read('clientPhone')),
        email: read('clientEmail'),
        message: read('clientMessage')
    };
}

// Devuelve { field, message } con el primer problema del formulario, o null si todo está bien
function validateQuoteClient(client) {
    if (!client.name) return { field: 'clientName', message: 'Ingresa tu nombre completo.' };
    if (!QUOTE_DOCUMENT_RE.test(client.document)) return { field: 'clientDocument', message: 'Ingresa un DNI (8 dígitos) o un RUC (11 dígitos).' };
    if (!QUOTE_MOBILE_RE.test(client.phone)) return { field: 'clientPhone', message: 'Ingresa un celular válido de 9 dígitos (ej. 987654321).' };
    if (client.email && !QUOTE_EMAIL_RE.test(client.email)) return { field: 'clientEmail', message: 'El correo electrónico no es válido.' };
    return null;
}

function documentLabel(documentNumber) {
    return documentNumber.length === 8 ? 'DNI' : 'RUC';
}

document.addEventListener('DOMContentLoaded', () => {
    // DNI/RUC solo admite dígitos; el celular, dígitos y los signos habituales (+ - espacio paréntesis)
    const documentInput = document.getElementById('clientDocument');
    if (documentInput) documentInput.addEventListener('input', () => { documentInput.value = onlyDigits(documentInput.value); });
    const phoneInput = document.getElementById('clientPhone');
    if (phoneInput) phoneInput.addEventListener('input', () => { phoneInput.value = phoneInput.value.replace(/[^\d+\s()-]/g, ''); });
    // El borde rojo de un campo con error se quita en cuanto se vuelve a escribir en él
    document.querySelectorAll('#clientInfoForm .form-input').forEach(input =>
        input.addEventListener('input', () => input.classList.remove('input-error')));
});

function xmlEscape(value) {
    return String(value ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function generateQuoteXML(list) {
    const client = readQuoteClient();
    const unspecified = 'No especificado';

    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<cotizacion>\n';
    xml += `  <fecha>${new Date().toISOString().split('T')[0]}</fecha>\n`;
    xml += '  <cliente>\n';
    xml += `    <nombre>${xmlEscape(client.name) || unspecified}</nombre>\n`;
    xml += `    <documento>${client.document || unspecified}</documento>\n`;
    xml += `    <empresa>${xmlEscape(client.company) || unspecified}</empresa>\n`;
    xml += `    <celular>${client.phone || unspecified}</celular>\n`;
    xml += `    <contacto>${xmlEscape(client.email) || unspecified}</contacto>\n`;
    xml += '  </cliente>\n';
    xml += '  <productos>\n';
    list.forEach(item => {
        xml += '    <producto>\n';
        xml += `      <id>${item.id}</id>\n`;
        xml += `      <nombre>${xmlEscape(item.name)}</nombre>\n`;
        xml += `      <cantidad>${item.quantity || 1}</cantidad>\n`;
        xml += `      <categoria>${xmlEscape(item.category)}</categoria>\n`;
        if (item.presentation) xml += `      <presentacion>${xmlEscape(item.presentation)}</presentacion>\n`;
        if (item.color) xml += `      <color>${xmlEscape(item.color)}</color>\n`;
        if (item.code) xml += `      <codigo>${xmlEscape(item.code)}</codigo>\n`;
        xml += '    </producto>\n';
    });
    xml += '  </productos>\n';
    xml += '</cotizacion>';
    return xml;
}

function downloadQuoteXML() {
    if (quoteList.length === 0) return;
    
    const xmlContent = generateQuoteXML(quoteList);
    const blob = new Blob([xmlContent], { type: 'text/xml' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cotizacion_dewill_${new Date().getTime()}.xml`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    showToast('XML descargado para uso administrativo', 'success');
}

function sendQuoteToWhatsApp() {
    if (quoteList.length === 0) return;

    const client = readQuoteClient();

    let message = "Hola Grupo Dewill, solicito una cotización para los siguientes productos:\n\n";

    const clientLines = [];
    if (client.name) clientLines.push(`- Nombre: ${client.name}`);
    if (client.document) clientLines.push(`- ${documentLabel(client.document)}: ${client.document}`);
    if (client.company) clientLines.push(`- Empresa: ${client.company}`);
    if (client.phone) clientLines.push(`- Celular: ${client.phone}`);
    if (client.email) clientLines.push(`- Email: ${client.email}`);
    if (clientLines.length) {
        message += "*DATOS DEL CLIENTE:*\n" + clientLines.join('\n') + "\n\n";
    }
    if (client.message) {
        message += `*MENSAJE:*\n${client.message}\n\n`;
    }

    message += "*LISTA DE PRODUCTOS:*\n";
    quoteList.forEach((item, index) => {
        // el color va con su codigo ("AMARILLO LIMON #41") y "Codigo" es el del Excel para esa presentacion y color
        const details = [
            item.presentation ? `Presentación: ${item.presentation}` : '',
            item.color ? `Color: ${item.color}` : '',
            item.code ? `Código: ${item.code}` : ''
        ].filter(Boolean).join(' - ');
        message += `${index + 1}. [Cant: ${item.quantity || 1}] ${item.name}${details ? ' - ' + details : ''}\n`;
    });

    // Añadir bloque XML
    message += "\n--- FORMATO XML ---\n";
    message += "```xml\n";
    message += generateQuoteXML(quoteList);
    message += "\n```\n";

    message += "\nPor favor, envíenme los precios y tiempos de entrega. ¡Gracias!";

    const encodedMessage = encodeURIComponent(message);
    const targetNumber = (typeof WHATSAPP_NUMBER !== 'undefined' && WHATSAPP_NUMBER.trim() !== '') ? WHATSAPP_NUMBER : '51977585654';
    window.open(`https://wa.me/${targetNumber}?text=${encodedMessage}`, '_blank');
}

class QuoteError extends Error {}

function submitQuoteRequest() {
    if (quoteList.length === 0) {
        showToast('La lista de cotización está vacía.', 'error');
        return;
    }

    const client = readQuoteClient();
    const problem = validateQuoteClient(client);
    if (problem) {
        showToast(problem.message, 'error');
        const field = document.getElementById(problem.field);
        if (field) {
            field.classList.add('input-error');
            field.focus();
        }
        return;
    }

    // Prepare JSON payload
    const payload = {
        name: client.name,
        document: client.document,
        company: client.company,
        phone: client.phone,
        email: client.email,
        message: client.message,
        items: quoteList.map(item => ({
            product_id: parseInt(item.id),
            quantity: parseInt(item.quantity) || 1,
            color: item.color || null,
            presentation: item.presentation || null
        }))
    };

    // Show loading state or disable button
    const btn = document.querySelector('.quote-footer button');
    let originalText = '';
    if (btn) {
        originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
    }

    fetch('/api/cotizacion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(async response => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.success) {
            // El servidor explica qué dato falta o es inválido; se muestra tal cual
            throw new QuoteError(data.error || 'Ocurrió un error. Inténtelo de nuevo.');
        }
        return data;
    })
    .then(data => {
        showToast('¡Solicitud de cotización enviada con éxito!', 'success');

        setTimeout(() => {
            if (confirm('¿Desea enviar también una copia de su cotización por WhatsApp para acelerar la atención?')) {
                sendQuoteToWhatsApp();
            }

            // Clear the quote
            quoteList = [];
            saveQuote();
            updateQuoteUI();
            toggleQuotePanel();
        }, 500);
    })
    .catch(error => {
        console.error('Error submitting quote:', error);
        showToast(error instanceof QuoteError ? error.message : 'Error de conexión. Inténtelo más tarde.', 'error');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    });
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
    const targetNumber = (typeof WHATSAPP_NUMBER !== 'undefined' && WHATSAPP_NUMBER.trim() !== '') ? WHATSAPP_NUMBER : '51977585654';
    waLink.href = `https://wa.me/${targetNumber}?text=${encodeURIComponent(waMsg)}`;

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
    // Remove existing toast if any
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}

function initHeroAnimations() {
    // Counter animation for hero stats
    const counters = document.querySelectorAll('.stat-number[data-target]');
    if (counters.length > 0) {
        const animateCounter = (el) => {
            const target = parseInt(el.getAttribute('data-target'));
            const duration = 2000;
            const start = performance.now();

            const step = (timestamp) => {
                const progress = Math.min((timestamp - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
                el.innerText = Math.floor(eased * target);
                if (progress < 1) {
                    requestAnimationFrame(step);
                } else {
                    el.innerText = target;
                }
            };
            requestAnimationFrame(step);
        };

        // Use IntersectionObserver to trigger counters when visible
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(c => counterObserver.observe(c));
    }

    // Scroll-triggered fade-in animations
    const options = { threshold: 0.1 };
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

// ==================== WHATSAPP WIDGET ====================
function toggleWhatsAppWidget(event) {
    if (event) event.stopPropagation();
    const card = document.getElementById('waWidgetCard');
    const icon = document.getElementById('waFloatIcon');
    if (!card) return;
    
    card.classList.toggle('show');
    
    if (card.classList.contains('show')) {
        if (icon) {
            icon.className = 'fas fa-times';
        }
    } else {
        if (icon) {
            icon.className = 'fab fa-whatsapp';
        }
    }
}

// Close widget when clicking outside
document.addEventListener('click', (event) => {
    const card = document.getElementById('waWidgetCard');
    const btn = document.getElementById('whatsappFloatBtn');
    const icon = document.getElementById('waFloatIcon');
    if (card && card.classList.contains('show')) {
        if (!card.contains(event.target) && (!btn || !btn.contains(event.target))) {
            card.classList.remove('show');
            if (icon) {
                icon.className = 'fab fa-whatsapp';
            }
        }
    }
});

// ========== MOBILE MENU ==========
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    const hamburger = document.getElementById('hamburger');
    if (navLinks) {
        navLinks.classList.toggle('active');
        hamburger.classList.toggle('is-active');
    }
}

// ==================== HERO CAROUSEL ====================
let currentSlide = 0;
let carouselInterval;

function initCarousel() {
    const slides = document.querySelectorAll('.carousel-slide');
    if (slides.length <= 1) return;

    startCarousel();
}

function showSlide(index) {
    const slides = document.querySelectorAll('.carousel-slide');
    const dots = document.querySelectorAll('.carousel-indicators .dot');
    
    if (slides.length === 0) return;

    if (index >= slides.length) currentSlide = 0;
    else if (index < 0) currentSlide = slides.length - 1;
    else currentSlide = index;

    slides.forEach(slide => slide.classList.remove('active'));
    dots.forEach(dot => dot.classList.remove('active'));

    slides[currentSlide].classList.add('active');
    if (dots[currentSlide]) dots[currentSlide].classList.add('active');
}

function moveCarousel(direction) {
    showSlide(currentSlide + direction);
    resetCarouselInterval();
}

function goToSlide(index) {
    showSlide(index);
    resetCarouselInterval();
}

function startCarousel() {
    carouselInterval = setInterval(() => {
        moveCarousel(1);
    }, 5000);
}

function resetCarouselInterval() {
    clearInterval(carouselInterval);
    startCarousel();
}

document.addEventListener('DOMContentLoaded', () => {
    initCarousel();
    initOffersCarousel();
});

// ========== OFERTAS: carrusel de banners debajo de Marcas ==========
// El desplazamiento y el arrastre con el dedo los hace el navegador (scroll-snap); aqui solo van las flechas,
// los puntos y el avance automatico, que se detiene con el cursor o el foco encima y si la pagina no se ve.
function initOffersCarousel() {
    document.querySelectorAll('.offers-carousel').forEach(carousel => {
        const track = carousel.querySelector('.offers-track');
        const dots = carousel.querySelectorAll('.offers-dot');
        const total = carousel.querySelectorAll('.offer-slide').length;
        if (!track || total === 0) return;

        const autoplayMs = parseInt(carousel.dataset.autoplay, 10) || 0;
        const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        let index = 0;          // oferta que se ve ahora
        let hovering = false;   // cursor, foco o dedo sobre el carrusel
        let inView = true;
        let timer = null;

        const goTo = target => track.scrollTo({ left: ((target + total) % total) * track.clientWidth, behavior: 'smooth' });
        const sync = () => {
            index = Math.min(total - 1, Math.max(0, Math.round(track.scrollLeft / track.clientWidth)));
            dots.forEach((dot, i) => dot.classList.toggle('active', i === index));
        };
        // Cada gesto del visitante reinicia la cuenta para que el avance automatico no le gane al movimiento
        const restart = () => {
            clearInterval(timer);
            if (total > 1 && autoplayMs && !reduceMotion) {
                timer = setInterval(() => { if (!hovering && inView && !document.hidden) goTo(index + 1); }, autoplayMs);
            }
        };

        let syncing = false;
        track.addEventListener('scroll', () => {
            if (syncing) return;
            syncing = true;
            requestAnimationFrame(() => { syncing = false; sync(); });
        }, { passive: true });

        const prev = carousel.querySelector('.offers-nav.prev');
        const next = carousel.querySelector('.offers-nav.next');
        if (prev) prev.addEventListener('click', () => { goTo(index - 1); restart(); });
        if (next) next.addEventListener('click', () => { goTo(index + 1); restart(); });
        dots.forEach((dot, i) => dot.addEventListener('click', () => { goTo(i); restart(); }));
        track.addEventListener('keydown', e => {
            if (e.key === 'ArrowLeft') { e.preventDefault(); goTo(index - 1); restart(); }
            if (e.key === 'ArrowRight') { e.preventDefault(); goTo(index + 1); restart(); }
        });

        carousel.addEventListener('mouseenter', () => { hovering = true; });
        carousel.addEventListener('mouseleave', () => { hovering = false; restart(); });
        carousel.addEventListener('focusin', () => { hovering = true; });
        carousel.addEventListener('focusout', () => { hovering = false; restart(); });
        carousel.addEventListener('touchstart', () => { hovering = true; }, { passive: true });
        carousel.addEventListener('touchend', () => { hovering = false; restart(); }, { passive: true });

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(entries => { inView = entries[0].isIntersecting; }, { threshold: 0.2 }).observe(carousel);
        }
        // Si cambia el ancho (girar el telefono), la oferta visible vuelve a quedar justo en su lugar, sin animacion
        window.addEventListener('resize', () => {
            track.style.scrollBehavior = 'auto';
            track.scrollLeft = index * track.clientWidth;
            track.style.scrollBehavior = '';
        });

        restart();
    });
}


// Featured Products Slider (Sequential Movement)
function scrollFeaturedSlider(direction) {
    const slider = document.getElementById('featuredSlider');
    if (slider) {
        const card = slider.querySelector('.product-card');
        if (card) {
            const cardWidth = card.offsetWidth;
            const style = window.getComputedStyle(card);
            const marginRight = parseFloat(style.marginRight) || 0;
            const marginLeft = parseFloat(style.marginLeft) || 0;
            const gap = parseFloat(window.getComputedStyle(slider).gap) || 0;
            const step = cardWidth + gap + marginRight + marginLeft;
            
            slider.scrollBy({
                left: direction * step,
                behavior: 'smooth'
            });
        } else {
            slider.scrollBy({
                left: direction * 324,
                behavior: 'smooth'
            });
        }
    }
}

// Auto scroll variables for featured carousel
let featuredInterval;
function startFeaturedAutoScroll() {
    const slider = document.getElementById('featuredSlider');
    if (!slider) return;
    
    clearInterval(featuredInterval);
    featuredInterval = setInterval(() => {
        const maxScroll = slider.scrollWidth - slider.clientWidth;
        if (slider.scrollLeft >= maxScroll - 10) {
            slider.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
            scrollFeaturedSlider(1);
        }
    }, 4000); // Auto scroll every 4 seconds
}

// Initialize scroll behaviors and event handlers
document.addEventListener('DOMContentLoaded', () => {
    const slider = document.getElementById('featuredSlider');
    if (slider) {
        startFeaturedAutoScroll();
        slider.addEventListener('mouseenter', () => clearInterval(featuredInterval));
        slider.addEventListener('mouseleave', startFeaturedAutoScroll);
        
        // Also pause auto scroll when manual arrows are clicked
        const btns = document.querySelectorAll('.product-slider-container .slider-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                clearInterval(featuredInterval);
                // Resume auto-scroll after 10 seconds of user inactivity
                setTimeout(startFeaturedAutoScroll, 10000);
            });
        });
    }
});

// ========== LIVE SEARCH ==========
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('globalSearchResults');
    let searchTimeout;

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            clearTimeout(searchTimeout);

            if (query.length < 2) {
                searchResults.classList.remove('show');
                return;
            }

            searchResults.innerHTML = '<div class="search-loading"><i class="fas fa-spinner fa-spin"></i> Buscando...</div>';
            searchResults.classList.add('show');

            searchTimeout = setTimeout(() => {
                fetch(`/api/productos/search?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.length === 0) {
                            searchResults.innerHTML = '<div class="search-no-results">No se encontraron productos</div>';
                            return;
                        }

                        searchResults.innerHTML = data.map(p => `
                            <a href="/producto/${p.id}" class="search-result-item">
                                <img src="/static/${p.main_image || 'assets/product_paint.png'}" class="search-result-img" alt="${p.name}">
                                <div class="search-result-info">
                                    <span class="search-result-title">${p.name}</span>
                                    <span class="search-result-cat">${p.category_name || ''} ${p.brand_name ? ' - ' + p.brand_name : ''}</span>
                                </div>
                            </a>
                        `).join('');
                    })
                    .catch(err => {
                        console.error('Error fetching search results:', err);
                        searchResults.innerHTML = '<div class="search-no-results">Error al buscar</div>';
                    });
            }, 300);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.remove('show');
            }
        });
        
        // Show again when clicking input if there is text
        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim().length >= 2 && searchResults.innerHTML !== '') {
                searchResults.classList.add('show');
            }
        });
    }
});