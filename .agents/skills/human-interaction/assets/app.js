import { clarificationDialog, restoreDraft } from "./clarification.js";
import { renderMarkdown } from "./markdown.js";
import { questionPager } from "./question-pages.js";

const main = document.querySelector("main");
const multiKinds = new Set(["multiselect", "checkbox-group"]);
let revision = -1;
let terminal = false;
let expiresAt = null;
let pollTimer;
let polling = false;
let draftPage;
let draft;

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
  if (!radio && field.required) group.dataset.requiredGroup = "";
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

function clarification(state, scope, questionContext = () => ({})) {
  return clarificationDialog(element, scope, async (feedback, modal) => {
    const result = await request("clarify", {
      page: state.page, revision: state.revision, scope, feedback, ...questionContext(),
    });
    modal.close();
    render(result);
  });
}

function renderContext(state) {
  const page = state.form;
  const intro = element("header", { className: "intro" });
  if (state.multi) intro.append(element("p", { className: "page-label", textContent: "Round " + state.page }));
  intro.append(element("h1", { textContent: page.title }));
  const context = element("div", { className: "context" });
  const help = clarification(state, "context");
  if (page.markdown) {
    const prologue = element("div", { className: "prologue" });
    renderMarkdown(prologue, page.markdown, page.images ?? {});
    context.append(prologue);
  }
  context.append(help.trigger, help.dialog);
  main.append(intro, context);
}

function renderForm(state) {
  const page = state.form;
  const form = element("form", { noValidate: true });
  form.dataset.answerPage = state.page;
  const error = element("p", { className: "error", hidden: true });
  error.setAttribute("role", "alert");
  const button = element("button", { type: "submit", textContent: page.submit_label ?? "Submit answers" });
  const pager = questionPager(form, page.fields, fieldNode, element, button, draft?.step);
  const questions = clarification(state, "questions", pager.questionContext);
  form.append(element("h2", { textContent: "Questions" }));
  if (page.fields.some(field => field.default !== undefined)) {
    form.append(element("p", { className: "hint", textContent: "Some answers are prefilled. Review or change them before submitting." }));
  }
  form.append(pager.indicator, ...pager.panels, error,
    element("div", { className: "actions" }, questions.trigger, ...pager.navigation));
  restoreDraft(form, draft);
  renderContext(state);
  main.append(form, questions.dialog);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (!pager.readyToSubmit()) return;
    button.disabled = true;
    error.hidden = true;
    try {
      const result = await request("submit", {
        page: state.page, revision: state.revision, answers: readValues(form, page.fields),
      });
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
  const message = element("p", { textContent: copy });
  box.append(element("h1", { textContent: title }), message);
  main.append(box);
  return message;
}

function acknowledge() {
  terminal = true;
  void request("ack", {}).catch(() => {});
}

function deliveryMessage(state) {
  const clarification = state.view === "clarifying";
  const item = clarification ? "clarification request" : "answers";
  if (state.agent_status === "received") {
    const next = state.view === "complete" ? "You can close this tab." : "Keep this tab open for the next update.";
    return `The agent received your ${item}. ${next}`;
  }
  if (state.agent_status === "listening") {
    return `The agent is listening for your ${item}. Keep this tab open.`;
  }
  const saved = clarification ? "Your clarification request is saved." : "Your answers are saved.";
  return saved + " Send the agent a message in chat so it can respond.";
}

function updateDeliveryStatus(state) {
  const message = main.querySelector("[data-agent-status]");
  if (!message) return;
  const copy = deliveryMessage(state);
  if (message.textContent !== copy) message.textContent = copy;
  if (state.view === "complete" && state.agent_status !== "listening") acknowledge();
}

function showDeliveryStatus(state, title, waiting, success = false) {
  const message = statusView(title, "", waiting, success);
  message.dataset.agentStatus = state.view;
  updateDeliveryStatus(state);
}

function renderStatus(state) {
  if (state.view === "waiting") {
    showDeliveryStatus(state, "Answers saved", true);
    return;
  }
  if (state.view === "clarifying") {
    showDeliveryStatus(state, "Clarification requested", true);
    return;
  }
  draft = null;
  const success = state.view === "complete" && state.submitted > 0;
  if (success && !state.multi) {
    showDeliveryStatus(state, "Submission complete", false, true);
    return;
  }
  const title = success ? "Submission complete" : state.view === "expired" ? "Form expired" : "Form closed";
  const message = state.view === "expired"
    ? "This session reached its time limit. Close this tab and return to the agent."
    : "You can close this tab and return to the agent.";
  statusView(title, message, false, success);
  acknowledge();
}

function rememberDraft(state) {
  if (draftPage !== state.page) draft = null;
  const form = main.querySelector(`form[data-answer-page="${state.page}"]`);
  if (form) {
    draft = {
      answers: new FormData(form),
      names: new Set(Array.from(form.elements, control => control.name)),
      step: Number(form.dataset.questionPage),
    };
  }
  draftPage = state.page;
}

function rememberDeadline(state) {
  if (state.revision >= revision && Number.isFinite(state.expires_at_ms)) {
    expiresAt = state.expires_at_ms;
  }
}

function render(state) {
  rememberDeadline(state);
  if (state.revision <= revision) return;
  rememberDraft(state);
  revision = state.revision;
  main.replaceChildren();
  main.setAttribute("aria-busy", "false");
  if (state.view === "form") renderForm(state);
  else renderStatus(state);
  document.title = main.querySelector("h1").textContent + " · Feedback form";
  focusHeading();
}

function showConnectionFailure() {
  if (main.querySelector('[data-agent-status="complete"]')) {
    updateDeliveryStatus({ view: "complete", agent_status: "away" });
  } else if (expiresAt !== null && Date.now() >= expiresAt) {
    // A tab may resume after the server's final grace period has elapsed.
    render({ view: "expired", page: draftPage, revision: revision + 1, submitted: 0 });
  } else if (revision < 0) {
    main.replaceChildren();
    main.setAttribute("aria-busy", "false");
    statusView("Trying to connect", "Keep this tab open or return to the agent if the form has ended.", true);
  }
}

async function refresh() {
  if (terminal || polling) return;
  clearTimeout(pollTimer);
  polling = true;
  try {
    const state = await request("state");
    rememberDeadline(state);
    if (state.revision > revision) render(state.view === "form" ? await request("page") : state);
    else if (state.revision === revision) updateDeliveryStatus(state);
  } catch {
    showConnectionFailure();
  } finally {
    polling = false;
    if (!terminal) pollTimer = setTimeout(refresh, 1250);
  }
}

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) void refresh();
});
void refresh();
