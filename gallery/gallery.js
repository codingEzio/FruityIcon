(() => {
  const words = {
    en: {
      linkMissing: "This gallery link does not match an item.",
      refresh: "Refresh",
      toolbarTitle: "Try the controls",
      roleSearch: "Search",
      roleAdd: "Add",
      roleFavorite: "Favorite",
      roleUpload: "Upload",
      roleDownload: "Download",
      roleSettings: "Toggle optical fit",
      importOld: "Import previous preferences",
      artwork: "Artwork",
      vector: "SVG comparison",
      importPrefs: "Import preferences JSON",
      exportPrefs: "Export preferences",
      remove: "Remove image",
      reset: "Reset sample",
      prefsSaved: "Preferences imported.",
      prefsInvalid: "Invalid preferences file.",
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
      linkMissing: "此圖庫連結找不到對應項目。",
      refresh: "重新整理",
      toolbarTitle: "試用操作",
      roleSearch: "搜尋",
      roleAdd: "加入",
      roleFavorite: "收藏",
      roleUpload: "上傳",
      roleDownload: "下載",
      roleSettings: "切換光學對齊",
      importOld: "匯入先前偏好",
      artwork: "圖稿",
      vector: "SVG 比較",
      importPrefs: "匯入偏好 JSON",
      exportPrefs: "匯出偏好",
      remove: "移除圖片",
      reset: "重設範例",
      prefsSaved: "已匯入偏好。",
      prefsInvalid: "偏好檔無效。",
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
      linkMissing: "此图集链接找不到对应项目。",
      refresh: "刷新",
      toolbarTitle: "试用操作",
      roleSearch: "搜索",
      roleAdd: "加入",
      roleFavorite: "收藏",
      roleUpload: "上传",
      roleDownload: "下载",
      roleSettings: "切换光学对齐",
      importOld: "导入先前偏好",
      artwork: "图稿",
      vector: "SVG 比较",
      importPrefs: "导入偏好 JSON",
      exportPrefs: "导出偏好",
      remove: "移除图片",
      reset: "重置示例",
      prefsSaved: "已导入偏好。",
      prefsInvalid: "偏好文件无效。",
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
  let data = null, selected = null, failure = "empty", linkMissing = false;
  const favorites = new Set(), tray = new Set();
  let localImage = null, uploadVersion = 0;
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
      return true;
    } catch {
      $("#notice").textContent = t("failed");
      return false;
    }
  }
  function icon(item, size = 48) {
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    const fitted = $("#fit").checked;
    const [x, y, w, h] = fitted ? [0, 0, 1, 1] : item.cell;
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
    img.setAttribute("preserveAspectRatio", "none");
    let target = svg;
    if (fitted) {
      const [sw, sh, sx, sy, top, right, bottom, left] = item.optical;
      const clipped = document.createElementNS(ns, "svg");
      for (
        const [k, v] of Object.entries({
          x: left,
          y: top,
          width: 1 - left - right,
          height: 1 - top - bottom,
          viewBox: `${left} ${top} ${1 - left - right} ${1 - top - bottom}`,
        })
      ) clipped.setAttribute(k, String(v));
      img.setAttribute("x", sx);
      img.setAttribute("y", sy);
      img.setAttribute("width", sw);
      img.setAttribute("height", sh);
      svg.append(clipped);
      target = clipped;
    } else {
      img.setAttribute("width", item.dimensions[actualTheme()][0]);
      img.setAttribute("height", item.dimensions[actualTheme()][1]);
    }
    img.addEventListener("error", () => {
      $("#notice").textContent = t("failed");
    });
    target.append(img);
    return svg;
  }
  function symbol(item, size = 24) {
    if (!item.symbol) return null;
    const ns = "http://www.w3.org/2000/svg",
      svg = document.createElementNS(ns, "svg"),
      use = document.createElementNS(ns, "use");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("class", "comparison-icon");
    svg.style.width = `${size}px`;
    svg.style.height = `${size}px`;
    use.setAttribute("href", `#comparison-${item.symbol}`);
    svg.append(use);
    return svg;
  }
  function renderToolbars() {
    const roles = [
      "search",
      "add",
      "favorite",
      "upload",
      "download",
      "settings",
    ];
    const mapping = data.toolbar;
    $("#toolbars").hidden = !Object.keys(mapping).length;
    for (const family of ["vector", "artwork"]) {
      const bar = $(`#toolbar-${family}`);
      bar.replaceChildren();
      for (const role of roles) {
        if (!mapping[role]) continue;
        const item = data.items.find((i) => i.id === mapping[role]);
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.action = role;
        button.dataset.family = family;
        button.setAttribute(
          "aria-label",
          t(`role${role[0].toUpperCase()}${role.slice(1)}`),
        );
        if (role === "add") {
          button.disabled = !selected || tray.has(selected.id);
        }
        if (role === "favorite") {
          button.disabled = !selected;
          button.setAttribute(
            "aria-pressed",
            String(!!selected && favorites.has(selected.id)),
          );
        }
        if (role === "settings") {
          button.setAttribute("aria-pressed", String(prefs.fit));
        }
        const graphic = family === "artwork"
          ? icon(item, 24)
          : symbol(item, 24);
        if (graphic) button.append(graphic);
        const label = document.createElement("span");
        label.textContent = t(`role${role[0].toUpperCase()}${role.slice(1)}`);
        button.append(label);
        bar.append(button);
      }
    }
  }
  function selectFromHash() {
    if (!data || !location.hash) return;
    let id;
    try {
      if (!location.hash.startsWith("#icon-")) throw Error();
      id = decodeURIComponent(location.hash.slice(6));
      if (!/^[a-z0-9][a-z0-9_-]{0,63}$/.test(id)) throw Error();
    } catch {
      linkMissing = true;
      return;
    }
    const item = data.items.find((i) =>
      i.id === id || (i.aliases || []).includes(id)
    );
    if (!item) {
      linkMissing = true;
      return;
    }
    linkMissing = false;
    selected = item;
    $("#search").value = "";
    $("#category").value = "";
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
    $("#notice").textContent = data
      ? (linkMissing ? t("linkMissing") : "")
      : t(failure);
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
        linkMissing = false;
        history.replaceState(null, "", `#icon-${encodeURIComponent(item.id)}`);
        render();
      };
      const card = document.createElement("div");
      card.className = "item-card";
      card.append(b);
      const star = document.createElement("button");
      star.type = "button";
      star.className = "item-star";
      star.setAttribute(
        "aria-label",
        `${t(favorites.has(item.id) ? "unfavorite" : "favorite")}: ${
          item.labels[prefs.language]
        }`,
      );
      star.setAttribute("aria-pressed", String(favorites.has(item.id)));
      star.textContent = favorites.has(item.id) ? "★" : "☆";
      star.onclick = () => {
        if (favorites.has(item.id)) favorites.delete(item.id);
        else favorites.add(item.id);
        render();
      };
      card.append(star);
      list.append(card);
    }
    renderToolbars();
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
    $("#vector-comparison").hidden = !selected.symbol;
    $("#vector-preview").replaceChildren();
    if (selected.symbol) {
      const ns = "http://www.w3.org/2000/svg";
      const svg = document.createElementNS(ns, "svg"),
        use = document.createElementNS(ns, "use");
      svg.setAttribute("viewBox", "0 0 24 24");
      svg.setAttribute("class", "comparison-icon");
      use.setAttribute("href", `#comparison-${selected.symbol}`);
      svg.append(use);
      $("#vector-preview").append(svg);
    }
    $("#sizes").replaceChildren(
      ...[16, 24, 32, 48].map((n) => icon(selected, n)),
    );
    const url = `/overlay/assets/${selected.assets[actualTheme()]}.png`;
    $("#download").href = url;
    $("#download").download = selected.assets[actualTheme()] + ".png";
    if ($("#fit").checked) {
      const [sw, sh, sx, sy, top, right, bottom, left] = selected.optical;
      const mono = $("#mono").checked && selected.monochrome;
      const paint = mono
        ? `background-color: currentColor;\nmask-image: url("${url}");\nmask-size: ${sw}em ${sh}em;\nmask-position: ${sx}em ${sy}em;\nmask-repeat: no-repeat;`
        : `background-image: url("${url}");\nbackground-size: ${sw}em ${sh}em;\nbackground-position: ${sx}em ${sy}em;\nbackground-repeat: no-repeat;`;
      $("#recipe").textContent =
        `/* Apply to a 1em square element. */\nwidth: 1em; height: 1em;\n${paint}\nclip-path: inset(${
          top * 100
        }% ${right * 100}% ${bottom * 100}% ${left * 100}%);`;
    } else {
      const [x, y, w, h] = selected.cell;
      $("#recipe").textContent =
        `width: ${w}px; height: ${h}px;\nbackground-image: url("${url}");\nbackground-position: -${x}px -${y}px;\nbackground-repeat: no-repeat;`;
    }
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
  $("#toolbars").addEventListener("click", (e) => {
    const button = e.target.closest("button[data-action]");
    if (!button || button.disabled) return;
    const action = button.dataset.action;
    if (action === "search") {
      $("#search").focus();
      $("#search").scrollIntoView({ block: "nearest" });
    }
    if (action === "add") $("#add").click();
    if (action === "favorite") $("#favorite").click();
    if (action === "upload") $("#upload").click();
    if (action === "settings") {
      $("#fit").checked = !$("#fit").checked;
      $("#fit").dispatchEvent(new Event("change"));
    }
    if (action === "download") {
      const item = data.items.find((i) => i.id === data.toolbar.download);
      const a = document.createElement("a");
      a.href = `/overlay/assets/${item.assets[actualTheme()]}.png`;
      a.download = item.assets[actualTheme()] + ".png";
      a.click();
    }
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
    const version = ++uploadVersion;
    const header = new Uint8Array(await file.slice(0, 24).arrayBuffer());
    if (version !== uploadVersion) return;
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
    const url = URL.createObjectURL(file);
    const probe = new Image();
    probe.onload = () => {
      if (version !== uploadVersion) {
        URL.revokeObjectURL(url);
        return;
      }
      if (localImage) URL.revokeObjectURL(localImage);
      localImage = url;
      const preview = $("#local-preview");
      preview.src = url;
      preview.alt = file.name;
      preview.hidden = false;
    };
    probe.onerror = () => {
      URL.revokeObjectURL(url);
      if (version === uploadVersion) $("#notice").textContent = t("badImage");
    };
    probe.src = url;
  });
  function clearUpload() {
    uploadVersion++;
    if (localImage) URL.revokeObjectURL(localImage);
    localImage = null;
    $("#local-preview").removeAttribute("src");
    $("#local-preview").hidden = true;
    $("#upload").value = "";
  }
  $("#clear-upload").addEventListener("click", clearUpload);
  $("#reset-demo").addEventListener("click", () => {
    favorites.clear();
    tray.clear();
    $("#search").value = "";
    clearUpload();
    render();
  });
  $("#export-prefs").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(prefs, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fruity-preferences.json";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  function applyImported(input) {
    if (!input || typeof input !== "object" || Array.isArray(input)) {
      throw Error();
    }
    const next = { ...prefs };
    const allowed = {
      language: ["en", "zh-Hant", "zh-Hans"],
      theme: ["system", "light", "dark"],
      font: ["system", "pixel"],
    };
    let count = 0;
    for (const [key, choices] of Object.entries(allowed)) {
      if (key in input) {
        if (!choices.includes(input[key])) throw Error();
        next[key] = input[key];
        count++;
      }
    }
    for (const key of ["fit", "mono"]) {
      if (key in input) {
        if (typeof input[key] !== "boolean") throw Error();
        next[key] = input[key];
        count++;
      }
    }
    if ("ink" in input) {
      if (!["color", "mono"].includes(input.ink)) throw Error();
      next.mono = input.ink === "mono";
      count++;
    }
    if ("size" in input) {
      if (
        !Number.isInteger(input.size) || input.size < 16 || input.size > 48 ||
        input.size % 2
      ) throw Error();
      next.size = input.size;
      count++;
    }
    if (!count) throw Error();
    Object.assign(prefs, next);
    $("#size").value = prefs.size;
    $("#fit").checked = prefs.fit;
    $("#mono").checked = prefs.mono;
    const saved = save();
    render();
    $("#notice").textContent = t(saved ? "prefsSaved" : "failed");
  }
  try {
    $("#import-old").hidden =
      localStorage.getItem("fruity.demo.preferences.v1") === null;
  } catch { /* Storage is unavailable. */ }
  $("#import-old").addEventListener("click", () => {
    try {
      const raw = localStorage.getItem("fruity.demo.preferences.v1");
      if (!raw || raw.length > 32768) throw Error();
      applyImported(JSON.parse(raw));
    } catch {
      $("#notice").textContent = t("prefsInvalid");
    }
  });
  $("#prefs-file").addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      if (file.size > 32768) throw Error();
      applyImported(JSON.parse(await file.text()));
    } catch {
      $("#notice").textContent = t("prefsInvalid");
    } finally {
      e.target.value = "";
    }
  });
  $("#refresh").addEventListener("click", () => location.reload());
  addEventListener("hashchange", () => {
    selectFromHash();
    render();
  });
  $("#search").addEventListener("input", render);
  $("#category").addEventListener("change", render);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  $("#copy").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("#recipe").textContent);
      $("#notice").textContent = t("copied");
    } catch {
      const range = document.createRange();
      range.selectNodeContents($("#recipe"));
      const selection = getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      $("#notice").textContent = t("copyFail");
    }
  });
  render();
  fetch("/overlay/catalog.json").then(async (r) => {
    if (r.status === 404) return;
    if (!r.ok) throw Error();
    data = await r.json();
    selectFromHash();
    render();
  }).catch(() => {
    failure = "failed";
    render();
  });
})();
