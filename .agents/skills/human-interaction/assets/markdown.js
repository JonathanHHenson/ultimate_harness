import { renderMermaid } from "./mermaid.js";

const token = /(?<image>!)?\[(?<label>[^\]\n]+)\]\((?:<(?<angle>[^>\n]+)>|(?<url>[^\s()]+))\)|(?<code>\x60[^\x60\n]+\x60)|(?<bold>\*\*[^*\n]+\*\*)|(?<em>\*[^*\n]+\*)/g;

function safeLink(value) {
  if (value.startsWith("#")) return value;
  try {
    const parsed = new URL(value);
    if (["https:", "http:", "mailto:"].includes(parsed.protocol)) return parsed.href;
  } catch {
    // Leave invalid and relative link labels visible as text.
  }
  return null;
}

function linkOrImage(label, reference, image, images) {
  if (image) {
    if (!Object.hasOwn(images, reference)) return label;
    const img = document.createElement("img");
    img.alt = label;
    img.src = images[reference];
    return img;
  }
  const href = safeLink(reference);
  if (!href) return label;
  const anchor = document.createElement("a");
  anchor.href = href;
  anchor.textContent = label;
  if (!href.startsWith("#")) {
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
  }
  return anchor;
}

function formattedText({ code, bold, em }) {
  const item = document.createElement(code ? "code" : bold ? "strong" : "em");
  item.textContent = code?.slice(1, -1) ?? bold?.slice(2, -2) ?? em.slice(1, -1);
  return item;
}

function inline(target, source, images) {
  let offset = 0;
  for (const match of source.matchAll(token)) {
    target.append(source.slice(offset, match.index));
    const { image, label, angle, url } = match.groups;
    target.append(label ? linkOrImage(label, angle ?? url, image, images) : formattedText(match.groups));
    offset = match.index + match[0].length;
  }
  target.append(source.slice(offset));
}

const fence = /^\s*(\x60{3,}|~{3,})([\w-]*)\s*$/;
const heading = /^(#{1,6})\s+(.*)$/;
const listItem = /^\s*([-+*]|\d+\.)\s+(.*)$/;
const rule = /^(?:-{3,}|\*{3,}|_{3,})$/;
const quote = /^>\s?/;

function isBlock(line) {
  return !line.trim() || fence.test(line) || heading.test(line) || listItem.test(line)
    || rule.test(line.trim()) || quote.test(line);
}

function codeBlock(source, language) {
  if (language === "mermaid") {
    const diagram = renderMermaid(source);
    if (diagram) return diagram;
  }
  const block = document.createElement("pre");
  const code = document.createElement("code");
  code.textContent = source;
  if (language === "mermaid") block.setAttribute("aria-label", "Mermaid diagram source");
  block.append(code);
  return block;
}

function fencedBlock(lines, index, opening) {
  const code = [];
  const end = new RegExp("^\\s*" + opening[1][0] + "{" + opening[1].length + ",}\\s*$");
  while (index < lines.length && !end.test(lines[index])) code.push(lines[index++]);
  if (index < lines.length) index += 1;
  return { node: codeBlock(code.join("\n"), opening[2]), next: index };
}

function headingNode(match, images) {
  const node = document.createElement("h" + Math.min(match[1].length + 1, 6));
  node.id = match[2].toLowerCase().trim().replace(/[^\p{L}\p{N}\s-]/gu, "").replace(/\s+/g, "-");
  inline(node, match[2], images);
  return node;
}

function listBlock(lines, index, first, images) {
  const ordered = first[1].endsWith(".");
  const node = document.createElement(ordered ? "ol" : "ul");
  if (ordered) node.start = Number(first[1].slice(0, -1));
  let entry = first;
  while (entry) {
    const li = document.createElement("li");
    inline(li, entry[2], images);
    node.append(li);
    entry = lines[index]?.match(listItem);
    if (!entry || entry[1].endsWith(".") !== ordered) break;
    index += 1;
  }
  return { node, next: index };
}

function proseBlock(lines, index, line, images) {
  const quoted = quote.test(line);
  const node = document.createElement(quoted ? "blockquote" : "p");
  const content = [quoted ? line.replace(quote, "") : line];
  if (quoted) {
    while (index < lines.length && quote.test(lines[index])) content.push(lines[index++].replace(quote, ""));
  } else {
    while (index < lines.length && !isBlock(lines[index])) content.push(lines[index++]);
  }
  inline(node, content.join(" "), images);
  return { node, next: index };
}

function readBlock(lines, index, images) {
  const line = lines[index++];
  const start = line.match(fence);
  if (start) return fencedBlock(lines, index, start);
  const head = line.match(heading);
  if (head) return { node: headingNode(head, images), next: index };
  const item = line.match(listItem);
  if (item) return listBlock(lines, index, item, images);
  if (rule.test(line.trim())) return { node: document.createElement("hr"), next: index };
  return proseBlock(lines, index, line, images);
}

export function renderMarkdown(target, source, images) {
  const lines = source.split(/\r?\n/);
  let index = 0;
  while (index < lines.length) {
    if (!lines[index].trim()) {
      index += 1;
      continue;
    }
    const { node, next } = readBlock(lines, index, images);
    target.append(node);
    index = next;
  }
}
