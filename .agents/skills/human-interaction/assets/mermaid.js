// A dependency-free renderer for the documented Mermaid flowchart and sequence subset.
const SVG = "http://www.w3.org/2000/svg";
let serial = 0;

function svg(tag, attributes, text) {
  const node = document.createElementNS(SVG, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  if (text !== undefined) node.textContent = text;
  return node;
}

function diagram(width, height, label) {
  const container = document.createElement("figure");
  container.className = "diagram" + (width > 460 ? " wide-diagram" : "");
  if (width > 460) container.tabIndex = 0;
  const drawing = svg("svg", { viewBox: "0 0 " + width + " " + height, role: "img", "aria-label": label });
  const arrow = "diagram-arrow-" + (++serial);
  const marker = svg("marker", { id: arrow, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto" });
  marker.append(svg("path", { d: "M 0 0 L 10 5 L 0 10 z", class: "arrow" }));
  const defs = svg("defs", {});
  defs.append(marker);
  drawing.append(defs);
  container.append(drawing);
  return { container, drawing, arrow: "url(#" + arrow + ")" };
}

function edge(drawing, shape, arrow, dashed = false) {
  const attributes = { d: shape, class: "edge" };
  if (arrow) attributes["marker-end"] = arrow;
  if (dashed) attributes["stroke-dasharray"] = "4 3";
  drawing.append(svg("path", attributes));
}

function shorten(value, limit = 23) {
  return value.length <= limit ? value : value.slice(0, limit - 1) + "…";
}

function box(drawing, x, y, node) {
  const width = 148;
  const height = 44;
  const shape = node.shape === "{"
    ? svg("polygon", { points: [x, y - 30, x + width / 2, y, x, y + 30, x - width / 2, y].join(" "), class: "node" })
    : svg("rect", { x: x - width / 2, y: y - height / 2, width, height, rx: node.shape === "(" ? 22 : 7, class: "node" });
  shape.append(svg("title", {}, node.label));
  drawing.append(shape, svg("text", { x, y: y + 5 }, shorten(node.label, node.shape === "{" ? 17 : 21)));
}

function readNode(piece, nodes) {
  const match = piece.trim().match(/^([A-Za-z_][\w-]*)(?:\[([^\]]+)\]|\(([^)]+)\)|\{([^}]+)\})?$/);
  if (!match) throw new Error("Unsupported node");
  const [, id, square, rounded, diamond] = match;
  const declared = [[square, "["], [rounded, "("], [diamond, "{"]].find(([label]) => label !== undefined);
  if (declared || !nodes.has(id)) {
    const [label, shape] = declared ?? [id, "["];
    nodes.set(id, { label: label.replace(/^"|"$/g, ""), shape });
  }
  return id;
}

function flowLayout(nodes, edges) {
  const levels = new Map();
  const remaining = new Set(nodes.keys());
  while (remaining.size) {
    let ready = [...remaining].filter(id => edges.every(edge => edge.to !== id || levels.has(edge.from)));
    // Break cycles visually while retaining the returning arrow.
    if (!ready.length) ready = [[...remaining][0]];
    const level = Math.max(0, ...ready.flatMap(id => edges.filter(edge => edge.to === id && levels.has(edge.from))
      .map(edge => levels.get(edge.from) + 1)));
    for (const id of ready) {
      levels.set(id, level);
      remaining.delete(id);
    }
  }
  const layers = [];
  for (const [id, level] of levels) (layers[level] ??= []).push(id);
  return layers;
}

function parseFlowchart(lines) {
  const nodes = new Map();
  const edges = [];
  for (const line of lines.flatMap(line => line.split(";"))) {
    if (!line.trim()) continue;
    const parts = line.split(/(-->|---|==>|-\.\->)(?:\|([^|\n]+)\|)?/);
    let from = readNode(parts[0], nodes);
    for (let index = 1; index < parts.length; index += 3) {
      const to = readNode(parts[index + 2], nodes);
      edges.push({ from, to, kind: parts[index], label: parts[index + 1] });
      from = to;
    }
  }
  return { nodes, edges };
}

function flowPositions(layers, direction) {
  const horizontal = ["LR", "RL"].includes(direction);
  if (direction === "RL" || direction === "BT") layers.reverse();
  const depth = layers.length;
  const breadth = Math.max(...layers.map(layer => layer.length));
  const width = (horizontal ? depth : breadth) * 188 + 20;
  const height = (horizontal ? breadth : depth) * 102 + 20;
  const points = new Map();
  layers.forEach((layer, i) => layer.forEach((id, j) => {
    const spread = j - (layer.length - 1) / 2;
    points.set(id, horizontal ? [104 + i * 188, height / 2 + spread * 102]
      : [width / 2 + spread * 188, 61 + i * 102]);
  }));
  return { points, width, height, horizontal };
}

function drawFlowEdge(drawing, link, points, horizontal, arrow) {
  const [x, y] = points.get(link.from);
  const [tx, ty] = points.get(link.to);
  const sign = Math.sign(horizontal ? tx - x : ty - y) || 1;
  const tail = link.kind === "---" ? null : arrow;
  if (link.from === link.to) {
    edge(drawing, "M " + (x + 48) + " " + (y - 20) + " q 65 -40 24 16", tail);
  } else {
    const dx = horizontal ? 74 * sign : 0;
    const dy = horizontal ? 0 : 30 * sign;
    edge(drawing, "M " + (x + dx) + " " + (y + dy) + " L " + (tx - dx) + " " + (ty - dy), tail, link.kind.startsWith("-."));
  }
  if (link.label) drawing.append(svg("text", { x: (x + tx) / 2, y: (y + ty) / 2 - 7, class: "edge-label" }, shorten(link.label, 28)));
}

function flowchart(lines, direction) {
  const { nodes, edges } = parseFlowchart(lines);
  if (!nodes.size || nodes.size > 30 || edges.length > 50) return null;
  const { points, width, height, horizontal } = flowPositions(flowLayout(nodes, edges), direction);
  const { container, drawing, arrow } = diagram(width, height, "Flowchart: " + [...nodes.values()].map(node => node.label).join(", "));
  for (const link of edges) drawFlowEdge(drawing, link, points, horizontal, arrow);
  for (const [id, [x, y]] of points) box(drawing, x, y, nodes.get(id));
  return container;
}

function parseSequence(lines) {
  const people = new Map();
  const messages = [];
  for (const line of lines) {
    const person = line.match(/^(?:participant|actor)\s+(\w+)(?:\s+as\s+(.+))?$/);
    if (person) {
      people.set(person[1], person[2] ?? person[1]);
      continue;
    }
    const message = line.match(/^(\w+)\s*(--?>>?)\s*(\w+)\s*:\s*(.+)$/);
    if (!message) return null;
    const [, from, kind, to, label] = message;
    if (!people.has(from)) people.set(from, from);
    if (!people.has(to)) people.set(to, to);
    messages.push({ from, kind, to, label });
  }
  return { people, messages };
}

function sequence(lines) {
  const parsed = parseSequence(lines);
  if (!parsed) return null;
  const { people, messages } = parsed;
  if (!people.size || people.size > 12 || messages.length > 30) return null;
  const width = people.size * 174 + 72;
  const height = 105 + messages.length * 52;
  const { container, drawing, arrow } = diagram(width, height, "Sequence diagram: " + messages.map(m => m.label).join(", "));
  const positions = new Map();
  for (const [id, label] of people) {
    const x = 100 + positions.size * 174;
    positions.set(id, x);
    edge(drawing, "M " + x + " 53 V " + (height - 15), null, true);
    box(drawing, x, 32, { label, shape: "[" });
  }
  messages.forEach((message, index) => {
    const from = positions.get(message.from);
    const to = positions.get(message.to);
    const y = 87 + 52 * index;
    const path = from === to ? "M " + from + " " + y + " h 40 v 15 H " + from
      : "M " + from + " " + y + " H " + to;
    edge(drawing, path, arrow, message.kind.startsWith("--"));
    drawing.append(svg("text", { x: (from + to) / 2, y: y - 7, class: "edge-label" }, shorten(message.label, 30)));
  });
  return container;
}

export function renderMermaid(source) {
  const lines = source.split("\n").map(line => line.trim()).filter(line => line && !line.startsWith("%%"));
  const header = lines.shift();
  if (!header || lines.length > 60) return null;
  try {
    if (header === "sequenceDiagram") return sequence(lines);
    const match = header.match(/^(?:flowchart|graph)(?:\s+(TD|TB|BT|LR|RL))?$/);
    return match ? flowchart(lines, match[1] ?? "TD") : null;
  } catch {
    return null;
  }
}
