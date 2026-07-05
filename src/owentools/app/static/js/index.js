const metricsBtn = document.getElementById('metrics_btn');
const networkBtn = document.getElementById('network_btn');
const logsBtn = document.getElementById('logs_btn');

const metricsSection = document.getElementById('metrics');
const networkSection = document.getElementById('network');
const logsSection = document.getElementById('logs');

const activeClasses = ['border-indigo-600', 'text-indigo-600', 'font-semibold'];
const inactiveClasses = ['border-transparent', 'text-gray-500', 'font-medium'];

for (const [btn, section] of [
  [metricsBtn, metricsSection],
  [networkBtn, networkSection],
  [logsBtn, logsSection],
]) {
  btn.addEventListener('click', (e) => {
    metricsSection.hidden = true;
    networkSection.hidden = true;
    logsSection.hidden = true;

    section.hidden = false;

    for (const otherBtn of [metricsBtn, networkBtn, logsBtn]) {
      otherBtn.classList.remove(...activeClasses);
      otherBtn.classList.add(...inactiveClasses);
    }

    btn.classList.remove(...inactiveClasses);
    btn.classList.add(...activeClasses);
  });
}
