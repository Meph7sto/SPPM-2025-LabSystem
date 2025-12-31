const modeButtons = document.querySelectorAll(".mode-btn");
const body = document.body;

modeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const mode = button.dataset.mode;
    body.dataset.mode = mode;

    modeButtons.forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.mode === mode);
      btn.setAttribute("aria-pressed", btn.dataset.mode === mode ? "true" : "false");
    });
  });
});

const nowLabel = document.querySelector("[data-now]");
if (nowLabel) {
  const formatter = new Intl.DateTimeFormat("zh-CN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
  nowLabel.textContent = `更新于 ${formatter.format(new Date())}`;
}
