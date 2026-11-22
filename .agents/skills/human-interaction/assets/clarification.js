export function clarificationDialog(element, send) {
  const trigger = element("button", { type: "button", className: "secondary", textContent: "Wait.. What?" });
  const dialog = element("dialog", { className: "clarification-dialog" });
  dialog.setAttribute("aria-labelledby", "clarification-title");
  dialog.setAttribute("aria-describedby", "clarification-help");
  const title = element("h2", { id: "clarification-title", textContent: "Ask for a clearer explanation" });
  const help = element("p", { id: "clarification-help", textContent: "Leave the box blank to ask about the whole page." });
  const label = element("label", { htmlFor: "clarification-feedback", textContent: "What needs explaining? (optional)" });
  const feedback = element("textarea", { id: "clarification-feedback", rows: 4, maxLength: 2000 });
  const cancel = element("button", { type: "button", className: "secondary", textContent: "Cancel" });
  const submit = element("button", { type: "submit", textContent: "Ask for clarification" });
  const error = element("p", { className: "error", hidden: true });
  error.setAttribute("role", "alert");
  const form = element("form", {}, label, feedback, error, element("div", { className: "actions" }, submit, cancel));
  dialog.append(title, help, form);
  trigger.addEventListener("click", () => { dialog.showModal(); feedback.focus(); });
  cancel.addEventListener("click", () => { dialog.close(); });
  dialog.addEventListener("close", () => { trigger.focus(); });
  form.addEventListener("submit", async event => {
    event.preventDefault();
    submit.disabled = true;
    error.hidden = true;
    try {
      await send(feedback.value, dialog);
    } catch (failure) {
      error.textContent = failure.message;
      error.hidden = false;
    } finally {
      submit.disabled = false;
    }
  });
  return { trigger, dialog };
}

function restoreControl(control, values) {
  if (control instanceof HTMLSelectElement) {
    for (const option of control.options) option.selected = values.includes(option.value);
  } else if (control.type === "checkbox" || control.type === "radio") {
    control.checked = values.includes(control.value);
  } else {
    control.value = values[0] ?? "";
    control.dispatchEvent(new Event("input"));
  }
}

export function restoreDraft(form, draft) {
  if (draft) {
    for (const control of form.elements) {
      if (control.name) restoreControl(control, draft.getAll(control.name));
    }
  }
}
