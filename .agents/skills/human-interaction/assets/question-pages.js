const questionsPerPage = 5;

function splitQuestions(fields) {
  const pages = [[]];
  let questionCount = 0;
  let headings = [];
  for (const field of fields) {
    if (field.type === "section") {
      headings.push(field);
      continue;
    }
    if (questionCount === questionsPerPage) {
      pages.push([]);
      questionCount = 0;
    }
    pages.at(-1).push(...headings, field);
    headings = [];
    questionCount++;
  }
  pages.at(-1).push(...headings);
  return pages;
}

function invalidControl(panel) {
  for (const group of panel.querySelectorAll("[data-required-group]")) {
    const message = group.querySelector("input:checked") ? "" : "Choose at least one option.";
    group.querySelector("input").setCustomValidity(message);
  }
  return panel.querySelector("input:invalid, select:invalid, textarea:invalid");
}

export function questionPager(form, fields, fieldNode, element, submit, startAt = 0) {
  const pages = splitQuestions(fields);
  const panels = pages.map(group => element("div", { className: "fields" }, ...group.map(fieldNode)));
  const count = panels.length;
  const status = element("p", { className: "page-label", tabIndex: -1 });
  const progress = element("progress", { max: count });
  progress.setAttribute("aria-label", "Question page progress");
  const indicator = element("div", { className: "question-progress", hidden: count === 1 }, status, progress);
  const back = element("button", { type: "button", className: "secondary", textContent: "Back" });
  const next = element("button", { type: "button", textContent: "Next" });
  let current = 0;

  function show(index, focus = false) {
    current = index;
    form.dataset.questionPage = index;
    panels.forEach((panel, position) => { panel.hidden = position !== current; });
    status.textContent = `Question page ${current + 1} of ${count}`;
    progress.value = current + 1;
    back.hidden = current === 0;
    next.hidden = current === count - 1;
    submit.hidden = !next.hidden;
    if (focus) status.focus();
  }

  back.addEventListener("click", () => show(current - 1, true));
  next.addEventListener("click", () => {
    const invalid = invalidControl(panels[current]);
    if (invalid) invalid.reportValidity();
    else show(current + 1, true);
  });
  show(Math.min(startAt, count - 1));

  function readyToSubmit() {
    if (current !== count - 1) return false;
    for (const [index, panel] of panels.entries()) {
      const invalid = invalidControl(panel);
      if (invalid) {
        show(index);
        invalid.reportValidity();
        return false;
      }
    }
    return true;
  }

  function questionContext() {
    return {
      question_page: current + 1,
      question_ids: pages[current].filter(field => field.type !== "section").map(field => field.id),
    };
  }

  return { indicator, panels, navigation: [back, next, submit], readyToSubmit, questionContext };
}
