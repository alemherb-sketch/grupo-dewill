// ==================== STATE ====================
let quoteList = JSON.parse(localStorage.getItem('dewill_quote')) || [];
let searchTimeout = null;

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    updateQuoteUI();
    setupNavbar();
    setupSearchAutocomplete();
    initCarousel();
    initFeaturedSlider();
    initAnimations();
});

// ==================== NAVBAR & MOBILE MENU ====================
function setupNavbar() {
    window.addEventListener('scroll', () => {
        const nav = document.getElementById('navbar');
        if (window.scrollY > 50) nav.classList.add('scrolled');
        else if (!nav.classList.contains('scrolled')) nav.classList.remove('scrolled'); // Only remove if not hardcoded
    });
}

function toggleMobileMenu() {
    document.getElementById('navLinks').classList.toggle('active');
    document.getElementById('hamburger').classList.toggle('active');
}

// ==================== QUOTE SYSTEM ====================
function addToQuote(id, name, image, color = null, quantity = 1, presentation = null) {
    const cart_id = id + '_' + (color || 'nc') + '_' + (presentation || 'np');
    const existing = quoteList.find(item => item.cart_id === cart_id);
    if (existing) {
        existing.quantity += quantity;
        showToast(`Cantidad aumentada: ${existing.quantity}`, 'success');
    } else {
        quoteList.push({ product_id: id, cart_id, name, image, color, presentation, quantity: quantity });
        showToast('Agregado a la lista de cotización', 'success');
    }
    saveQuote();
    updateQuoteUI();
}

function updateQuantity(cart_id, delta) {
    const item = quoteList.find(p => p.cart_id === cart_id || p.product_id === cart_id);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity < 1) item.quantity = 1;
    saveQuote();
    updateQuoteUI();
}

function removeFromQuote(cart_id) {
    quoteList = quoteList.filter(item => item.cart_id !== cart_id && item.product_id !== cart_id);
    saveQuote();
    updateQuoteUI();
}

function clearQuote() {
    if (confirm('¿Limpiar toda la lista?')) {
        quoteList = [];
        saveQuote();
        updateQuoteUI();
    }
}

function saveQuote() {
    localStorage.setItem('dewill_quote', JSON.stringify(quoteList));
}

function updateQuoteUI() {
    document.getElementById('cartBadge').innerText = quoteList.length;
    const itemsContainer = document.getElementById('quoteItems');
    const empty = document.getElementById('quoteEmpty');
    const footer = document.getElementById('quoteFooter');
    const form = document.getElementById('clientInfoForm');

    if (quoteList.length === 0) {
        empty.style.display = 'block';
        itemsContainer.style.display = 'none';
        footer.style.display = 'none';
        form.style.display = 'none';
        document.getElementById('btnCart').classList.remove('has-items-alert');
    } else {
        empty.style.display = 'none';
        itemsContainer.style.display = 'block';
        footer.style.display = 'flex';
        form.style.display = 'block';
        document.getElementById('quoteTotalCount').innerText = quoteList.length;
        document.getElementById('btnCart').classList.add('has-items-alert');

        itemsContainer.innerHTML = '';
        quoteList.forEach(item => {
            const colorBadge = item.color ? `<span style="display:inline-block; margin-top:5px; margin-right:5px; font-size:12px; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:12px;">Color: ${item.color}</span>` : '';
            const presBadge = item.presentation ? `<span style="display:inline-block; margin-top:5px; font-size:12px; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:12px;">Pres: ${item.presentation}</span>` : '';
            const c_id = typeof item.cart_id === 'string' ? `'${item.cart_id}'` : item.product_id;
            itemsContainer.innerHTML += `
                <div class="quote-item">
                    <img src="${item.image.startsWith('http') || item.image.startsWith('/') ? item.image : '/static/' + item.image}" class="quote-item-img">
                    <div class="quote-item-info">
                        <h4>${item.name}</h4>
                        <div>${colorBadge}${presBadge}</div>
                        <div class="quote-item-controls">
                            <div class="quantity-selector">
                                <button class="qty-btn" onclick="updateQuantity(${c_id}, -1)"><i class="fas fa-minus"></i></button>
                                <span class="qty-val">${item.quantity}</span>
                                <button class="qty-btn" onclick="updateQuantity(${c_id}, 1)"><i class="fas fa-plus"></i></button>
                            </div>
                            <button class="btn-remove" onclick="removeFromQuote(${c_id})"><i class="fas fa-trash-alt"></i></button>
                        </div>
                    </div>
                </div>
            `;
        });
    }
}

function toggleQuotePanel() {
    document.getElementById('quotePanel').classList.toggle('open');
    document.getElementById('quoteOverlay').classList.toggle('open');
}

async function submitQuoteRequest() {
    const name = document.getElementById('clientName').value.trim();
    const email = document.getElementById('clientEmail').value.trim();
    const phone = document.getElementById('clientPhone').value.trim();
    
    if (!name || !email || !phone) {
        alert("Por favor completa tu nombre, email y teléfono.");
        return;
    }

    const payload = {
        name, email, phone,
        company: document.getElementById('clientCompany').value.trim(),
        message: document.getElementById('clientMessage').value.trim(),
        items: quoteList
    };

    try {
        const btn = document.querySelector('#quoteFooter .btn-primary');
        const oldText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        btn.disabled = true;

        const res = await fetch('/api/cotizacion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        btn.innerHTML = oldText;
        btn.disabled = false;

        if (data.success) {
            quoteList = [];
            saveQuote();
            updateQuoteUI();
            toggleQuotePanel();
            showToast('¡Solicitud enviada exitosamente!', 'success');
        } else {
            showToast('Error al enviar la solicitud', 'error');
        }
    } catch (e) {
        showToast('Error de conexión', 'error');
        document.querySelector('#quoteFooter .btn-primary').disabled = false;
    }
}

function sendQuoteWhatsApp() {
    if (quoteList.length === 0) return;
    const name = document.getElementById('clientName').value.trim();
    let msg = "Hola Grupo Dewill, solicito una cotización:\n\n";
    if (name) msg += `*Cliente:* ${name}\n\n`;
    msg += "*Productos:*\n";
    quoteList.forEach((item, i) => {
        const colorText = item.color ? ` (Color: ${item.color})` : '';
        const presText = item.presentation ? ` (Pres: ${item.presentation})` : '';
        msg += `${i+1}. [Cant: ${item.quantity}] ${item.name}${colorText}${presText}\n`;
    });
    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`, '_blank');
}

// ==================== SEARCH AUTOCOMPLETE ====================
function setupSearchAutocomplete() {
    const searchInput = document.getElementById('productSearch');
    const dropdown = document.getElementById('autocompleteDropdown');
    if (!searchInput || !dropdown) return;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (q.length < 2) {
            dropdown.innerHTML = '';
            dropdown.classList.remove('show');
            return;
        }

        searchTimeout = setTimeout(async () => {
            const res = await fetch(`/api/productos/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            
            if (data.length > 0) {
                dropdown.innerHTML = data.map(p => `
                    <a href="/producto/${p.id}" class="autocomplete-item">
                        <img src="/static/${p.main_image || 'assets/product_paint.png'}" alt="">
                        <div>
                            <strong>${p.name}</strong>
                            <span>${p.category}</span>
                        </div>
                    </a>
                `).join('');
                dropdown.classList.add('show');
            } else {
                dropdown.innerHTML = '<div class="autocomplete-empty">No se encontraron productos</div>';
                dropdown.classList.add('show');
            }
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
}

// ==================== CAROUSEL ====================
let currentSlide = 0;
function initCarousel() {
    const slides = document.querySelectorAll('.hero-slide');
    if (slides.length <= 1) return;
    setInterval(() => nextSlide(), 6000);
}

function goToSlide(index) {
    const slides = document.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.carousel-dots .dot');
    if (slides.length === 0) return;
    
    slides[currentSlide].classList.remove('active');
    if (dots.length) dots[currentSlide].classList.remove('active');
    
    currentSlide = index;
    
    slides[currentSlide].classList.add('active');
    if (dots.length) dots[currentSlide].classList.add('active');
}

function nextSlide() {
    const slides = document.querySelectorAll('.hero-slide');
    if (slides.length <= 1) return;
    goToSlide((currentSlide + 1) % slides.length);
}

function prevSlide() {
    const slides = document.querySelectorAll('.hero-slide');
    if (slides.length <= 1) return;
    goToSlide((currentSlide - 1 + slides.length) % slides.length);
}

function scrollFeaturedSlider(direction) {
    const slider = document.getElementById('featuredSlider');
    if (slider) {
        const scrollAmount = 332; // card width + gap
        slider.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });
    }
}

let featuredSliderInterval;
function initFeaturedSlider() {
    const slider = document.getElementById('featuredSlider');
    if (!slider) return;
    
    featuredSliderInterval = setInterval(autoScrollFeaturedSlider, 2500);
    
    slider.addEventListener('mouseenter', () => clearInterval(featuredSliderInterval));
    slider.addEventListener('mouseleave', () => {
        clearInterval(featuredSliderInterval);
        featuredSliderInterval = setInterval(autoScrollFeaturedSlider, 2500);
    });
}

function autoScrollFeaturedSlider() {
    const slider = document.getElementById('featuredSlider');
    if (!slider) return;
    
    const maxScroll = slider.scrollWidth - slider.clientWidth;
    const scrollAmount = 332;
    
    if (slider.scrollLeft >= maxScroll - 10) {
        slider.scrollTo({ left: 0, behavior: 'smooth' });
    } else {
        slider.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}

// ==================== PRODUCT DETAILS ====================
function changeMainImage(element) {
    const mainImg = document.getElementById('mainImage');
    document.querySelectorAll('.thumb').forEach(t => t.classList.remove('active'));
    element.classList.add('active');
    mainImg.src = element.getAttribute('data-src');
}

// ==================== UTILS ====================
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function initAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.section-header, .glass-card, .product-card, .why-card').forEach(el => observer.observe(el));

    // Stats counter animation
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-target'));
                const duration = 2000;
                const step = target / (duration / 16);
                let current = 0;
                
                const updateCounter = () => {
                    current += step;
                    if (current < target) {
                        el.innerText = Math.ceil(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        el.innerText = target;
                    }
                };
                updateCounter();
                statsObserver.unobserve(el);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.stat-number').forEach(el => statsObserver.observe(el));
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
