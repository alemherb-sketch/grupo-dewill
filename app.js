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

    renderProducts();
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

    const infoForm = document.getElementById('clientInfoForm');
    if (quoteList.length === 0) {
        quoteEmpty.style.display = 'block';
        quoteItems.style.display = 'none';
        quoteFooter.style.display = 'none';
        if (infoForm) infoForm.style.display = 'none';
    } else {
        quoteEmpty.style.display = 'none';
        quoteItems.style.display = 'block';
        quoteFooter.style.display = 'flex';
        if (infoForm) infoForm.style.display = 'block';

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

function generateQuoteXML(list) {
    const clientName = document.getElementById('clientName')?.value || 'No especificado';
    const clientCompany = document.getElementById('clientCompany')?.value || 'No especificado';
    const clientEmail = document.getElementById('clientEmail')?.value || 'No especificado';

    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<cotizacion>\n';
    xml += `  <fecha>${new Date().toISOString().split('T')[0]}</fecha>\n`;
    xml += '  <cliente>\n';
    xml += `    <nombre>${clientName}</nombre>\n`;
    xml += `    <empresa>${clientCompany}</empresa>\n`;
    xml += `    <contacto>${clientEmail}</contacto>\n`;
    xml += '  </cliente>\n';
    xml += '  <productos>\n';
    list.forEach(item => {
        xml += '    <producto>\n';
        xml += `      <id>${item.id}</id>\n`;
        xml += `      <nombre>${item.name}</nombre>\n`;
        xml += `      <cantidad>${item.quantity || 1}</cantidad>\n`;
        xml += `      <categoria>${item.category}</categoria>\n`;
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

    const clientName = document.getElementById('clientName')?.value;
    const clientCompany = document.getElementById('clientCompany')?.value;
    const clientEmail = document.getElementById('clientEmail')?.value;

    let message = "Hola Grupo Dewill, solicito una cotización para los siguientes productos:\n\n";
    
    if (clientName || clientCompany) {
        message += "*DATOS DEL CLIENTE:*\n";
        if (clientName) message += `- Nombre: ${clientName}\n`;
        if (clientCompany) message += `- Empresa: ${clientCompany}\n`;
        if (clientEmail) message += `- Contacto: ${clientEmail}\n`;
        message += "\n";
    }

    message += "*LISTA DE PRODUCTOS:*\n";
    quoteList.forEach((item, index) => {
        message += `${index + 1}. [Cant: ${item.quantity || 1}] ${item.name}\n`;
    });

    // Añadir bloque XML
    message += "\n--- FORMATO XML ---\n";
    message += "```xml\n";
    message += generateQuoteXML(quoteList);
    message += "\n```\n";

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
