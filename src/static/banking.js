/**
 * SecureBank - Banking User Account Dashboard
 * JavaScript logic for login, account overview, transactions, and transfers.
 */

const API_BASE = '/banking';

let currentUser = null;
let userAccounts = [];

// ──────────────────────────────────────────────
// Utilities
// ──────────────────────────────────────────────

function formatCurrency(amount) {
  const abs = Math.abs(amount);
  const formatted = abs.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
  return amount < 0 ? `-${formatted}` : formatted;
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function categoryIcon(category) {
  const icons = {
    'Food & Dining': '🍔',
    'Income': '💼',
    'Bills & Utilities': '💡',
    'Entertainment': '🎬',
    'Transfer': '🔄',
    'Interest': '📈',
    'Shopping': '🛍️',
    'Auto & Transport': '⛽',
    'Payment': '💳',
    'Other': '📄'
  };
  return icons[category] || '📄';
}

function showElement(id) { document.getElementById(id).classList.remove('hidden'); }
function hideElement(id) { document.getElementById(id).classList.add('hidden'); }

// ──────────────────────────────────────────────
// API helpers
// ──────────────────────────────────────────────

async function apiLogin(username, password) {
  const params = new URLSearchParams({ username, password });
  const res = await fetch(`${API_BASE}/login?${params}`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Login failed');
  }
  return res.json();
}

async function apiGetAccounts(username) {
  const res = await fetch(`${API_BASE}/accounts/${encodeURIComponent(username)}`);
  if (!res.ok) throw new Error('Could not load accounts');
  return res.json();
}

async function apiGetTransactions(username, accountNumber, limit = 10) {
  const res = await fetch(
    `${API_BASE}/accounts/${encodeURIComponent(username)}/${encodeURIComponent(accountNumber)}/transactions?limit=${limit}`
  );
  if (!res.ok) throw new Error('Could not load transactions');
  return res.json();
}

async function apiTransfer(username, fromAccount, toAccount, amount, description) {
  const params = new URLSearchParams({
    username,
    from_account: fromAccount,
    to_account: toAccount,
    amount,
    description: description || 'Transfer'
  });
  const res = await fetch(`${API_BASE}/transfer?${params}`, { method: 'POST' });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Transfer failed');
  return data;
}

// ──────────────────────────────────────────────
// Login
// ──────────────────────────────────────────────

document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('login-error');

  errorDiv.classList.add('hidden');
  errorDiv.textContent = '';

  try {
    const user = await apiLogin(username, password);
    currentUser = user;
    sessionStorage.setItem('bankUser', JSON.stringify(user));
    showDashboard();
  } catch (err) {
    errorDiv.textContent = err.message;
    errorDiv.classList.remove('hidden');
  }
});

// ──────────────────────────────────────────────
// Dashboard Initialization
// ──────────────────────────────────────────────

async function showDashboard() {
  hideElement('login-screen');
  const dash = document.getElementById('dashboard-screen');
  dash.classList.remove('hidden');

  document.getElementById('header-display-name').textContent = currentUser.display_name;

  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
  document.getElementById('greeting-text').textContent =
    `${greeting}, ${currentUser.display_name}! Here's your financial summary.`;

  await loadAccounts();
  switchSection('overview');
}

async function loadAccounts() {
  try {
    userAccounts = await apiGetAccounts(currentUser.username);
    populateAccountSelects();
  } catch (err) {
    console.error('Error loading accounts:', err);
  }
}

// ──────────────────────────────────────────────
// Navigation
// ──────────────────────────────────────────────

document.querySelectorAll('.nav-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    switchSection(btn.dataset.section);
  });
});

function switchSection(name) {
  document.querySelectorAll('.nav-btn').forEach((b) => {
    b.classList.toggle('active', b.dataset.section === name);
  });
  document.querySelectorAll('.dashboard-section').forEach((s) => {
    s.classList.add('hidden');
  });
  document.getElementById(`section-${name}`).classList.remove('hidden');

  if (name === 'overview') renderOverview();
  if (name === 'transactions') renderTransactionsSection();
}

// ──────────────────────────────────────────────
// Overview Section
// ──────────────────────────────────────────────

async function renderOverview() {
  renderAccountCards();
  await renderRecentTransactions();
}

function renderAccountCards() {
  const container = document.getElementById('accounts-container');
  if (!userAccounts.length) {
    container.innerHTML = '<p class="loading-text">No accounts found.</p>';
    return;
  }

  let netWorth = 0;
  container.innerHTML = userAccounts.map((acc) => {
    netWorth += acc.balance;
    const isNegative = acc.balance < 0;
    const balanceClass = isNegative ? 'negative' : '';
    const icon = acc.account_type === 'checking' ? '🏦'
               : acc.account_type === 'savings'  ? '💰'
               : '💳';

    let creditBar = '';
    if (acc.account_type === 'credit' && acc.credit_limit) {
      const used = Math.abs(acc.balance);
      const pct = Math.min((used / acc.credit_limit) * 100, 100).toFixed(1);
      creditBar = `
        <div class="credit-limit-bar">
          <div class="credit-limit-bar-bg">
            <div class="credit-limit-bar-fill" style="width:${pct}%"></div>
          </div>
          <div class="credit-limit-text">
            <span>Used: ${formatCurrency(used)}</span>
            <span>Limit: ${formatCurrency(acc.credit_limit)}</span>
          </div>
        </div>`;
    }

    return `
      <div class="account-card ${acc.account_type}">
        <div class="account-card-header">
          <span class="account-type-badge">${acc.account_type}</span>
          <span class="account-icon">${icon}</span>
        </div>
        <div class="account-name">${acc.account_name}</div>
        <div class="account-number">•••• ${acc.account_number.slice(-4)}</div>
        <div class="account-balance-label">Current Balance</div>
        <div class="account-balance ${balanceClass}">${formatCurrency(acc.balance)}</div>
        ${creditBar}
      </div>`;
  }).join('');

  const nwCard = document.getElementById('net-worth-card');
  document.getElementById('net-worth-amount').textContent = formatCurrency(netWorth);
  nwCard.style.display = '';
}

async function renderRecentTransactions() {
  const container = document.getElementById('recent-transactions-list');
  if (!userAccounts.length) {
    container.innerHTML = '<p class="loading-text">No accounts available.</p>';
    return;
  }

  try {
    // Load transactions for the first (primary) account
    const primaryAccount = userAccounts.find((a) => a.account_type === 'checking') || userAccounts[0];
    const txns = await apiGetTransactions(currentUser.username, primaryAccount.account_number, 5);
    renderTransactionRows(container, txns);
  } catch (err) {
    container.innerHTML = '<p class="loading-text">Could not load transactions.</p>';
  }
}

function renderTransactionRows(container, transactions) {
  if (!transactions.length) {
    container.innerHTML = '<p class="loading-text">No transactions found.</p>';
    return;
  }
  container.innerHTML = transactions.map((txn) => `
    <div class="transaction-row">
      <div class="transaction-icon">${categoryIcon(txn.category)}</div>
      <div class="transaction-details">
        <div class="transaction-description">${txn.description}</div>
        <div class="transaction-meta">
          <span>${formatDate(txn.date)}</span>
          <span class="transaction-category">${txn.category}</span>
        </div>
      </div>
      <div class="transaction-amount ${txn.type}">
        ${txn.type === 'credit' ? '+' : '-'}${formatCurrency(txn.amount)}
      </div>
    </div>
  `).join('');
}

// ──────────────────────────────────────────────
// Transactions Section
// ──────────────────────────────────────────────

function renderTransactionsSection() {
  const select = document.getElementById('txn-account-select');
  if (select.options.length > 0) {
    loadTransactionsForSelectedAccount();
  }
}

function populateAccountSelects() {
  const txnSelect = document.getElementById('txn-account-select');
  const fromSelect = document.getElementById('from-account');
  const toSelect = document.getElementById('to-account');

  const options = userAccounts.map((acc) =>
    `<option value="${acc.account_number}">${acc.account_name} (${acc.account_number})</option>`
  ).join('');

  txnSelect.innerHTML = options;
  fromSelect.innerHTML = options;
  toSelect.innerHTML = options;

  // Default to-account to second account if available
  if (userAccounts.length >= 2) {
    toSelect.value = userAccounts[1].account_number;
  }
}

document.getElementById('txn-account-select').addEventListener('change', loadTransactionsForSelectedAccount);

async function loadTransactionsForSelectedAccount() {
  const accountNumber = document.getElementById('txn-account-select').value;
  const container = document.getElementById('transactions-table-container');
  container.innerHTML = '<p class="loading-text">Loading…</p>';
  try {
    const txns = await apiGetTransactions(currentUser.username, accountNumber, 20);
    const wrapper = document.createElement('div');
    wrapper.className = 'transactions-list';
    container.innerHTML = '';
    renderTransactionRows(wrapper, txns);
    container.appendChild(wrapper);
  } catch (err) {
    container.innerHTML = '<p class="loading-text">Could not load transactions.</p>';
  }
}

// ──────────────────────────────────────────────
// Transfer Section
// ──────────────────────────────────────────────

document.getElementById('transfer-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fromAccount = document.getElementById('from-account').value;
  const toAccount = document.getElementById('to-account').value;
  const amount = parseFloat(document.getElementById('transfer-amount').value);
  const description = document.getElementById('transfer-description').value.trim();
  const msgBox = document.getElementById('transfer-message');

  msgBox.className = 'message-box hidden';
  msgBox.textContent = '';

  if (fromAccount === toAccount) {
    msgBox.className = 'message-box error';
    msgBox.textContent = 'Source and destination accounts must be different.';
    return;
  }

  try {
    const result = await apiTransfer(
      currentUser.username,
      fromAccount,
      toAccount,
      amount,
      description || 'Transfer'
    );
    msgBox.className = 'message-box success';
    msgBox.textContent = result.message;
    document.getElementById('transfer-amount').value = '';
    document.getElementById('transfer-description').value = '';

    // Refresh account data
    await loadAccounts();
  } catch (err) {
    msgBox.className = 'message-box error';
    msgBox.textContent = err.message;
  }
});

// ──────────────────────────────────────────────
// Logout
// ──────────────────────────────────────────────

document.getElementById('logout-btn').addEventListener('click', () => {
  currentUser = null;
  userAccounts = [];
  sessionStorage.removeItem('bankUser');
  hideElement('dashboard-screen');
  showElement('login-screen');
  document.getElementById('login-form').reset();
  document.getElementById('login-error').classList.add('hidden');
});

// ──────────────────────────────────────────────
// Session restore on page load
// ──────────────────────────────────────────────

(function init() {
  const saved = sessionStorage.getItem('bankUser');
  if (saved) {
    try {
      currentUser = JSON.parse(saved);
      showDashboard();
    } catch (_) {
      sessionStorage.removeItem('bankUser');
    }
  }
})();
