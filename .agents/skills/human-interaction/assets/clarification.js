export function clarificationDialog(element, scope, send) {
  const trigger = element("button", {
    type: "button", className: "secondary clarification-trigger", textContent: "Wait.. What?",
  });
  trigger.setAttribute("aria-label", "Wait.. What? about the " + scope);
  const dialog = element("dialog", { className: "clarification-dialog" });
  const id = "clarification-" + scope;
  dialog.setAttribute("aria-labelledby", id + "-title");
  dialog.setAttribute("aria-describedby", id + "-help");
  const title = element("h2", { id: id + "-title", textContent: "Clarify the " + scope });
  const help = element("p", { id: id + "-help", textContent: `Leave the box blank to ask about all the ${scope}.` });
  const label = element("label", { htmlFor: id + "-feedback", textContent: "What needs explaining? (optional)" });
  const feedback = element("textarea", { id: id + "-feedback", rows: 4, maxLength: 2000 });
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
      if (control.name && draft.names.has(control.name)) {
        restoreControl(control, draft.answers.getAll(control.name));
      }
    }
  }
}
