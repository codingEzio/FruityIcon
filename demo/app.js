(() => {
  const labels = {
    en: {
      intro: "PNG bounds and CSS sprites. Six geometric examples.",
      title: "FruityIcon · Geometry tools",
      preferences: "Preferences",
      recipeNote:
        "Requires demo.css and generated icons.css; paths are relative to demo/.",
      language: "Language",
      theme: "Theme",
      system: "System",
      light: "Light",
      dark: "Dark",
      font: "Font",
      systemFont: "System",
      pixel: "Pixel",
      size: "Size",
      examples: "Examples",
      circle: "Circle",
      square: "Square",
      diamond: "Diamond",
      triangle: "Triangle",
      cross: "Cross",
      ring: "Ring",
      download: "Download the geometric sheet",
      scope:
        "Tool-only candidate. Original generated artwork and its derived previews are excluded. Geometry examples and source code use MIT. Fonts are not included.",
      guide: "Source guide",
      provenance: "Example provenance",
      storage: "Preferences could not be saved in this browser.",
    },
    "zh-Hant": {
      intro: "PNG 邊界量測與 CSS 精靈。六個幾何範例。",
      title: "FruityIcon · 幾何工具",
      preferences: "偏好設定",
      recipeNote: "需要 demo.css 與產生的 icons.css；路徑相對於 demo/。",
      language: "語言",
      theme: "主題",
      system: "跟隨系統",
      light: "淺色",
      dark: "深色",
      font: "字型",
      systemFont: "系統字型",
      pixel: "像素字型",
      size: "尺寸",
      examples: "範例",
      circle: "圓形",
      square: "方形",
      diamond: "菱形",
      triangle: "三角形",
      cross: "十字",
      ring: "圓環",
      download: "下載幾何範例圖",
      scope:
        "純工具候選。原生成圖像及其衍生預覽均未收錄。幾何範例與原始碼採 MIT；不含字型。",
      guide: "原始碼指南",
      provenance: "範例來源",
      storage: "此瀏覽器無法儲存偏好設定。",
    },
    "zh-Hans": {
      intro: "PNG 边界测量与 CSS 精灵。六个几何示例。",
      title: "FruityIcon · 几何工具",
      preferences: "偏好设置",
      recipeNote: "需要 demo.css 与生成的 icons.css；路径相对于 demo/。",
      language: "语言",
      theme: "主题",
      system: "跟随系统",
      light: "浅色",
      dark: "深色",
      font: "字体",
      systemFont: "系统字体",
      pixel: "像素字体",
      size: "尺寸",
      examples: "示例",
      circle: "圆形",
      square: "方形",
      diamond: "菱形",
      triangle: "三角形",
      cross: "十字",
      ring: "圆环",
      download: "下载几何示例图",
      scope:
        "纯工具候选。原生成图像及其衍生预览均未收录。几何示例与源代码采用 MIT；不含字体。",
      guide: "源代码指南",
      provenance: "示例来源",
      storage: "此浏览器无法保存偏好设置。",
    },
  };
  labels["ja"] = {
    "intro": "PNG の境界と CSS スプライト。6 つの幾何学サンプル。",
    "title": "FruityIcon · 幾何学ツール",
    "preferences": "設定",
    "recipeNote": "demo.css と生成された icons.css が必要です。",
    "language": "言語",
    "theme": "テーマ",
    "system": "システム",
    "light": "ライト",
    "dark": "ダーク",
    "font": "フォント",
    "systemFont": "システム",
    "pixel": "ピクセル",
    "size": "サイズ",
    "examples": "サンプル",
    "circle": "円",
    "square": "正方形",
    "diamond": "ひし形",
    "triangle": "三角形",
    "cross": "十字",
    "ring": "リング",
    "download": "サンプル画像をダウンロード",
    "scope": "ツールのみ。元のイラストとフォントは含みません。",
    "guide": "ソースガイド",
    "provenance": "サンプルの出典",
    "storage": "設定を保存できませんでした。",
    "fontMissing": "ピクセルフォントを選択してください。",
    "fontLoaded": "フォントを読み込みました。",
    "fontError": "フォントを読み込めません。",
    "fontFile": "フォントファイル",
  };
  labels["ko"] = {
    "intro": "PNG 경계와 CSS 스프라이트. 여섯 가지 도형 예제.",
    "title": "FruityIcon · 도형 도구",
    "preferences": "환경설정",
    "recipeNote": "demo.css와 생성된 icons.css가 필요합니다.",
    "language": "언어",
    "theme": "테마",
    "system": "시스템",
    "light": "라이트",
    "dark": "다크",
    "font": "글꼴",
    "systemFont": "시스템",
    "pixel": "픽셀",
    "size": "크기",
    "examples": "예제",
    "circle": "원",
    "square": "사각형",
    "diamond": "마름모",
    "triangle": "삼각형",
    "cross": "십자",
    "ring": "고리",
    "download": "도형 시트 다운로드",
    "scope": "도구 전용. 원본 일러스트와 글꼴은 포함되지 않습니다.",
    "guide": "소스 안내",
    "provenance": "예제 출처",
    "storage": "설정을 저장하지 못했습니다.",
    "fontMissing": "픽셀 글꼴을 선택하세요.",
    "fontLoaded": "글꼴을 불러왔습니다.",
    "fontError": "글꼴을 불러오지 못했습니다.",
    "fontFile": "글꼴 파일",
  };
  labels["es"] = {
    "intro": "Límites PNG y sprites CSS. Seis ejemplos geométricos.",
    "title": "FruityIcon · Herramientas geométricas",
    "preferences": "Preferencias",
    "recipeNote": "Requiere demo.css e icons.css generado.",
    "language": "Idioma",
    "theme": "Tema",
    "system": "Sistema",
    "light": "Claro",
    "dark": "Oscuro",
    "font": "Fuente",
    "systemFont": "Sistema",
    "pixel": "Píxel",
    "size": "Tamaño",
    "examples": "Ejemplos",
    "circle": "Círculo",
    "square": "Cuadrado",
    "diamond": "Rombo",
    "triangle": "Triángulo",
    "cross": "Cruz",
    "ring": "Anillo",
    "download": "Descargar hoja geométrica",
    "scope":
      "Solo herramientas. No se incluyen ilustraciones originales ni fuentes.",
    "guide": "Guía de código",
    "provenance": "Origen de ejemplos",
    "storage": "No se pudieron guardar las preferencias.",
    "fontMissing": "Seleccione una fuente píxel.",
    "fontLoaded": "Fuente cargada.",
    "fontError": "No se pudo cargar la fuente.",
    "fontFile": "Archivo de fuente",
  };
  Object.assign(labels.en, {
    fontMissing: "Choose a Pixel font file.",
    fontLoaded: "Font loaded.",
    fontError: "Could not load font.",
    fontFile: "Font file",
  });
  Object.assign(labels["zh-Hant"], {
    fontMissing: "請選擇像素字型檔案。",
    fontLoaded: "字型已載入。",
    fontError: "無法載入字型。",
    fontFile: "字型檔案",
  });
  Object.assign(labels["zh-Hans"], {
    fontMissing: "请选择像素字体文件。",
    fontLoaded: "字体已加载。",
    fontError: "无法加载字体。",
    fontFile: "字体文件",
  });
  let activeFace = null;
  let fontGeneration = 0;
  let fontLoaded = false;
  let fontError = false;
  const ids = ["circle", "square", "diamond", "triangle", "cross", "ring"];
  const $ = (id) => document.getElementById(id);
  const key = "fruity.tool.preferences.v1";
  const prefs = { language: "en", theme: "system", font: "system", size: 48 };
  let storageFailed = false;
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    if (saved && labels[saved.language]) prefs.language = saved.language;
    if (["light", "dark", "system"].includes(saved?.theme)) {
      prefs.theme = saved.theme;
    }
    if (["system", "pixel"].includes(saved?.font)) prefs.font = saved.font;
    if (Number.isInteger(saved?.size) && saved.size >= 16 && saved.size <= 96) {
      prefs.size = saved.size;
    }
  } catch {
    storageFailed = true;
  }
  let selected = ids.includes(location.hash.slice(1))
    ? location.hash.slice(1)
    : ids[0];
  const sample = (id) =>
    `<span class="fruity" data-action="${id}" aria-hidden="true"><span class="ink"></span></span>`;
  function render() {
    const t = labels[prefs.language];
    const root = document.documentElement;
    root.lang = prefs.language;
    document.title = t.title;
    $("controls").setAttribute("aria-label", t.preferences);
    root.dataset.theme = prefs.theme;
    root.dataset.font = prefs.font === "pixel" && fontLoaded
      ? "pixel"
      : "system";
    $("font-file").hidden = prefs.font !== "pixel";
    $("font-file").setAttribute("aria-label", t.fontFile);
    $("font-status").textContent = prefs.font !== "pixel"
      ? ""
      : fontError
      ? t.fontError
      : fontLoaded
      ? t.fontLoaded
      : t.fontMissing;
    root.style.setProperty("--size", `${prefs.size}px`);
    document.querySelectorAll("[data-text]").forEach((node) => {
      node.textContent = t[node.dataset.text];
    });
    $("storage").textContent = storageFailed ? t.storage : "";
    for (const name of ["language", "theme", "font", "size"]) {
      $(name).value = prefs[name];
    }
    $("size-value").textContent = `${
      new Intl.NumberFormat(prefs.language).format(prefs.size)
    } px`;
    $("samples").innerHTML = ids.map((id) =>
      `<button type="button" data-id="${id}" aria-pressed="${
        id === selected
      }">${sample(id)}<span>${t[id]}</span></button>`
    ).join("");
    $("selected").textContent = t[selected];
    $("scales").innerHTML = [16, 24, 32, 48].map((size) =>
      `<div class="scale" style="--size:${size}px">${
        sample(selected)
      }<code>${size} px</code></div>`
    ).join("");
    const style = getComputedStyle($("scales").querySelector(".fruity"));
    const metric = (v) =>
      `calc(${style.getPropertyValue(`--sprite-${v}`).trim()} * 1em)`;
    const dark = prefs.theme === "dark" ||
      (prefs.theme === "system" &&
        matchMedia("(prefers-color-scheme: dark)").matches);
    const file = `actions-${dark ? "dark" : "light"}.png`;
    $("download").href = `../examples/${file}`;
    $("recipe").textContent =
      `.fruity[data-action="${selected}"] .ink {\n  background-image: url("../examples/${file}");\n  background-size: ${
        metric("w")
      } ${metric("h")};\n  background-position: ${metric("x")} ${
        metric("y")
      };\n  background-repeat: no-repeat;\n}\n/* ${t.recipeNote} */`;
  }
  $("samples").addEventListener("click", (event) => {
    const button = event.target.closest("[data-id]");
    if (!button) return;
    selected = button.dataset.id;
    history.replaceState(null, "", `#${selected}`);
    render();
    $("samples").querySelector(`[data-id="${selected}"]`).focus();
  });
  for (const name of ["language", "theme", "font", "size"]) {
    $(name).addEventListener(name === "size" ? "input" : "change", (event) => {
      prefs[name] = name === "size"
        ? Number(event.target.value)
        : event.target.value;
      try {
        localStorage.setItem(key, JSON.stringify(prefs));
        storageFailed = false;
      } catch {
        storageFailed = true;
      }
      render();
    });
  }
  $("font-file").addEventListener("change", async (event) => {
    const generation = ++fontGeneration;
    if (activeFace) document.fonts.delete(activeFace);
    activeFace = null;
    fontLoaded = false;
    fontError = false;
    render();
    const file = event.target.files[0];
    if (!file) return;
    try {
      const face = new FontFace("Fruity Pixel", await file.arrayBuffer());
      await face.load();
      if (generation !== fontGeneration) return;
      document.fonts.add(face);
      activeFace = face;
      fontLoaded = true;
    } catch {
      if (generation === fontGeneration) fontError = true;
    }
    render();
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", render);
  render();
})();
