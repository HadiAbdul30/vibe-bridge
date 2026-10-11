/**
 * VibeBridge Control Center - Modular Client JS
 * Handles Sidebar Tab Switching & View State
 */

function switchTab(tabId) {
  // Hide all tab contents
  document.querySelectorAll('.tab-content').forEach(el => {
    el.classList.add('hidden');
  });

  // Remove active styles from all nav buttons
  document.querySelectorAll('aside nav button').forEach(btn => {
    btn.classList.remove('text-white', 'bg-surfaceHover', 'border', 'border-borderSubtle');
    btn.classList.add('text-slate-400');
  });

  // Show target tab
  const targetTab = document.getElementById(`tab-${tabId}`);
  if (targetTab) {
    targetTab.classList.remove('hidden');
  }

  // Activate target nav button
  const targetNav = document.getElementById(`nav-${tabId}`);
  if (targetNav) {
    targetNav.classList.remove('text-slate-400');
    targetNav.classList.add('text-white', 'bg-surfaceHover', 'border', 'border-borderSubtle');
  }

  // Update breadcrumb
  const breadcrumbCurrent = document.getElementById('breadcrumb-current');
  if (breadcrumbCurrent) {
    const titles = {
      'overview': 'Overview',
      'pipelines': 'Pipelines',
      'credentials': 'Credentials',
      'audit': 'Audit Trail'
    };
    breadcrumbCurrent.textContent = titles[tabId] || 'Dashboard';
  }
}

window.switchTab = switchTab;