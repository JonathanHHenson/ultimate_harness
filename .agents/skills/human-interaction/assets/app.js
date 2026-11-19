import { renderMarkdown } from "./markdown.js";

const main = document.querySelector("main");
const multiKinds = new Set(["multiselect", "checkbox-group"]);
let revision = -1;
let terminal = false;
let expiresAt = null;
let pollTimer;
let polling = false;

function element(tag, properties = {}, ...children) {
  const node = Object.assign(document.createElement(tag), properties);
  node.append(...children);
  return node;
}

function labelText(field) {
  return field.label + (field.required ? " *" : "");
}

function help(container, field) {
  if (field.help) {
    container.append(element("p", { className: "hint", id: "help-" + field.id, textContent: field.help }));
  }
}

function describe(control, field) {
  if (field.help) control.setAttribute("aria-describedby", "help-" + field.id);
}

function choices(field) {
  const group = element("fieldset", { className: "field" + (field.wide ? " wide" : "") });
  group.append(element("legend", { textContent: labelText(field) }));
  const radio = field.type === "radio";
  for (const option of field.options) {
    const control = element("input", {
      type: radio ? "radio" : "checkbox", name: field.id, value: option.value,
      checked: radio ? field.default === option.value : (field.default ?? []).includes(option.value),
      required: radio && Boolean(field.required),
    });
    describe(control, field);
    group.append(element("label", { className: "choice" }, control, element("span", { textContent: option.label })));
  }
  help(group, field);
  return group;
}

function controlFor(field) {
  const kind = field.type;
  if (kind === "select" || kind === "multiselect") {
    const multiple = kind === "multiselect";
    const select = element("select", { multiple });
    if (!multiple) select.append(element("option", { value: "", textContent: field.placeholder ?? "Choose an option" }));
    for (const option of field.options) {
      select.append(element("option", {
        value: option.value, textContent: option.label,
        selected: multiple ? (field.default ?? []).includes(option.value) : field.default === option.value,
      }));
    }
    return select;
  }
  if (kind === "textarea") return element("textarea", { rows: field.rows ?? 4 });
  return element("input", { type: kind });
}

function configureControl(control, field) {
  control.id = "field-" + field.id;
  control.name = field.id;
  control.required = Boolean(field.required);
  if (field.type === "number") control.step = "any";
  describe(control, field);
  for (const [key, attribute] of Object.entries({
    min: "min", max: "max", step: "step", min_length: "minlength",
    max_length: "maxlength", placeholder: "placeholder",
  })) {
    if (field[key] !== undefined) control.setAttribute(attribute, String(field[key]));
  }
}

function sectionHeading(field) {
  const section = element("section", { className: "section" }, element("h2", { textContent: field.label }));
  if (field.help) section.append(element("p", { className: "hint", textContent: field.help }));
  return section;
}

function fieldNode(field) {
  if (field.type === "section") return sectionHeading(field);
  if (field.type === "radio" || field.type === "checkbox-group") return choices(field);
  const block = element("div", { className: "field" + (field.wide || field.type === "textarea" ? " wide" : "") });
  const control = controlFor(field);
  configureControl(control, field);
  if (field.type === "checkbox") {
    control.checked = Boolean(field.default);
    block.append(element("label", { className: "choice" }, control, element("span", { textContent: labelText(field) })));
  } else {
    if (!(control instanceof HTMLSelectElement) && field.default != null) control.value = field.default;
    block.append(element("label", { htmlFor: control.id, textContent: labelText(field) }), control);
  }
  if (field.type === "range") {
    const output = element("output", { textContent: control.value });
    output.setAttribute("for", control.id);
    control.addEventListener("input", () => { output.textContent = control.value; });
    block.append(output);
  }
  help(block, field);
  return block;
}

async function request(route, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  const options = { signal: controller.signal };
  if (body !== undefined) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  try {
    const response = await fetch("./" + route, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error ?? "The form is unavailable.");
    return result;
  } finally {
    clearTimeout(timer);
  }
}

function readValues(form, fields) {
  const data = new FormData(form);
  const pairs = fields.filter(field => field.type !== "section").map(field => {
    const raw = data.get(field.id);
    let value = raw ?? "";
    if (field.type === "checkbox") value = data.has(field.id);
    if (multiKinds.has(field.type)) value = data.getAll(field.id);
    if (field.type === "number" || field.type === "range") value = raw ? Number(raw) : null;
    return [field.id, value];
  });
  return Object.fromEntries(pairs);
}

function focusHeading() {
  const heading = main.querySelector("h1");
  heading.tabIndex = -1;
  heading.focus();
}

function renderForm(state) {
  const page = state.form;
  const form = element("form");
  const error = element("p", { className: "error", hidden: true });
  error.setAttribute("role", "alert");
  const button = element("button", { type: "submit", textContent: page.submit_label ?? "Submit answers" });
  const section = element("div", { className: "fields" }, ...page.fields.map(fieldNode));
  form.append(section, error, button);
  if (state.multi) main.append(element("p", { className: "page-label", textContent: "Page " + state.page }));
  main.append(element("h1", { textContent: page.title }));
  if (page.markdown) {
    const prologue = element("div", { className: "prologue" });
    renderMarkdown(prologue, page.markdown, page.images ?? {});
    main.append(prologue);
  }
  main.append(form);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    button.disabled = true;
    error.hidden = true;
    try {
      const result = await request("submit", { page: state.page, answers: readValues(form, page.fields) });
      render(result);
    } catch (failure) {
      error.textContent = failure.message;
      error.hidden = false;
    } finally {
      button.disabled = false;
    }
  });
}

function statusView(title, copy, waiting, success = false) {
  const box = element("div", { className: "status" });
  box.setAttribute("role", "status");
  if (waiting || success) {
    const icon = element("span", { className: waiting ? "spinner" : "badge", textContent: success ? "✓" : "" });
    icon.setAttribute("aria-hidden", "true");
    box.append(icon);
  }
  box.append(element("h1", { textContent: title }), element("p", { textContent: copy }));
  main.append(box);
}

function rankOf(state) {
  return 4 * state.page + ({ form: 0, waiting: 1, complete: 2, expired: 2 }[state.view] ?? 0);
}

function rememberDeadline(state) {
  if (rankOf(state) >= revision && Number.isFinite(state.expires_at_ms)) {
    expiresAt = state.expires_at_ms;
  }
}

function render(state) {
  rememberDeadline(state);
  const rank = rankOf(state);
  if (rank <= revision) return;
  revision = rank;
  main.replaceChildren();
  main.setAttribute("aria-busy", "false");
  if (state.view === "form") renderForm(state);
  else if (state.view === "waiting") {
    statusView("Answers received", "Please keep this tab open while the agent prepares the next questions.", true);
  } else {
    terminal = true;
    const success = state.view === "complete" && state.submitted > 0;
    const title = success ? "Submission complete" : state.view === "expired" ? "Form expired" : "Form closed";
    const message = state.view === "expired"
      ? "This session reached its time limit. Close this tab and return to the agent."
      : "You can close this tab and return to the agent.";
    statusView(title, message, false, success);
    void request("ack", {}).catch(() => {});
  }
  document.title = main.querySelector("h1").textContent + " · Feedback form";
  focusHeading();
}

async function refresh() {
  if (terminal || polling) return;
  clearTimeout(pollTimer);
  polling = true;
  try {
    const state = await request("state");
    rememberDeadline(state);
    if (rankOf(state) > revision) render(state.view === "form" ? await request("page") : state);
  } catch {
    if (expiresAt !== null && Date.now() >= expiresAt) {
      // A tab may resume after the server's final grace period has elapsed.
      render({ view: "expired", page: Math.max(1, Math.floor(revision / 4)), submitted: 0 });
    } else if (revision < 0) {
      main.replaceChildren();
      main.setAttribute("aria-busy", "false");
      statusView("Trying to connect", "Keep this tab open or return to the agent if the form has ended.", true);
    }
  } finally {
    polling = false;
    if (!terminal) pollTimer = setTimeout(refresh, 1250);
  }
}

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) void refresh();
});
void refresh();
