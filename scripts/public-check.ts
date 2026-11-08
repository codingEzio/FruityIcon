// Inspect an explicit local review payload. This is not permission to publish.
type Policy = {
  files: string[];
  releaseBlockers: string[];
  sources?: Record<string, string>;
  packageKind?: string;
};
if (
  Deno.args.some((arg) =>
    !["--export", "--release", "--curated", "--tool-only"].includes(arg)
  )
) {
  throw Error("Unknown option");
}
const curated = Deno.args.includes("--curated");
const toolOnly = Deno.args.includes("--tool-only");
if (curated && toolOnly) throw Error("Choose one package kind");
const policyName = toolOnly
  ? "tool-files.json"
  : curated
  ? "curated-files.json"
  : "public-files.json";
const policy: Policy = JSON.parse(await Deno.readTextFile(policyName));
const outputRoot = toolOnly
  ? "Local/tool-candidates"
  : curated
  ? "Local/curated-candidates"
  : "Local/public-candidates";
const hash = async (bytes: Uint8Array) =>
  Array.from(
    new Uint8Array(
      await crypto.subtle.digest("SHA-256", new Uint8Array(bytes).buffer),
    ),
  )
    .map((n) => n.toString(16).padStart(2, "0")).join("");
const files = [...policy.files].sort();
if (!files.length || new Set(files).size !== files.length) {
  throw Error("Invalid file list");
}
const records: {
  path: string;
  sha256: string;
  bytes: number;
  executable: boolean;
  sourcePath: string;
}[] = [];
const source = new Map<string, Uint8Array>();
for (const path of files) {
  if (
    path.startsWith("/") || path.includes("\\") ||
    path.split("/").some((p) =>
      !p || p === "." || p === ".." || p === ".git" || p === "Local" ||
      p === ".local" ||
      p.startsWith(".env")
    )
  ) throw Error(`Unsafe payload path: ${path}`);
  const sourcePath = policy.sources?.[path] ?? (curated
    ? ({
      "README.md": "CURATED.md",
      "README.zh-Hant.md": "CURATED.zh-Hant.md",
      "README.zh-Hans.md": "CURATED.zh-Hans.md",
    } as Record<string, string>)[path]
    : undefined) ??
    path;
  if (
    sourcePath.startsWith("/") || sourcePath.includes("\\") ||
    sourcePath.split("/").some((p) =>
      !p || p === "." || p === ".." || p === ".git" || p === ".local" ||
      p.startsWith(".env") || p === "Local"
    )
  ) throw Error(`Unsafe source path: ${sourcePath}`);
  const parts = sourcePath.split("/");
  for (let i = 1; i <= parts.length; i++) {
    if ((await Deno.lstat(parts.slice(0, i).join("/"))).isSymlink) {
      throw Error(`Symlink in payload: ${path}`);
    }
  }
  const stat = await Deno.stat(sourcePath);
  if (!stat.isFile) throw Error(`Not a regular file: ${path}`);
  const bytes = await Deno.readFile(sourcePath);
  // Binary assets are verified by their normal owner checks and hashed here.
  if (!/\.(png|icns|woff2|ttf)$/i.test(path)) {
    const text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    if (/\/(?:Users|home)\/[^\s/]+|[A-Z]:\\Users\\[^\s\\]+/.test(text)) {
      throw Error(`Personal absolute home path: ${path}`);
    }
    if (
      /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b/
        .test(text)
    ) {
      throw Error(`Credential-shaped text: ${path}`);
    }
  }
  source.set(path, bytes);
  records.push({
    path,
    sourcePath,
    sha256: await hash(bytes),
    bytes: bytes.length,
    executable: !!((stat.mode ?? 0) & 0o111),
  });
}
if (toolOnly) {
  if (
    policy.packageKind !== "tool-only" ||
    records.some((r) =>
      r.path.startsWith("experiments/") ||
      r.sourcePath.startsWith("experiments/") ||
      /preview\.(png|html)$/.test(r.path)
    )
  ) throw Error("Tool package must exclude private artwork and image previews");
  const scope = JSON.parse(
    new TextDecoder().decode(source.get("LICENSE-SCOPE.json")),
  );
  if (scope.packageKind !== "tool-only" || scope.artwork?.included !== false) {
    throw Error("Tool package scope must exclude original artwork");
  }
  const examples = JSON.parse(
    new TextDecoder().decode(source.get("examples/provenance.json")),
  );
  const images = records.filter((r) => /\.png$/i.test(r.path));
  if (
    images.length !== examples.assets.length ||
    images.some((r) =>
      !examples.assets.some((a: { file: string; sha256: string }) =>
        a.file === r.path && a.sha256 === r.sha256
      )
    )
  ) throw Error("Tool example hashes must match provenance exactly");
}
if (curated) {
  const scope = JSON.parse(
    new TextDecoder().decode(source.get("LICENSE-SCOPE.json")),
  );
  const selected = scope.artwork.assets.filter((a: { selection: string }) =>
    a.selection === "first-round-candidate"
  );
  const images = records.filter((r) => /\.png$/i.test(r.path));
  if (
    images.length !== selected.length ||
    images.some((r) =>
      !selected.some((a: { file: string; sha256: string }) =>
        a.file === r.path && a.sha256 === r.sha256
      )
    )
  ) {
    throw Error(
      "Curated PNG inventory must match selected scope hashes exactly",
    );
  }
}
const seal = await hash(new TextEncoder().encode(JSON.stringify(records)));
const receipt = {
  schemaVersion: 1,
  scope: toolOnly
    ? "tool-only-local-candidate; no-original-artwork"
    : curated
    ? "curated-local-candidate; rights-not-cleared"
    : "local-review-only",
  seal,
  files: records,
  releaseBlockers: policy.releaseBlockers,
  limitations: [
    "Working files only; Git index/history and remote state require separate review.",
    "Pattern checks are not a complete secret or rights audit.",
  ],
};
if (Deno.args.includes("--release") && policy.releaseBlockers.length) {
  console.error("Release blocked: " + policy.releaseBlockers.join("; "));
  Deno.exit(1);
}
if (Deno.args.includes("--export")) {
  for (const directory of ["Local", outputRoot]) {
    try {
      const stat = await Deno.lstat(directory);
      if (!stat.isDirectory || stat.isSymlink) {
        throw Error(`Unsafe output directory: ${directory}`);
      }
    } catch (error) {
      if (!(error instanceof Deno.errors.NotFound)) throw error;
    }
  }
  const output = `${outputRoot}/${seal}`;
  const receiptText = JSON.stringify(receipt, null, 2) + "\n";
  let exists = false;
  try {
    const stat = await Deno.lstat(output);
    if (stat.isSymlink || !stat.isDirectory) {
      throw Error("Unsafe candidate directory");
    }
    exists = true;
  } catch (error) {
    if (!(error instanceof Deno.errors.NotFound)) throw error;
  }
  if (!exists) {
    await Deno.mkdir(output, { recursive: true });
    for (const record of records) {
      const target = `${output}/${record.path}`;
      await Deno.mkdir(target.slice(0, target.lastIndexOf("/")), {
        recursive: true,
      });
      const mode = record.executable ? 0o755 : 0o644;
      await Deno.writeFile(target, source.get(record.path)!, {
        mode,
        createNew: true,
      });
      // Only the newly created payload file is adjusted to its promised mode.
      await Deno.chmod(target, mode);
    }
    await Deno.writeTextFile(`${output}/candidate-receipt.json`, receiptText, {
      createNew: true,
    });
  }
  const actual: string[] = [];
  const directories: string[] = [];
  const walk = async (base = "") => {
    for await (const entry of Deno.readDir(`${output}/${base}`)) {
      const path = base ? `${base}/${entry.name}` : entry.name;
      if (entry.isSymlink) throw Error(`Candidate symlink: ${path}`);
      if (entry.isDirectory) {
        directories.push(path);
        await walk(path);
      } else if (entry.isFile) actual.push(path);
      else throw Error(`Unexpected candidate entry: ${path}`);
    }
  };
  await walk();
  const expectedDirectories = new Set<string>();
  for (const path of files) {
    const parts = path.split("/");
    for (let i = 1; i < parts.length; i++) {
      expectedDirectories.add(parts.slice(0, i).join("/"));
    }
  }
  if (
    JSON.stringify(actual.sort()) !==
      JSON.stringify([...files, "candidate-receipt.json"].sort()) ||
    JSON.stringify(directories.sort()) !==
      JSON.stringify([...expectedDirectories].sort())
  ) {
    throw Error(
      "Candidate contains missing or unexpected entries; no files overwritten",
    );
  }
  for (const record of records) {
    const target = `${output}/${record.path}`;
    const stat = await Deno.stat(target);
    if (
      await hash(await Deno.readFile(target)) !== record.sha256 ||
      (stat.mode !== null &&
        (stat.mode & 0o777) !== (record.executable ? 0o755 : 0o644))
    ) {
      throw Error(
        `Candidate bytes/mode mismatch: ${record.path}; no files overwritten`,
      );
    }
  }
  const receiptMode =
    (await Deno.stat(`${output}/candidate-receipt.json`)).mode;
  if (
    await Deno.readTextFile(`${output}/candidate-receipt.json`) !==
      receiptText ||
    (receiptMode !== null &&
      ((receiptMode & 0o400) === 0 || (receiptMode & 0o133) !== 0))
  ) {
    throw Error("Candidate receipt mismatch; no files overwritten");
  }
  console.log(`Candidate: ${output}`);
}
console.log(JSON.stringify(receipt, null, 2));
