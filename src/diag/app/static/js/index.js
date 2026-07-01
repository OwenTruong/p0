const metricsBtn = document.getElementById('metrics_btn');
const networkBtn = document.getElementById('network_btn');
const logsBtn = document.getElementById('logs_btn');

const metricsSection = document.getElementById('metrics');
const networkSection = document.getElementById('network');
const logsSection = document.getElementById('logs');

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
  });
}
