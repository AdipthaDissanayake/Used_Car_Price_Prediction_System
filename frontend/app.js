// Used Car Price Prediction System - Frontend Client Logic with Google Auth & MySQL History

let currentUser = null;

// Parse JWT without external library
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        console.error("JWT parse error:", e);
        return null;
    }
}

// Global callback for Google Identity Services
window.handleGoogleCredentialResponse = async function(response) {
    const idToken = response.credential;
    const userProfile = parseJwt(idToken);

    try {
        const authRes = await fetch('/api/auth/google', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                credential: idToken,
                user: userProfile
            })
        });

        const data = await authRes.json();
        if (authRes.ok && data.user) {
            currentUser = data.user;
            localStorage.setItem('used_car_user', JSON.stringify(currentUser));
            updateAuthUI();
            loadHistory();
        } else {
            console.error("Auth error:", data.message);
        }
    } catch (err) {
        console.error("Google Auth request failed:", err);
    }
};

function updateAuthUI() {
    const loginBox = document.getElementById('google-login-container');
    const profileBox = document.getElementById('user-profile-box');
    const userAvatar = document.getElementById('user-avatar');
    const userName = document.getElementById('user-name');
    const userEmail = document.getElementById('user-email');

    if (currentUser) {
        loginBox.style.display = 'none';
        profileBox.style.display = 'flex';
        userName.textContent = currentUser.name || 'User';
        userEmail.textContent = currentUser.email || '';
        userAvatar.src = currentUser.picture || 'https://www.gravatar.com/avatar/?d=mp';
    } else {
        loginBox.style.display = 'block';
        profileBox.style.display = 'none';
    }
}

async function loadHistory() {
    const historyList = document.getElementById('history-list');
    try {
        const url = currentUser ? `/api/predictions/history?user_id=${currentUser.id}&limit=8` : '/api/predictions/history?limit=8';
        const res = await fetch(url);
        const json = await res.json();
        if (res.ok && json.data && json.data.length > 0) {
            historyList.innerHTML = '';
            json.data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `
                    <div class="history-item-details">
                        <span class="history-item-title">${item.model_year} ${item.brand}</span>
                        <span class="history-item-sub">${Number(item.milage).toLocaleString()} mi • ${item.fuel_type} • ${item.created_at || ''}</span>
                    </div>
                    <span class="history-item-price">${item.predicted_price_formatted}</span>
                `;
                historyList.appendChild(div);
            });
        } else {
            historyList.innerHTML = '<div class="history-empty">No valuations recorded yet.</div>';
        }
    } catch (e) {
        console.error("Failed to load history:", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Check saved user session
    const savedUser = localStorage.getItem('used_car_user');
    if (savedUser) {
        try {
            currentUser = JSON.parse(savedUser);
            updateAuthUI();
        } catch (e) {
            localStorage.removeItem('used_car_user');
        }
    }

    // Sign out button
    document.getElementById('logout-btn').addEventListener('click', () => {
        currentUser = null;
        localStorage.removeItem('used_car_user');
        updateAuthUI();
        loadHistory();
    });

    // Refresh history button
    document.getElementById('refresh-history-btn').addEventListener('click', loadHistory);

    // Initial load of history
    loadHistory();

    const form = document.getElementById('prediction-form');
    const submitBtn = document.getElementById('submit-btn');
    const resetBtn = document.getElementById('reset-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.btn-spinner');
    const formAlert = document.getElementById('form-alert');

    const yearInput = document.getElementById('model_year');
    const milageInput = document.getElementById('milage');
    const yearHelper = document.getElementById('year-helper');
    const mileageHelper = document.getElementById('mileage-helper');

    const resultsPlaceholder = document.getElementById('results-placeholder');
    const resultsContent = document.getElementById('results-content');
    const displayPrice = document.getElementById('display-price');
    const displayRange = document.getElementById('display-range');
    const displayModel = document.getElementById('display-model');
    const displayR2 = document.getElementById('display-r2');
    const displayLog = document.getElementById('display-log');
    const insightsList = document.getElementById('insights-list');

    // Live helper calculations
    function updateHelpers() {
        const year = parseInt(yearInput.value, 10);
        const milage = parseFloat(milageInput.value);

        if (!isNaN(year)) {
            const age = 2026 - year;
            yearHelper.textContent = `Vehicle Age: ${age > 0 ? age + ' years' : 'Brand new (<1 yr)'}`;
            
            if (!isNaN(milage) && age >= 0) {
                const effectiveAge = age > 0 ? age : 1;
                const mpy = Math.round(milage / effectiveAge);
                mileageHelper.textContent = `Annual Usage: ~${mpy.toLocaleString()} mi/yr`;
            }
        }
    }

    yearInput.addEventListener('input', updateHelpers);
    milageInput.addEventListener('input', updateHelpers);
    updateHelpers();

    function showAlert(msg, isError = true) {
        formAlert.textContent = msg;
        formAlert.className = `alert-box ${isError ? 'error' : 'success'}`;
        formAlert.style.display = 'block';
    }

    function clearAlert() {
        formAlert.style.display = 'none';
        formAlert.textContent = '';
    }

    function clearErrors() {
        document.querySelectorAll('.field-error').forEach(el => {
            el.textContent = '';
            el.style.display = 'none';
        });
        clearAlert();
    }

    function setFieldError(fieldId, errorMsg) {
        const errorEl = document.getElementById(`error-${fieldId}`);
        if (errorEl) {
            errorEl.textContent = errorMsg;
            errorEl.style.display = 'block';
        }
    }

    function validateForm(data) {
        clearErrors();
        let isValid = true;

        if (!data.brand) {
            setFieldError('brand', 'Please select a vehicle brand.');
            isValid = false;
        }

        const year = parseInt(data.model_year, 10);
        if (isNaN(year) || year < 1990 || year > 2026) {
            setFieldError('model_year', 'Year must be between 1990 and 2026.');
            isValid = false;
        }

        const milage = parseFloat(data.milage);
        if (isNaN(milage) || milage < 0) {
            setFieldError('milage', 'Mileage cannot be negative.');
            isValid = false;
        } else if (milage > 1500000) {
            setFieldError('milage', 'Mileage exceeds maximum supported limit (1,500,000).');
            isValid = false;
        }

        if (!data.transmission) {
            setFieldError('transmission', 'Please select a transmission type.');
            isValid = false;
        }

        if (!data.clean_title) {
            setFieldError('clean_title', 'Please specify title status.');
            isValid = false;
        }

        if (!data.accident) {
            setFieldError('accident', 'Please specify accident history.');
            isValid = false;
        }

        if (!data.fuel_type) {
            setFieldError('fuel_type', 'Please select a fuel type.');
            isValid = false;
        }

        return isValid;
    }

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const payload = {
            brand: formData.get('brand'),
            model_year: parseInt(formData.get('model_year'), 10),
            milage: parseFloat(formData.get('milage')),
            transmission: formData.get('transmission'),
            clean_title: formData.get('clean_title'),
            accident: formData.get('accident'),
            fuel_type: formData.get('fuel_type'),
            user_id: currentUser ? currentUser.id : null
        };

        if (!validateForm(payload)) {
            showAlert('Please correct the highlighted fields before submitting.');
            return;
        }

        // Set Loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Calculating...';
        btnSpinner.style.display = 'inline-block';
        clearAlert();

        try {
            const apiUrl = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
                ? '/predict'
                : 'http://localhost:5000/predict';

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `Server responded with status ${response.status}`);
            }

            const pred = data.data;

            // Update UI with results
            displayPrice.textContent = pred.predicted_price_formatted;
            displayRange.textContent = pred.price_range_90_pct.formatted;
            displayModel.textContent = pred.model_used;
            displayR2.textContent = pred.model_test_r2 ? pred.model_test_r2.toFixed(4) : '0.6619';
            displayLog.textContent = pred.log_price.toFixed(4);

            // Populate insights
            insightsList.innerHTML = '';
            if (pred.insights && pred.insights.length > 0) {
                pred.insights.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    insightsList.appendChild(li);
                });
            }

            resultsPlaceholder.style.display = 'none';
            resultsContent.style.display = 'block';

            // Refresh recent database history
            loadHistory();

            if (window.innerWidth < 900) {
                document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
            }

        } catch (err) {
            console.error('Prediction request error:', err);
            showAlert(`Prediction error: ${err.message || 'Unable to connect to backend server.'}`);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Estimate Market Value';
            btnSpinner.style.display = 'none';
        }
    });

    // Reset button
    resetBtn.addEventListener('click', () => {
        form.reset();
        clearErrors();
        updateHelpers();
        resultsContent.style.display = 'none';
        resultsPlaceholder.style.display = 'block';
    });
});
