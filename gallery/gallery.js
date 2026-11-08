(() => {
  const words = {
    en: {
      size: "Size",
      fit: "Optical fit",
      mono: "Monochrome",
      favorite: "Favorite",
      unfavorite: "Unfavorite",
      add: "Add to tray",
      tray: "Tray",
      upload: "Preview local PNG",
      badImage: "Choose a PNG up to 8 MiB and 4 megapixels.",
      tool: "Geometry tool",
      language: "Language",
      theme: "Theme",
      font: "Font",
      system: "System",
      light: "Light",
      dark: "Dark",
      pixel: "Pixel",
      search: "Search",
      category: "Category",
      all: "All",
      download: "Download source",
      copy: "Copy CSS",
      empty:
        "No local gallery is configured. Start the server with an overlay to view your collection.",
      failed: "The local gallery could not be loaded.",
      none: "No matching items.",
      count: "{count} of {total} items",
      fontMissing: "Pixel font is unavailable; using system font.",
      copied: "CSS copied.",
      copyFail: "Select the CSS text to copy it.",
    },
    "zh-Hant": {
      size: "尺寸",
      fit: "光學對齊",
      mono: "單色",
      favorite: "收藏",
      unfavorite: "取消收藏",
      add: "加入托盤",
      tray: "托盤",
      upload: "預覽本機 PNG",
      badImage: "請選擇不超過 8 MiB、400 萬像素的 PNG。",
      tool: "幾何工具",
      language: "語言",
      theme: "主題",
      font: "字型",
      system: "系統",
      light: "淺色",
      dark: "深色",
      pixel: "像素",
      search: "搜尋",
      category: "分類",
      all: "全部",
      download: "下載原圖",
      copy: "複製 CSS",
      empty: "尚未設定本機圖庫。啟動伺服器時加入資料目錄即可檢視。",
      failed: "無法載入本機圖庫。",
      none: "沒有符合的項目。",
      count: "{count}／{total} 個項目",
      fontMissing: "像素字型無法載入，使用系統字型。",
      copied: "CSS 已複製。",
      copyFail: "請選取 CSS 文字複製。",
    },
    "zh-Hans": {
      size: "尺寸",
      fit: "光学对齐",
      mono: "单色",
      favorite: "收藏",
      unfavorite: "取消收藏",
      add: "加入托盘",
      tray: "托盘",
      upload: "预览本机 PNG",
      badImage: "请选择不超过 8 MiB、400 万像素的 PNG。",
      tool: "几何工具",
      language: "语言",
      theme: "主题",
      font: "字体",
      system: "系统",
      light: "浅色",
      dark: "深色",
      pixel: "像素",
      search: "搜索",
      category: "分类",
      all: "全部",
      download: "下载原图",
      copy: "复制 CSS",
      empty: "尚未设置本地图集。启动服务器时加入数据目录即可查看。",
      failed: "无法加载本地图集。",
      none: "没有匹配的项目。",
      count: "{count}／{total} 个项目",
      fontMissing: "像素字体无法加载，使用系统字体。",
      copied: "CSS 已复制。",
      copyFail: "请选择 CSS 文字复制。",
    },
  };
  const $ = (s) => document.querySelector(s);
  const prefs = {
    language: "en",
    theme: "system",
    font: "system",
    fit: true,
    mono: false,
  };
  try {
    Object.assign(
      prefs,
      JSON.parse(localStorage.getItem("fruity.gallery.preferences.v1") || "{}"),
    );
  } catch {
    // Invalid or unavailable stored preferences use defaults.
  }
  for (
    const [key, allowed] of Object.entries({
      language: ["en", "zh-Hant", "zh-Hans"],
      theme: ["system", "light", "dark"],
      font: ["system", "pixel"],
    })
  ) {
    if (!allowed.includes(prefs[key])) {
      prefs[key] = key === "language" ? "en" : "system";
    }
  }
  if (
    !Number.isInteger(prefs.size) || prefs.size < 16 || prefs.size > 48 ||
    prefs.size % 2
  ) prefs.size = 24;
  $("#size").value = prefs.size;
  if (typeof prefs.fit !== "boolean") prefs.fit = true;
  if (typeof prefs.mono !== "boolean") prefs.mono = false;
  $("#fit").checked = prefs.fit;
  $("#mono").checked = prefs.mono;
  let data = null, selected = null, failure = "empty";
  const favorites = new Set(), tray = new Set();
  let localImage = null;
  const t = (key) => words[prefs.language][key];
  const actualTheme = () =>
    prefs.theme === "system"
      ? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
      : prefs.theme;
  function save() {
    try {
      localStorage.setItem(
        "fruity.gallery.preferences.v1",
        JSON.stringify(prefs),
      );
    } catch {
      $("#notice").textContent = t("failed");
    }
  }
  function icon(item, size = 48) {
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    const [x, y, w, h] = $("#fit").checked ? item.rect : item.cell;
    svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
    svg.setAttribute("class", "icon");
    if ($("#mono").checked && item.monochrome) svg.classList.add("mono");
    svg.style.width = `${size}px`;
    svg.style.height = `${size}px`;
    const img = document.createElementNS(ns, "image");
    img.setAttribute(
      "href",
      `/overlay/assets/${item.assets[actualTheme()]}.png`,
    );
    img.setAttribute("width", "4096");
    img.setAttribute("height", "4096");
    img.setAttribute("preserveAspectRatio", "none");
    // Image dimensions are supplied by the server, preserving sprite coordinates.
    img.setAttribute("width", item.dimensions[actualTheme()][0]);
    img.setAttribute("height", item.dimensions[actualTheme()][1]);
    img.addEventListener("error", () => {
      $("#notice").textContent = t("failed");
    });
    svg.append(img);
    return svg;
  }
  function localize() {
    document.documentElement.lang = prefs.language;
    for (const node of document.querySelectorAll("[data-i18n]")) {
      node.textContent = t(node.dataset.i18n);
    }
  }
  function render() {
    document.documentElement.dataset.theme = actualTheme();
    $("#size-value").textContent = `${prefs.size} px`;
    document.documentElement.dataset.font = prefs.font;
    localize();
    for (const key of ["language", "theme", "font"]) {
      $(`#${key}`).value = prefs[key];
    }
    $("#library").hidden = !data;
    $("#notice").textContent = data ? "" : t(failure);
    if (!data) return;
    const category = $("#category"), previous = category.value;
    category.replaceChildren(new Option(t("all"), ""));
    for (const [id, names] of Object.entries(data.categories)) {
      category.add(new Option(names[prefs.language], id));
    }
    category.value = previous;
    const q = $("#search").value.trim().toLocaleLowerCase();
    const visible = data.items.filter((i) =>
      (!category.value || i.category === category.value) &&
      Object.values(i.labels).some((v) => v.toLocaleLowerCase().includes(q))
    );
    $("#count").textContent = visible.length
      ? t("count").replace("{count}", visible.length).replace(
        "{total}",
        data.items.length,
      )
      : t("none");
    if (!visible.includes(selected)) selected = visible[0] || null;
    const list = $("#items");
    list.replaceChildren();
    for (const item of visible) {
      const b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-pressed", String(item === selected));
      b.append(icon(item, prefs.size));
      const span = document.createElement("span");
      span.textContent = item.labels[prefs.language];
      b.append(span);
      b.onclick = () => {
        selected = item;
        render();
      };
      list.append(b);
    }
    $("#detail").hidden = !selected;
    if (!selected) return;
    $("#name").textContent = selected.labels[prefs.language];
    $("#description").textContent = selected.description[prefs.language];
    $("#favorite").textContent = t(
      favorites.has(selected.id) ? "unfavorite" : "favorite",
    );
    $("#favorite").setAttribute(
      "aria-pressed",
      String(favorites.has(selected.id)),
    );
    const trayNode = $("#tray");
    trayNode.replaceChildren();
    for (const item of data.items.filter((i) => tray.has(i.id))) {
      const b = document.createElement("button");
      b.type = "button";
      b.append(icon(item, 24));
      const label = document.createElement("span");
      label.textContent = item.labels[prefs.language];
      b.append(label);
      b.onclick = () => {
        tray.delete(item.id);
        render();
      };
      trayNode.append(b);
    }
    $("#preview").replaceChildren(icon(selected, 96));
    $("#sizes").replaceChildren(
      ...[16, 24, 32, 48].map((n) => icon(selected, n)),
    );
    const url = `/overlay/assets/${selected.assets[actualTheme()]}.png`;
    $("#download").href = url;
    $("#download").download = selected.assets[actualTheme()] + ".png";
    const [x, y, w, h] = $("#fit").checked ? selected.rect : selected.cell;
    $("#recipe").textContent =
      `width: ${w}px; height: ${h}px;\nbackground-image: url("${url}");\nbackground-position: -${x}px -${y}px;\nbackground-repeat: no-repeat;`;
  }
  for (const key of ["language", "theme", "font"]) {
    $(`#${key}`).addEventListener("change", async (e) => {
      prefs[key] = e.target.value;
      save();
      render();
      if (key === "font" && prefs.font === "pixel") {
        try {
          await document.fonts.load("16px GalleryPixel");
        } catch {
          $("#notice").textContent = t("fontMissing");
        }
      }
    });
  }
  $("#size").addEventListener("input", (e) => {
    prefs.size = Number(e.target.value);
    save();
    render();
  });
  $("#fit").addEventListener("change", (e) => {
    prefs.fit = e.target.checked;
    save();
    render();
  });
  $("#mono").addEventListener("change", (e) => {
    prefs.mono = e.target.checked;
    save();
    render();
  });
  $("#favorite").addEventListener("click", () => {
    if (!selected) return;
    if (favorites.has(selected.id)) favorites.delete(selected.id);
    else favorites.add(selected.id);
    render();
  });
  $("#add").addEventListener("click", () => {
    if (selected) tray.add(selected.id);
    render();
  });
  $("#upload").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const header = new Uint8Array(await file.slice(0, 24).arrayBuffer());
    const valid = header.length === 24 &&
      [137, 80, 78, 71, 13, 10, 26, 10].every((v, i) => header[i] === v);
    const view = new DataView(header.buffer);
    const w = valid ? view.getUint32(16) : 0,
      h = valid ? view.getUint32(20) : 0;
    if (
      !valid || file.size > 8 * 1024 * 1024 || !w || !h || w > 4096 ||
      h > 4096 || w * h > 4000000
    ) {
      $("#notice").textContent = t("badImage");
      return;
    }
    if (localImage) URL.revokeObjectURL(localImage);
    localImage = URL.createObjectURL(file);
    const preview = $("#local-preview");
    preview.src = localImage;
    preview.alt = file.name;
    preview.hidden = false;
  });
  $("#search").addEventListener("input", render);
  $("#category").addEventListener("change", render);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  $("#copy").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("#recipe").textContent);
      $("#notice").textContent = t("copied");
    } catch {
      $("#notice").textContent = t("copyFail");
    }
  });
  render();
  fetch("/overlay/catalog.json").then(async (r) => {
    if (r.status === 404) return;
    if (!r.ok) throw Error();
    data = await r.json();
    render();
  }).catch(() => {
    failure = "failed";
    render();
  });
})();
