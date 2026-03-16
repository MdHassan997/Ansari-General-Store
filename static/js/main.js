/* ============================================
   ANSARI GENERAL STORE — Main JavaScript
   ============================================ */

/* ── TOAST NOTIFICATIONS ── */
function showToast(message, type = 'info', duration = 3000) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = 'toast visible ' + type;
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove('visible');
  }, duration);
}

/* ── CART BADGE UPDATE ── */
function updateCartBadge(count) {
  const badge = document.getElementById('cartBadge');
  if (badge) {
    badge.textContent = count;
    badge.style.transform = 'scale(1.4)';
    setTimeout(() => badge.style.transform = 'scale(1)', 200);
  }
}

/* ── ADD TO CART ── */
function addToCart(productId, quantity = 1) {
  // Check if logged in (badge will tell us via API)
  fetch('/api/cart/add', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId, quantity: quantity })
  })
  .then(r => r.json())
  .then(data => {
    if (data.redirect) {
      window.location.href = data.redirect + '?next=' + encodeURIComponent(window.location.pathname);
      return;
    }
    if (data.success) {
      updateCartBadge(data.cart_count);
      showToast('Added to cart! 🛒', 'success');
    } else {
      showToast(data.error || 'Failed to add to cart.', 'error');
    }
  })
  .catch(() => showToast('Network error. Try again.', 'error'));
}

/* ── WISHLIST TOGGLE ── */
function toggleWishlist(productId, btn) {
  const isActive = btn.classList.contains('active');
  const endpoint = isActive ? '/api/wishlist/remove' : '/api/wishlist/add';

  fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId })
  })
  .then(r => r.json())
  .then(data => {
    if (data.redirect) {
      window.location.href = data.redirect + '?next=' + encodeURIComponent(window.location.pathname);
      return;
    }
    if (data.success) {
      btn.classList.toggle('active');
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = btn.classList.contains('active') ? 'fas fa-heart' : 'far fa-heart';
      }
      showToast(isActive ? 'Removed from wishlist' : 'Added to wishlist ❤️', isActive ? 'info' : 'success');
    }
  })
  .catch(() => showToast('Network error. Try again.', 'error'));
}

/* ── HERO SLIDER ── */
(function initSlider() {
  const track = document.getElementById('sliderTrack');
  const prevBtn = document.getElementById('sliderPrev');
  const nextBtn = document.getElementById('sliderNext');
  const dots = document.querySelectorAll('.slider-dots .dot');
  if (!track) return;

  let current = 0;
  const total = track.children.length;

  function goTo(index) {
    current = (index + total) % total;
    track.style.transform = `translateX(-${current * 100}%)`;
    dots.forEach((d, i) => d.classList.toggle('active', i === current));
  }

  prevBtn?.addEventListener('click', () => goTo(current - 1));
  nextBtn?.addEventListener('click', () => goTo(current + 1));
  dots.forEach(dot => dot.addEventListener('click', () => goTo(+dot.dataset.index)));

  // Auto-advance
  const autoPlay = setInterval(() => goTo(current + 1), 5000);
  track.closest('.hero-slider')?.addEventListener('mouseenter', () => clearInterval(autoPlay));

  // Keyboard navigation
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') goTo(current - 1);
    if (e.key === 'ArrowRight') goTo(current + 1);
  });

  // Touch swipe
  let startX = 0;
  track.addEventListener('touchstart', e => startX = e.touches[0].clientX, { passive: true });
  track.addEventListener('touchend', e => {
    const diff = startX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) goTo(current + (diff > 0 ? 1 : -1));
  }, { passive: true });
})();

/* ── MOBILE HAMBURGER ── */
(function initMobileMenu() {
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  if (!hamburger || !mobileMenu) return;

  hamburger.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
    hamburger.innerHTML = mobileMenu.classList.contains('open')
      ? '<i class="fas fa-times"></i>'
      : '<i class="fas fa-bars"></i>';
  });

  // Close on outside click
  document.addEventListener('click', e => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
      hamburger.innerHTML = '<i class="fas fa-bars"></i>';
    }
  });
})();

/* ── SEARCH SUGGESTIONS ── */
(function initSearchSuggestions() {
  const input = document.getElementById('searchInput');
  const suggestionsBox = document.getElementById('searchSuggestions');
  if (!input || !suggestionsBox) return;

  let debounceTimer;

  input.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const q = input.value.trim();
    if (q.length < 2) {
      suggestionsBox.classList.remove('active');
      suggestionsBox.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(results => {
          if (!results.length) {
            suggestionsBox.classList.remove('active');
            return;
          }
          suggestionsBox.innerHTML = results.map(p => {
            const originalPrice = parseFloat(p.price) || 0;
            const discount = parseFloat(p.discount) || 0;
            const finalPrice = discount > 0
              ? originalPrice - (originalPrice * discount / 100)
              : originalPrice;
            const priceHtml = discount > 0
              ? `<span style="color:#2e7d32;font-size:12px;font-weight:700">₹${finalPrice.toFixed(2)}</span>
                 <span style="color:#999;font-size:11px;text-decoration:line-through;margin-left:4px">₹${originalPrice.toFixed(2)}</span>
                 <span style="background:#ffebee;color:#c62828;font-size:10px;font-weight:700;padding:1px 5px;border-radius:10px;margin-left:4px">${Math.round(discount)}% OFF</span>`
              : `<span style="color:#2e7d32;font-size:12px;font-weight:700">₹${finalPrice.toFixed(2)}</span>`;
            return `
              <div class="suggestion-item" onclick="location.href='/product/${p.id}'">
                ${p.image_url
                  ? `<img src="${p.image_url}" alt="${p.name}" onerror="this.style.display='none'">`
                  : '<span style="font-size:24px">🛒</span>'}
                <div>
                  <div style="font-weight:600;font-size:13px">${p.name}</div>
                  <div style="display:flex;align-items:center;gap:4px;margin-top:2px">${priceHtml}</div>
                </div>
              </div>
            `;
          }).join('');
          suggestionsBox.classList.add('active');
        })
        .catch(() => {});
    }, 300);
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !suggestionsBox.contains(e.target)) {
      suggestionsBox.classList.remove('active');
    }
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Escape') suggestionsBox.classList.remove('active');
  });
})();

/* ── LAZY IMAGE LOADING ── */
(function initLazyLoad() {
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          observer.unobserve(img);
        }
      });
    }, { rootMargin: '100px' });

    document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));
  }
})();

/* ── FLASH MESSAGE AUTO-DISMISS ── */
(function initFlashDismiss() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => flash.remove(), 5000);
  });
})();

/* ── SMOOTH SCROLL TO TOP ON PAGE LOAD ── */
window.addEventListener('pageshow', () => {
  if (window.location.hash) return;
  // Fetch and update cart count on every page load
  fetch('/api/cart/count')
    .then(r => r.json())
    .then(data => {
      const badge = document.getElementById('cartBadge');
      if (badge && data.count !== undefined) {
        badge.textContent = data.count;
      }
    })
    .catch(() => {});
});

/* ── FORM VALIDATION HELPERS ── */
function validateRequired(fields) {
  for (const [id, label] of Object.entries(fields)) {
    const el = document.getElementById(id);
    if (!el || !el.value.trim()) {
      showToast(`${label} is required.`, 'error');
      el?.focus();
      return false;
    }
  }
  return true;
}

/* ── NUMBER FORMATTING ── */
function formatCurrency(amount) {
  return '₹' + parseFloat(amount).toFixed(2);
}

/* ── CONFIRM DELETE HELPER ── */
function confirmDelete(message) {
  return confirm(message || 'Are you sure you want to delete this?');
}

/* ── IMAGE PREVIEW ── */
function previewImage(input, previewId) {
  const preview = document.getElementById(previewId);
  if (!preview || !input.files || !input.files[0]) return;
  const reader = new FileReader();
  reader.onload = e => { preview.src = e.target.result; preview.style.display = 'block'; };
  reader.readAsDataURL(input.files[0]);
}

/* ── PRINT ORDER ── */
function printOrder() {
  window.print();
}

/* ── COPY TO CLIPBOARD ── */
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => showToast('Copied to clipboard!', 'success'))
    .catch(() => showToast('Copy failed.', 'error'));
}

/* ── PRODUCT CARD ANIMATION ON SCROLL ── */
(function initScrollAnimation() {
  if (!('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.product-card, .cat-card, .order-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity .4s ease, transform .4s ease';
    observer.observe(card);
  });
})();
