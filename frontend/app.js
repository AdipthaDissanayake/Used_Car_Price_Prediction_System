/**
 * AutoValuate.AI - Professional Client Workspace Logic
 * Features: JWT Authentication, Real-time Valuation Inference, User-Specific History & Deletion
 */

let currentUser = null;
let currentToken = null;

// =========================================================================
// Initialization & Authentication Management
// =========================================================================

function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };
    if (currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
    }
    return headers;
}

function updateNavAuthUI() {
    const guestEl = document.getElementById('auth-guest');
    const userEl = document.getElementById('auth-user');
    const initialsEl = document.getElementById('nav-user-initials');
    const nameEl = document.getElementById('nav-user-name');
    const emailEl = document.getElementById('nav-user-email');

    const historyGuestPrompt = document.getElementById('history-guest-prompt');
    const historyScrollList = document.getElementById('history-scroll-list');
    const historyActions = document.getElementById('history-actions');

    if (currentUser && currentToken) {
        guestEl.style.display = 'none';
        userEl.style.display = 'flex';

        const name = currentUser.name || currentUser.email.split('@')[0];
        nameEl.textContent = name;
        emailEl.textContent = currentUser.email;

        // Initials avatar
        const initials = name.split(' ').map(p => p[0]).join('').substring(0, 2).toUpperCase();
        initialsEl.textContent = initials || 'US';

        // History View for User
        historyGuestPrompt.style.display = 'none';
        historyScrollList.style.display = 'block';
        historyActions.style.display = 'block';

        loadUserHistory();
    } else {
        guestEl.style.display = 'flex';
        userEl.style.display = 'none';

        // Guest prompt for History
        historyGuestPrompt.style.display = 'flex';
        historyScrollList.style.display = 'none';
        historyActions.style.display = 'none';
        document.getElementById('history-count').textContent = '0 records';
    }
}

// Modal State Controls
const authModal = document.getElementById('auth-modal');
const modalAlert = document.getElementById('modal-alert');
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const loginForm = document.getElementById('modal-login-form');
const registerForm = document.getElementById('modal-register-form');

function openModal(activeTab = 'login') {
    modalAlert.style.display = 'none';
    modalAlert.textContent = '';
    authModal.style.display = 'flex';

    if (activeTab === 'login') {
        tabLogin.classList.add('active');
        tabRegister.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    } else {
        tabRegister.classList.add('active');
        tabLogin.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    }
}

function closeModal() {
    authModal.style.display = 'none';
    modalAlert.style.display = 'none';
    modalAlert.textContent = '';
}

function showModalError(msg) {
    modalAlert.textContent = msg;
    modalAlert.className = 'ui-alert error';
    modalAlert.style.display = 'block';
}

// =========================================================================
// History Fetching, Loading Specs, and Deletion
// =========================================================================

async function loadUserHistory() {
    if (!currentToken) return;

    const itemsContainer = document.getElementById('history-items-container');
    const emptyMsg = document.getElementById('history-empty-msg');
    const countBadge = document.getElementById('history-count');

    try {
        const res = await fetch('/api/predictions/history?limit=25', {
            headers: getAuthHeaders()
        });
        const json = await res.json();

        if (res.ok && json.data) {
            const history = json.data;
            countBadge.textContent = `${history.length} record${history.length === 1 ? '' : 's'}`;

            if (history.length === 0) {
                emptyMsg.style.display = 'block';
                itemsContainer.innerHTML = '';
                return;
            }

            emptyMsg.style.display = 'none';
            itemsContainer.innerHTML = '';

            history.forEach(item => {
                const card = document.createElement('div');
                card.className = 'history-row-card';
                card.id = `history-item-${item.id}`;

                const cleanLabel = item.clean_title === 'Yes' ? 'Clean Title' : 'Salvage/Rebuilt';
                const accidentLabel = item.accident.toLowerCase().includes('accident') ? 'Damage Reported' : 'Clean Record';

                card.innerHTML = `
                    <div class="history-info-block">
                        <span class="history-car-title">${item.model_year} ${item.brand}</span>
                        <span class="history-specs-sub">${Number(item.milage).toLocaleString()} mi • ${item.transmission} • ${item.fuel_type} • ${accidentLabel}</span>
                        <span class="history-time">${item.created_at || 'Recently'}</span>
                    </div>
                    <div class="history-side-actions">
                        <span class="history-price-tag">${item.predicted_price_formatted}</span>
                        <button type="button" class="btn-load-specs" title="Load into parameters form">Load Specs</button>
                        <button type="button" class="btn-delete-row" title="Delete record">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                <line x1="10" y1="11" x2="10" y2="17"/>
                                <line x1="14" y1="11" x2="14" y2="17"/>
                            </svg>
                        </button>
                    </div>
                `;

                // Handle Load Specs click
                card.querySelector('.btn-load-specs').addEventListener('click', () => {
                    populateFormWithSpecs(item);
                });

                // Handle Single Delete click
                card.querySelector('.btn-delete-row').addEventListener('click', async () => {
                    await deleteSingleHistoryRecord(item.id);
                });

                itemsContainer.appendChild(card);
            });
        }
    } catch (err) {
        console.error("Failed to load history:", err);
    }
}

function populateFormWithSpecs(specs) {
    document.getElementById('brand').value = specs.brand || '';
    document.getElementById('model_year').value = specs.model_year || 2021;
    document.getElementById('milage').value = specs.milage || 38000;
    document.getElementById('transmission').value = specs.transmission || 'Automatic';
    document.getElementById('fuel_type').value = specs.fuel_type || 'Gasoline';
    document.getElementById('clean_title').value = specs.clean_title || 'Yes';
    document.getElementById('accident').value = specs.accident || 'None reported';

    updateLiveHelpers();

    // Scroll to console
    document.querySelector('.console-card').scrollIntoView({ behavior: 'smooth' });
}

async function deleteSingleHistoryRecord(logId) {
    if (!currentToken) return;

    try {
        const res = await fetch(`/api/predictions/history/${logId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (res.ok) {
            const cardEl = document.getElementById(`history-item-${logId}`);
            if (cardEl) {
                cardEl.style.transition = 'all 0.2s ease';
                cardEl.style.opacity = '0';
                cardEl.style.transform = 'translateX(20px)';
                setTimeout(() => {
                    loadUserHistory();
                }, 200);
            } else {
                loadUserHistory();
            }
        }
    } catch (e) {
        console.error("Error deleting record:", e);
    }
}

async function clearAllUserHistory() {
    if (!currentToken) return;
    if (!confirm("Are you sure you want to permanently clear all your saved valuation history?")) {
        return;
    }

    try {
        const res = await fetch('/api/predictions/history', {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        if (res.ok) {
            loadUserHistory();
        }
    } catch (e) {
        console.error("Error clearing history:", e);
    }
}

// =========================================================================
// Real-time Vehicle Form Helpers & Live Estimation
// =========================================================================

function updateLiveHelpers() {
    const yearInput = document.getElementById('model_year');
    const milageInput = document.getElementById('milage');
    const agePill = document.getElementById('pill-car-age');
    const ratePill = document.getElementById('pill-mileage-rate');

    const year = parseInt(yearInput.value, 10);
    const milage = parseFloat(milageInput.value);

    if (!isNaN(year)) {
        const age = 2026 - year;
        agePill.textContent = age > 0 ? `Age: ${age} year${age === 1 ? '' : 's'}` : 'New Vehicle (<1 yr)';

        if (!isNaN(milage) && age >= 0) {
            const effectiveAge = age > 0 ? age : 1;
            const rate = Math.round(milage / effectiveAge);
            ratePill.textContent = `Usage Rate: ~${rate.toLocaleString()} mi/yr`;
        }
    }
}

// =========================================================================
// DOM Ready Event Setup
// =========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // 1. Restore persistent user session
    const savedUser = localStorage.getItem('autovaluate_user');
    const savedToken = localStorage.getItem('autovaluate_token');
    if (savedUser && savedToken) {
        try {
            currentUser = JSON.parse(savedUser);
            currentToken = savedToken;
        } catch (e) {
            localStorage.removeItem('autovaluate_user');
            localStorage.removeItem('autovaluate_token');
        }
    }
    updateNavAuthUI();

    // 2. Auth Modal Triggers
    document.getElementById('btn-open-login').addEventListener('click', () => openModal('login'));
    document.getElementById('btn-open-register').addEventListener('click', () => openModal('register'));
    document.getElementById('btn-prompt-login').addEventListener('click', () => openModal('login'));
    document.getElementById('btn-close-modal').addEventListener('click', closeModal);
    authModal.addEventListener('click', (e) => {
        if (e.target === authModal) closeModal();
    });

    tabLogin.addEventListener('click', () => openModal('login'));
    tabRegister.addEventListener('click', () => openModal('register'));

    // 3. User Sign Out
    document.getElementById('btn-logout').addEventListener('click', () => {
        currentUser = null;
        currentToken = null;
        localStorage.removeItem('autovaluate_user');
        localStorage.removeItem('autovaluate_token');
        updateNavAuthUI();
    });

    // 4. Modal Login Submit
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('input-login-email').value.trim();
        const password = document.getElementById('input-login-password').value;

        const btn = document.getElementById('btn-submit-login');
        const btnText = btn.querySelector('.btn-text');
        const btnSpinner = btn.querySelector('.btn-spinner');

        btn.disabled = true;
        btnText.textContent = 'Verifying credentials...';
        btnSpinner.style.display = 'inline-block';

        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();

            if (res.ok && data.user && data.token) {
                currentUser = data.user;
                currentToken = data.token;
                localStorage.setItem('autovaluate_user', JSON.stringify(currentUser));
                localStorage.setItem('autovaluate_token', currentToken);
                closeModal();
                updateNavAuthUI();
            } else {
                showModalError(data.message || "Invalid credentials.");
            }
        } catch (err) {
            showModalError("Unable to reach authentication service.");
        } finally {
            btn.disabled = false;
            btnText.textContent = 'Sign In';
            btnSpinner.style.display = 'none';
        }
    });

    // 5. Modal Register Submit
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('input-reg-name').value.trim();
        const email = document.getElementById('input-reg-email').value.trim();
        const password = document.getElementById('input-reg-password').value;

        const btn = document.getElementById('btn-submit-register');
        const btnText = btn.querySelector('.btn-text');
        const btnSpinner = btn.querySelector('.btn-spinner');

        btn.disabled = true;
        btnText.textContent = 'Creating profile...';
        btnSpinner.style.display = 'inline-block';

        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            const data = await res.json();

            if (res.ok && data.user && data.token) {
                currentUser = data.user;
                currentToken = data.token;
                localStorage.setItem('autovaluate_user', JSON.stringify(currentUser));
                localStorage.setItem('autovaluate_token', currentToken);
                closeModal();
                updateNavAuthUI();
            } else {
                showModalError(data.message || "Registration failed.");
            }
        } catch (err) {
            showModalError("Unable to connect to service.");
        } finally {
            btn.disabled = false;
            btnText.textContent = 'Create Account';
            btnSpinner.style.display = 'none';
        }
    });

    // 6. Clear All History Button
    document.getElementById('btn-clear-history').addEventListener('click', clearAllUserHistory);

    // 7. Mileage Quick Preset Buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const miles = btn.getAttribute('data-miles');
            document.getElementById('milage').value = miles;
            updateLiveHelpers();
        });
    });

    // 8. Live input observers
    document.getElementById('model_year').addEventListener('input', updateLiveHelpers);
    document.getElementById('milage').addEventListener('input', updateLiveHelpers);
    updateLiveHelpers();

    // 9. Reset form
    document.getElementById('btn-reset-form').addEventListener('click', () => {
        document.getElementById('valuation-form').reset();
        document.getElementById('model_year').value = 2021;
        document.getElementById('milage').value = 38000;
        updateLiveHelpers();
        document.getElementById('val-empty-state').style.display = 'block';
        document.getElementById('val-active-state').style.display = 'none';
    });

    // 10. Valuation Form Submission
    const valForm = document.getElementById('valuation-form');
    const predictBtn = document.getElementById('btn-predict-submit');
    const predictBtnText = predictBtn.querySelector('.btn-text');
    const predictBtnSpinner = predictBtn.querySelector('.btn-spinner');
    const formAlert = document.getElementById('form-alert');

    valForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Clear field errors
        document.querySelectorAll('.field-hint').forEach(el => {
            el.textContent = '';
            el.style.display = 'none';
        });
        formAlert.style.display = 'none';

        const formData = new FormData(valForm);
        const payload = {
            brand: formData.get('brand'),
            model_year: parseInt(formData.get('model_year'), 10),
            milage: parseFloat(formData.get('milage')),
            transmission: formData.get('transmission'),
            clean_title: formData.get('clean_title'),
            accident: formData.get('accident'),
            fuel_type: formData.get('fuel_type')
        };

        // Client validation
        let isValid = true;
        if (!payload.brand) {
            const el = document.getElementById('error-brand');
            el.textContent = 'Vehicle make is required.';
            el.style.display = 'block';
            isValid = false;
        }
        if (isNaN(payload.model_year) || payload.model_year < 1990 || payload.model_year > 2026) {
            const el = document.getElementById('error-model_year');
            el.textContent = 'Year must be between 1990 and 2026.';
            el.style.display = 'block';
            isValid = false;
        }
        if (isNaN(payload.milage) || payload.milage < 0) {
            const el = document.getElementById('error-milage');
            el.textContent = 'Valid positive mileage required.';
            el.style.display = 'block';
            isValid = false;
        }

        if (!isValid) return;

        // Loading State
        predictBtn.disabled = true;
        predictBtnText.textContent = 'Processing Valuation Pipeline...';
        predictBtnSpinner.style.display = 'inline-block';

        try {
            const res = await fetch('/predict', {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.message || "Failed to calculate valuation.");
            }

            const pred = data.data;

            // Render Output Card
            document.getElementById('val-empty-state').style.display = 'none';
            document.getElementById('val-active-state').style.display = 'block';

            // Format price without decimals in main hero
            const integerPrice = Math.round(pred.predicted_price).toLocaleString();
            document.getElementById('val-price').textContent = integerPrice;
            document.getElementById('val-range').textContent = pred.price_range_90_pct.formatted;
            document.getElementById('val-model-name').textContent = pred.model_used;
            document.getElementById('val-r2').textContent = (pred.model_test_r2 || 0.6619).toFixed(4);
            document.getElementById('val-log-price').textContent = pred.log_price.toFixed(4);
            document.getElementById('val-timestamp').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            // Insights list
            const insightsContainer = document.getElementById('val-insights-list');
            insightsContainer.innerHTML = '';
            if (pred.insights && pred.insights.length > 0) {
                pred.insights.forEach(insight => {
                    const li = document.createElement('li');
                    li.textContent = insight;
                    insightsContainer.appendChild(li);
                });
            }

            // Refresh History if user is authenticated
            if (currentToken) {
                loadUserHistory();
            }

            // Smooth scroll on small screen
            if (window.innerWidth < 1024) {
                document.getElementById('valuation-card').scrollIntoView({ behavior: 'smooth' });
            }

        } catch (err) {
            formAlert.textContent = err.message || "Inference error occurred.";
            formAlert.style.display = 'block';
        } finally {
            predictBtn.disabled = false;
            predictBtnText.textContent = 'Compute Market Valuation';
            predictBtnSpinner.style.display = 'none';
        }
    });
});
