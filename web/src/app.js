/* Pop Agent Web v1.
   High-fidelity implementation target:
   D:\bit\2_2\pop-agent file\design_handoff_pop_agent */

const STATE_ORDER = ["empty", "filled", "running", "success", "failed"];
const STORAGE_KEY = "pop-agent-web-v1-state";
const API_BASE = window.POP_AGENT_API_BASE || "";

const STRINGS = {
  zh: {
    newRun: "新建生成",
    history: "历史记录",
    settings: "设置 / 安装",
    docs: "使用文档",
    workspace: "工作台",
    runs: "会话",
    breadcrumb: "工作台 / 新建生成",
    inputSection: "输入",
    inputHint: "上传或粘贴一段你希望被讲清楚的复杂材料。Prompt-only 模式当前作为原型入口。",
    sourceTab: "上传 / 粘贴文本",
    promptTab: "Prompt only",
    placeholderSource: "把一段需要被讲清楚的文章、论文摘要、PRD 或笔记粘贴到这里...",
    placeholderPrompt: "告诉 Pop Agent 你想被讲清楚的题目，例如：黑洞为什么不是洞？",
    parametersSection: "生成参数",
    outputSection: "输出模态",
    outputHint: "只有文本是 v1 已开放的真实生成路径；图片、视频先保留占位入口。",
    generate: "开始生成",
    backend: "后端",
    iterations: "最大迭代",
    chars: "字",
    audience: "目标读者",
    style: "写作风格",
    userId: "用户记忆 ID",
    stop: "停止",
    retry: "从此处重试",
    runningTitle: "正在生成中...",
    failedTitle: "生成失败",
    resultTitle: "生成结果",
    lang: "中文",
  },
  en: {
    newRun: "New run",
    history: "History",
    settings: "Settings",
    docs: "Docs",
    workspace: "Workspace",
    runs: "Runs",
    breadcrumb: "Workspace / New run",
    inputSection: "Input",
    inputHint: "Upload or paste a complex passage. Prompt-only is a preview entry while retrieval is still in progress.",
    sourceTab: "Upload / paste",
    promptTab: "Prompt only",
    placeholderSource: "Paste an article, abstract, PRD, or notes that you want explained clearly...",
    placeholderPrompt: "Tell Pop Agent the topic you want explained, e.g. why a black hole is not a hole.",
    parametersSection: "Parameters",
    outputSection: "Output modality",
    outputHint: "Only Text is the live v1 path. Image and Video keep an entry but no real backend is wired yet.",
    generate: "Generate",
    backend: "Backend",
    iterations: "Max iterations",
    chars: "chars",
    audience: "Audience",
    style: "Style",
    userId: "Memory user-id",
    stop: "Stop",
    retry: "Retry from here",
    runningTitle: "Generating...",
    failedTitle: "Generation failed",
    resultTitle: "Result",
    lang: "English",
  },
};

const RUNTIME = {
  backend: "deepseek",
  model: "deepseek-v4-pro",
  baseUrl: "https://api.deepseek.com",
  dataDir: "~/.local/share/pop-agent/data",
  maxIterations: 3,
  clarityThreshold: 8,
};

const RUNS = [
  {
    id: "run_20260515T142308Z_8f3a",
    title: "黑洞不是“洞”：从被压弯的时空说起",
    topic: "黑洞为什么不是洞",
    audience: "初中生",
    status: "running",
    when: "正在运行",
    backend: "deepseek",
    bucket: "今天",
  },
  {
    id: "run_20260515T091422Z_a1c0",
    title: "为什么夏天比冬天更容易出汗",
    topic: "出汗的物理与生理机制",
    audience: "高中生",
    status: "success",
    when: "4 小时前",
    backend: "deepseek",
    bucket: "今天",
  },
  {
    id: "run_20260514T231019Z_55e2",
    title: "把熵讲成“房间为什么会自己变乱”",
    topic: "热力学第二定律",
    audience: "初中生",
    status: "success",
    when: "昨天",
    backend: "openai",
    bucket: "昨天",
  },
  {
    id: "run_20260514T184435Z_07b4",
    title: "电子并不绕着原子核打转",
    topic: "原子模型的演化",
    audience: "高中生",
    status: "failed",
    when: "昨天",
    backend: "deepseek",
    bucket: "昨天",
  },
  {
    id: "run_20260513T120002Z_31df",
    title: "mRNA 疫苗到底“教”了细胞什么",
    topic: "mRNA 疫苗工作机制",
    audience: "大学非生物专业",
    status: "success",
    when: "5 月 13 日",
    backend: "deepseek",
    bucket: "本周早些",
  },
  {
    id: "run_20260512T093015Z_dd91",
    title: "空调省电模式真的省电吗",
    topic: "空调省电机制",
    audience: "普通成年人",
    status: "success",
    when: "5 月 12 日",
    backend: "mock",
    bucket: "本周早些",
  },
  {
    id: "run_20260510T222041Z_b88a",
    title: "声音是怎么“翻译”成神经信号的",
    topic: "听觉信号通路",
    audience: "高中生",
    status: "success",
    when: "5 月 10 日",
    backend: "deepseek",
    bucket: "更早",
  },
];

const STAGES = [
  { stage: "memory", label: "Memory", msg: "为 student-001 检索记忆，匹配 4 条相关认知", sub: "黑洞基础 / 引力 / 事件视界 / 光速", time: "0.4s", dur: 600 },
  { stage: "teacher", label: "Teacher", msg: "第 1 轮：起草“黑洞不是洞”的开篇与三段主干", sub: "audience=初中生 / style=clear, engaging", time: "6.2s", dur: 6200 },
  { stage: "student", label: "Student", msg: "第 1 轮：模拟读者，给出 comprehension 6/10、interest 7/10", sub: "记下 3 个困惑点：事件视界、引力强度、为什么能看见", time: "3.1s", dur: 3100 },
  { stage: "aggregate", label: "Aggregate", msg: "第 1 轮：归纳为 2 项 must-fix、1 项 nice-to-have", sub: "must-fix #1: 事件视界没有先解释 / #2: “吸”字带来误解", time: "0.8s", dur: 800 },
  { stage: "teacher", label: "Teacher", msg: "第 2 轮：根据反馈重写第 2、3 段，并替换“吸”为“单行线”", sub: "引入“橡皮膜”类比，删除 3 处技术术语", time: "5.4s", dur: 5400 },
  { stage: "student", label: "Student", msg: "第 2 轮：comprehension 8/10、interest 8/10，剩 1 个困惑点", sub: "剩余困惑：为什么能拍到 2019 年那张照片", time: "2.7s", dur: 2700 },
  { stage: "aggregate", label: "Aggregate", msg: "第 2 轮：clarity 达到阈值 8，停止迭代", sub: "剩余 0 项 must-fix、1 项 nice-to-have，可交由 Editor 处理", time: "0.5s", dur: 500 },
  { stage: "fact_check", label: "Fact check", msg: "事实检查：0 项阻断，1 项警告", sub: "建议修正“向外的方向不存在”这一表述", time: "2.2s", dur: 2200 },
  { stage: "editor", label: "Editor", msg: "编辑润色：合并长句，统一术语“事件视界”", sub: "保留橡皮膜比喻；纠正一处标点", time: "3.5s", dur: 3500 },
  { stage: "done", label: "Done", msg: "最终稿写入 data/runs/.../final/article.md，记忆已更新 2 条", sub: "总耗时 38.6s / 2 轮迭代 / clarity 8/10", time: "0.3s", dur: 300 },
];

const THINKING = [
  "正在加载 student-001 的认知画像：用户知道引力会让东西掉下来，但 <em>没有把引力解释为时空弯曲</em>，对“事件视界”一词完全陌生。",
  "草稿读到第二段：“黑洞像井一样把东西吸进去”正是用户已有的 <em>错误类比</em>，会让她以为事件视界是一面墙。",
  "困惑点 1：“事件视界”直到第 3 段才出现，但第 2 段已经在使用它，<em>顺序需要调换</em>。",
  "困惑点 2：“连光都跑不掉”听起来像速度问题，需要说明 <em>是路径本身的问题，不是速度问题</em>。",
  "复述测试：用户能说出“黑洞是一段被压弯的时空”，并区分“洞”和“单行线”，理解评分上调到 8/10。",
];

const ITERATIONS = [
  { n: 1, clarity: 6, interest: 7, mustFix: 2, niceToHave: 1, durationMs: 9500 },
  { n: 2, clarity: 8, interest: 8, mustFix: 0, niceToHave: 1, durationMs: 8200 },
];

const MEMORY_UPDATES = [
  {
    op: "add",
    section: "knowledge",
    title: "黑洞基础理解",
    summary: "用户能区分“洞”和“事件视界”，理解光出不来是路径问题，不是速度问题。",
    tags: ["黑洞", "事件视界", "引力"],
    confidence: 0.85,
  },
  {
    op: "update",
    section: "misconceptions",
    title: "关于“吸”的直觉",
    summary: "用户已经从“黑洞像吸尘器”的描述中走出来，下次科普可从这一点继续推进。",
    tags: ["黑洞", "类比"],
    confidence: 0.6,
  },
];

const ARTICLE = {
  title: "黑洞不是“洞”：从被压弯的时空说起",
  synopsis: "在物理学里，黑洞并不是一个挖出来的洞，而是恒星坍缩后留下的一段被引力极度压弯的时空。本文带你区分“坑”和“黑洞”，理解事件视界，以及光为什么进得去却出不来。",
  meta: { wordCount: 1284, readMinutes: 5, audience: "初中生", topic: "黑洞为什么不是洞" },
  body: [
    { type: "h2", text: "不是井，而是斜坡" },
    { type: "p", text: "我们小时候听到“黑洞”两个字，脑子里画的常常是一口井：黑黝黝的，深不见底，掉进去的东西一直往下落。但天文学家用“黑洞”这个名字，其实更像一个翻译事故。它指的不是空间里被挖掉的一块，而是一个引力强到让附近的 <span class='annot' title='把空间和时间看作一个整体'>时空</span> 被压弯的区域。" },
    { type: "p", text: "把宇宙想象成一张橡皮膜。普通恒星会让膜微微下凹，地球绕着这个凹陷转，就像弹珠在漏斗边缘绕圈。如果一颗恒星燃料烧完，自己坍缩成只有几公里大，但质量还是原来那么重，它在膜上压出来的就不是普通凹陷，而是一段陡得几乎垂直的斜坡。" },
    { type: "h2", text: "事件视界：一条单行线" },
    { type: "p", text: "黑洞最关键的东西，是 <span class='annot' title='event horizon：黑洞的边界，光从这里掉进去就再出不来'>事件视界</span>。它不是一堵墙，而是一条单行线：跨过这条线，连光都没有机会再回头。" },
    { type: "p", text: "为什么连光都跑不掉？因为在事件视界以内，所有未来的路径都指向中心。这一点和“速度不够快”无关，不管你跑得多快，路本身已经没有通向外面的那一段。" },
    { type: "h2", text: "为什么我们能看见黑洞？" },
    { type: "p", text: "2019 年那张黑洞照片拍的不是黑洞本身，而是它周围被甩成圆环的高温气体。气体在掉进事件视界之前，会被加速到接近光速，发出强烈的电磁辐射。中间那块黑，是因为黑洞吞掉了背后的光线，留下了一块“应该有光但没有”的阴影。" },
    { type: "blockquote", text: "黑洞不是宇宙挖出来的洞，它是宇宙里光线无法再回头的区域。" },
    { type: "h2", text: "一个适合反复想的小练习" },
    { type: "p", text: "下次有人说“黑洞会把所有东西都吸进去”时，可以问一句：如果太阳现在突然变成一个相同质量的黑洞，地球会不会立刻被吸过去？答案是：不会。地球还会按现在的轨道继续转，因为远处的引力大小没有变，只是太阳被压缩成了非常小的一团。" },
  ],
};

const SOURCE_TEXT = "虽然名字里有“洞”字，黑洞并不是一个挖出来的洞。从广义相对论角度看，黑洞是一个由质量极度聚集导致时空被强烈弯曲的区域，其边界叫做事件视界。在事件视界以内，任何信号，包括光，都无法逃出。\n\n黑洞通常由大质量恒星在燃料耗尽后坍缩形成。坍缩过程压缩了恒星的全部物质，使得视界内的引力极强，但视界外的引力场和同等质量的普通天体在远处并无区别。这意味着如果太阳现在突然变成等质量的黑洞，地球依然会沿现有轨道继续运行。\n\n2019 年 4 月，事件视界望远镜国际合作团队公布了 M87 中心超大质量黑洞的第一张图像。图像中央的暗影并非黑洞本身，而是黑洞吞没背后光线后投下的“光的阴影”，周围环状的高亮区域来自被吸积盘加速到接近光速的炽热气体。";

const appState = {
  view: "filled",
  inputMode: "source",
  modality: "text",
  density: "normal",
  lang: "zh",
  search: "",
  historySearch: "",
  activeRunId: RUNS[0].id,
  source: SOURCE_TEXT,
  prompt: "",
  params: {
    topic: "黑洞为什么不是洞",
    audience: "初中生",
    style: "clear, engaging",
    userId: "student-001",
    iterations: 3,
  },
  currentIdx: 0,
  elapsed: 0,
  thinkIdx: 0,
  resultTab: "text",
  apiRunId: "",
  article: ARTICLE,
  settingsOpen: false,
  historyOpen: false,
  provider: "deepseek",
  apiKey: "sk-••••••••••••••••f8b",
  toast: "",
};

let progressTimer = null;
let stageTimer = null;
let thinkingTimer = null;
let toastTimer = null;

function t() {
  return STRINGS[appState.lang];
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function icon(name, size = 14) {
  const attrs = `width="${size}" height="${size}" viewBox="0 0 16 16" fill="none" aria-hidden="true"`;
  const common = `stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"`;
  const paths = {
    plus: `<path d="M8 3v10M3 8h10" ${common}/>` ,
    search: `<circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.3"/><path d="M11 11l3 3" ${common}/>` ,
    gear: `<circle cx="8" cy="8" r="2" stroke="currentColor" stroke-width="1.3"/><path d="M8 1.5v2M8 12.5v2M14.5 8h-2M3.5 8h-2M12.6 3.4l-1.4 1.4M4.8 11.2l-1.4 1.4M12.6 12.6l-1.4-1.4M4.8 4.8L3.4 3.4" ${common}/>` ,
    history: `<path d="M2.5 8a5.5 5.5 0 1 0 1.6-3.9" ${common}/><path d="M2.5 3v3h3" ${common}/><path d="M8 5v3.5l2.2 1.3" ${common}/>` ,
    book: `<path d="M2.5 3.5h4.5A1.5 1.5 0 0 1 8.5 5v8a1 1 0 0 0-1-1h-5V3.5zM13.5 3.5H9A1.5 1.5 0 0 0 7.5 5v8a1 1 0 0 1 1-1h5V3.5z" ${common}/>` ,
    memory: `<rect x="2.5" y="3.5" width="11" height="9" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M5 6.5h6M5 9h4" ${common}/>` ,
    upload: `<path d="M8 2v8M5 5l3-3 3 3M3 13h10" ${common}/>` ,
    check: `<path d="M3 8l3.5 3.5L13 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>` ,
    x: `<path d="M4 4l8 8M12 4l-8 8" ${common}/>` ,
    sparkle: `<path d="M8 1.5l1.3 4.2L13.5 7l-4.2 1.3L8 12.5 6.7 8.3 2.5 7l4.2-1.3L8 1.5z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"/>` ,
    image: `<rect x="2.5" y="3" width="11" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/><circle cx="6" cy="6.5" r="1" stroke="currentColor" stroke-width="1.3"/><path d="M3 12l3-3 2 2 3-3 2 2" ${common}/>` ,
    video: `<rect x="2" y="4" width="9" height="8" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M11 7l3-1.5v5L11 9z" ${common}/>` ,
    text: `<path d="M4 4h8M8 4v8M5.5 12h5" ${common}/>` ,
    lock: `<rect x="3" y="7" width="10" height="7" rx="1.5" stroke="currentColor" stroke-width="1.3"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" ${common}/>` ,
    refresh: `<path d="M13 8a5 5 0 1 1-1.5-3.5" ${common}/><path d="M13.5 2.5v3h-3" ${common}/>` ,
    arrow: `<path d="M3 8h10M9 4l4 4-4 4" ${common}/>` ,
  };
  return `<svg ${attrs}>${paths[name] || ""}</svg>`;
}

function render() {
  document.documentElement.lang = appState.lang === "zh" ? "zh" : "en";
  document.documentElement.dataset.density = appState.density;
  document.getElementById("app").innerHTML = `
    <div class="app" data-state="${appState.view}">
      ${renderSidebar()}
      <main class="col main">
        ${renderMainHead()}
        <div class="main-body">${renderMain()}</div>
      </main>
      ${renderMetaPanel()}
      ${appState.settingsOpen ? renderSettingsModal() : ""}
      ${appState.historyOpen ? renderHistoryOverlay() : ""}
      ${appState.toast ? `<div class="toast">${icon("check", 12)}${escapeHtml(appState.toast)}</div>` : ""}
    </div>`;
  bindEvents();
}

function renderSidebar() {
  const grouped = groupRuns(appState.search);
  return `
    <aside class="col sidebar" aria-label="Run navigation">
      <div class="brand">
        <div class="brand-mark">P</div>
        <div>
          <div class="brand-name">Pop Agent</div>
          <div class="brand-sub">multi-agent / v1.0</div>
        </div>
      </div>
      <button class="new-run-btn" data-action="new-run">${icon("plus", 13)}${t().newRun}<span class="kbd">⌘ N</span></button>
      <div class="section-label"><span>${t().runs}</span><span class="count">${RUNS.length}</span></div>
      <div class="search-row">
        ${icon("search", 12)}
        <label class="sr-only" for="run-search">Search runs</label>
        <input id="run-search" data-field="search" value="${escapeHtml(appState.search)}" placeholder="${appState.lang === "zh" ? "搜索 run / 主题" : "Search runs / topics"}" />
      </div>
      <div class="run-list">
        ${grouped.length ? grouped.map(renderRunGroup).join("") : `<div class="meta-empty" style="margin:8px">${appState.lang === "zh" ? "没有匹配的 run。" : "No matching runs."}</div>`}
      </div>
      <div class="sidebar-footer">
        <button class="nav-link" data-action="open-history">${icon("history")}${t().history}</button>
        <button class="nav-link" data-action="open-settings">${icon("gear")}${t().settings}</button>
        <a class="nav-link" href="https://github.com/Yi-ming-Zhao/pop-agent" target="_blank" rel="noreferrer">${icon("book")}${t().docs}</a>
        <div class="user-row">
          <div class="avatar">SZ</div>
          <div>
            <div style="font-size:12px;color:var(--ink)">${appState.lang === "zh" ? "本地工作区" : "Local workspace"}</div>
            <div class="uid">student-001</div>
          </div>
        </div>
      </div>
    </aside>`;
}

function groupRuns(query) {
  const q = query.trim().toLowerCase();
  const buckets = ["今天", "昨天", "本周早些", "更早"];
  const filtered = q
    ? RUNS.filter((run) => `${run.title} ${run.topic} ${run.audience} ${run.id}`.toLowerCase().includes(q))
    : RUNS;
  return buckets
    .map((bucket) => ({ bucket, items: filtered.filter((run) => run.bucket === bucket) }))
    .filter((group) => group.items.length);
}

function renderRunGroup(group) {
  return `
    <div>
      <div class="run-group-label">${escapeHtml(group.bucket)}</div>
      ${group.items.map((run) => `
        <button class="run-item ${run.id === appState.activeRunId ? "active" : ""}" data-run-id="${run.id}">
          <span class="ri-title">${escapeHtml(run.title)}</span>
          <span class="ri-meta">
            <span class="run-status ${run.status}"><span class="ind"></span>${run.status === "running" ? "RUN" : run.status === "failed" ? "FAIL" : "OK"}</span>
            <span class="dot-muted"></span><span>${escapeHtml(run.when)}</span>
            <span class="dot-muted"></span><span>${escapeHtml(run.audience)}</span>
          </span>
        </button>`).join("")}
    </div>`;
}

function renderMainHead() {
  const isRun = !["empty", "filled"].includes(appState.view);
  const runId = currentRunId();
  const title = appState.view === "running"
    ? t().runningTitle
    : appState.view === "success"
    ? ARTICLE.title
    : appState.view === "failed"
    ? t().failedTitle
    : "";
  const statusLabel = appState.view === "running"
    ? (appState.lang === "zh" ? "运行中" : "running")
    : appState.view === "failed"
    ? (appState.lang === "zh" ? "失败" : "failed")
    : (appState.lang === "zh" ? "已完成" : "done");
  return `
    <header class="main-head">
      <div>
        <div class="breadcrumb">${isRun ? `${t().workspace} / run ${runId}` : t().breadcrumb}</div>
        ${isRun ? `<h1>${escapeHtml(title)}</h1>` : `<div class="lede">${appState.lang === "zh" ? "主生成页 / 单 Run 模式 / 完整流程：Teacher -> Student -> Aggregate -> Fact check -> Editor" : "Single-run mode / pipeline: Teacher -> Student -> Aggregate -> Fact check -> Editor"}</div>`}
      </div>
      <div class="head-actions">
        ${isRun ? `<span class="head-pill ${appState.view}"><span class="ind"></span>${statusLabel}</span>` : ""}
        <button class="head-pill pill-button" data-action="toggle-lang">${appState.lang === "zh" ? "中文" : "English"}</button>
        <button class="head-pill pill-button" data-action="cycle-density">density: ${appState.density}</button>
        <span class="head-pill success"><span class="ind"></span>daemon: <span class="uid">localhost:8765</span></span>
      </div>
    </header>`;
}

function renderMain() {
  if (appState.view === "running") return renderProgress(false);
  if (appState.view === "failed") return renderProgress(true);
  if (appState.view === "success") return renderResult();
  return `
    ${appState.view === "empty" ? renderEmptyHero() : ""}
    ${renderInputBlock()}
    ${renderParameters()}
    ${renderModality()}
    ${renderGenerateBar()}
    ${appState.modality !== "text" ? `<div style="margin-top:22px">${renderPlaceholder(appState.modality, true)}</div>` : ""}`;
}

function renderEmptyHero() {
  const cards = [
    ["Teacher", "教师", "基于主题与读者画像，起草并修订草稿。"],
    ["Student", "学生", "模拟目标读者，给出可懂度和困惑点。"],
    ["Aggregator", "聚合", "把多人反馈归并成必须修复和可选优化。"],
    ["Fact check", "事实", "检查事实风险，给出阻断或警告。"],
    ["Editor", "编辑", "在不动事实的前提下润色最终稿。"],
  ];
  return `
    <section class="empty-hero">
      <h1>${appState.lang === "zh" ? "把复杂的东西，讲给一个真实的读者" : "Make hard things land for a specific reader."}</h1>
      <div class="lede">${appState.lang === "zh" ? "Pop Agent 用五个 Agent 协作把复杂材料改写成科普文章：教师起草、学生用读者认知模拟评分、聚合反馈、事实检查、最后编辑润色。" : "Pop Agent uses five agents: Teacher drafts, Student scores comprehension, Aggregator distills feedback, Fact checker flags risks, and Editor polishes."}</div>
      <div class="agent-card-row">
        ${cards.map(([tag, name, desc]) => `
          <div class="agent-card">
            <div class="tag">${tag.toUpperCase()}</div>
            <div class="name">${name}</div>
            <div class="desc">${desc}</div>
          </div>`).join("")}
      </div>
    </section>`;
}

function renderInputBlock() {
  return `
    <section class="section">
      <div class="section-h">
        <h2>${t().inputSection}</h2>
        <div class="step-num"><span class="num">1</span><span>${appState.lang === "zh" ? "材料来源" : "Material"}</span></div>
      </div>
      <div class="helper" style="font-size:13px;margin-bottom:12px;max-width:64ch">${t().inputHint}</div>
      <div class="tab-row" role="tablist">
        <button class="tab ${appState.inputMode === "source" ? "active" : ""}" data-action="input-mode" data-mode="source">${icon("upload", 12)}${t().sourceTab}</button>
        <button class="tab ${appState.inputMode === "prompt" ? "active" : ""}" data-action="input-mode" data-mode="prompt">${icon("sparkle", 12)}${t().promptTab}<span class="badge preview">Preview</span></button>
      </div>
      ${appState.inputMode === "source" ? renderSourceInput() : renderPromptInput()}
    </section>`;
}

function renderSourceInput() {
  return `
    <div class="source-shell">
      <label class="sr-only" for="source-text">Source text</label>
      <textarea id="source-text" data-field="source" placeholder="${t().placeholderSource}">${escapeHtml(appState.source)}</textarea>
      <div class="source-foot">
        <div class="actions">
          <input id="file-input" type="file" accept=".md,.txt,.pdf,text/markdown,text/plain,application/pdf" hidden />
          <button class="icon-btn" data-action="choose-file">${icon("upload", 11)}${appState.lang === "zh" ? "上传 .md / .txt / .pdf" : "Upload .md / .txt / .pdf"}</button>
          <button class="icon-btn" data-action="paste-clipboard">${appState.lang === "zh" ? "从剪贴板粘贴" : "Paste from clipboard"}</button>
        </div>
        <div>${appState.source.length.toLocaleString()} / 32,000 ${t().chars}</div>
      </div>
    </div>`;
}

function renderPromptInput() {
  return `
    <div class="prompt-shell">
      <label class="sr-only" for="prompt-text">Prompt</label>
      <textarea id="prompt-text" data-field="prompt" placeholder="${t().placeholderPrompt}">${escapeHtml(appState.prompt)}</textarea>
      <div class="prompt-preview-note">
        <span class="pin">PREVIEW</span>
        <div>${appState.lang === "zh" ? "<strong>Prompt-only 当前作为原型入口。</strong> 信息检索 Agent 还没接入，Teacher Agent 会直接按主题起草；建议先用上传文本模式做 v1 演示。" : "<strong>Prompt-only is a preview entry.</strong> The retrieval agent is not wired yet; source-text mode is recommended for v1 demos."}</div>
      </div>
    </div>`;
}

function renderParameters() {
  return `
    <section class="section">
      <div class="section-h">
        <h2>${t().parametersSection}</h2>
        <div class="step-num"><span class="num">2</span><span>${appState.lang === "zh" ? "生成参数" : "Generation parameters"}</span></div>
      </div>
      <div class="form-grid">
        <div class="field">
          <label for="topic">TOPIC</label>
          <input id="topic" data-param="topic" value="${escapeHtml(appState.params.topic)}" placeholder="${appState.lang === "zh" ? "例如：黑洞为什么不是洞" : "e.g. why a black hole is not a hole"}" />
        </div>
        <div class="field">
          <label for="audience">${t().audience}</label>
          <select id="audience" data-param="audience">${["初中生","高中生","大学非生物专业","普通成年人","general beginner"].map((x) => `<option ${x === appState.params.audience ? "selected" : ""}>${x}</option>`).join("")}</select>
        </div>
      </div>
      <div class="form-grid three">
        <div class="field">
          <label for="style">${t().style}</label>
          <select id="style" data-param="style">${["clear, engaging","narrative-driven","concise, factual","Socratic"].map((x) => `<option ${x === appState.params.style ? "selected" : ""}>${x}</option>`).join("")}</select>
        </div>
        <div class="field">
          <label for="user-id">${t().userId}</label>
          <input id="user-id" data-param="userId" value="${escapeHtml(appState.params.userId)}" />
        </div>
        <div class="field">
          <label for="iterations">${t().iterations}</label>
          <div class="field-wrap">
            <input id="iterations" type="number" min="1" max="6" data-param="iterations" value="${escapeHtml(appState.params.iterations)}" />
            <span class="suffix">${appState.lang === "zh" ? "轮" : "rounds"}</span>
          </div>
        </div>
      </div>
    </section>`;
}

function renderModality() {
  const items = [
    ["text", appState.lang === "zh" ? "文本" : "Text", "text", appState.lang === "zh" ? "科普文章，Markdown 输出。v1 主路径。" : "Markdown article. v1 main path.", "ready", "READY"],
    ["image", appState.lang === "zh" ? "图片" : "Image", "image", appState.lang === "zh" ? "示意图 + 关键图解。占位入口，等图像 Agent。" : "Diagrams and key visuals. Placeholder.", "beta", "BETA / PLACEHOLDER"],
    ["video", appState.lang === "zh" ? "视频" : "Video", "video", appState.lang === "zh" ? "解说短视频，等视频生成 Agent。" : "Narrated short video. Coming soon.", "soon", "COMING SOON"],
  ];
  return `
    <section class="section">
      <div class="section-h">
        <h2>${t().outputSection}</h2>
        <div class="step-num"><span class="num">3</span><span>${appState.lang === "zh" ? "输出形式" : "Output form"}</span></div>
      </div>
      <div class="helper" style="font-size:13px;margin-bottom:12px">${t().outputHint}</div>
      <div class="modality-row">
        ${items.map(([id, name, iconName, desc, badge, label]) => `
          <button class="mod-card ${appState.modality === id ? "selected" : ""}" data-action="modality" data-modality="${id}">
            <span class="mod-row">
              <span class="mod-name">${icon(iconName, 14)}${name}</span>
              <span class="mod-badge ${badge}">${label}</span>
            </span>
            <span class="mod-desc">${desc}</span>
          </button>`).join("")}
      </div>
    </section>`;
}

function renderGenerateBar() {
  const label = appState.modality === "text"
    ? t().generate
    : appState.modality === "image"
    ? (appState.lang === "zh" ? "查看图片占位" : "View image placeholder")
    : (appState.lang === "zh" ? "查看视频占位" : "View video placeholder");
  return `
    <div class="generate-bar">
      <div class="summary">
        <span><span class="k">${t().backend}</span>${RUNTIME.backend}</span>
        <span style="color:var(--ink-4)">/</span>
        <span><span class="k">model</span>${RUNTIME.model}</span>
        <span style="color:var(--ink-4)">/</span>
        <span><span class="k">${t().iterations}</span>${appState.params.iterations}</span>
        <span style="color:var(--ink-4)">/</span>
        <span><span class="k">memory</span>${escapeHtml(appState.params.userId)}</span>
      </div>
      <button class="btn-primary" data-action="generate">${label}<span class="kbd">⌘ ↵</span></button>
    </div>`;
}

function renderProgress(failed) {
  const current = failed ? 4 : appState.currentIdx;
  const iter = failed ? 2 : Math.min(3, Math.max(1, Math.floor(current / 3) + 1));
  return `
    <section class="section">
      <div class="section-h">
        <h2>${appState.lang === "zh" ? "运行进度" : "Run progress"}</h2>
        <div class="helper mono-label">${appState.lang === "zh" ? `第 ${iter} / ${appState.params.iterations} 轮迭代` : `iter ${iter}/${appState.params.iterations}`} / ${failed ? "11.4" : appState.elapsed.toFixed(1)}s</div>
      </div>
      <div class="run-frame">
        <div class="run-frame-head">
          <div class="left"><span style="color:var(--ink-3)">RUN</span><span class="run-id">${currentRunId()}</span><span class="iter-pill">${appState.lang === "zh" ? "迭代" : "iter"} ${iter}/${appState.params.iterations}</span></div>
          <div class="row">
            ${failed ? `<button class="btn-ghost" data-action="retry">${icon("refresh", 11)}${t().retry}</button>` : `<button class="btn-ghost" data-action="stop">${icon("x", 11)}${t().stop}</button>`}
          </div>
        </div>
        ${!failed ? `
          <div class="thinking">
            <div class="agent-tag">${icon("sparkle", 10)}STUDENT / 实时思考</div>
            <div class="think-body">${THINKING[appState.thinkIdx]}<span class="blink"></span></div>
          </div>` : ""}
        <div class="timeline">
          ${STAGES.map((stage, index) => renderStageRow(stage, index, current, failed)).join("")}
        </div>
        <div class="run-frame-foot">
          <div>${failed ? (appState.lang === "zh" ? "运行失败，可以从失败阶段重试" : "Run failed; retry from the failed stage") : `${appState.lang === "zh" ? "日志写入" : "Logs written to"} data/runs/${currentRunId().slice(0, 12)}...`}</div>
          <div>${!failed ? `${icon("check", 11)} ${appState.lang === "zh" ? "保留断点续跑" : "Resumable"}` : ""}</div>
        </div>
      </div>
    </section>`;
}

function renderStageRow(stage, index, current, failed) {
  let cls = "pending";
  if (failed && index === current) cls = "failed";
  else if (index < current) cls = "done";
  else if (!failed && index === current) cls = "current";
  const time = failed && index === current ? "failed" : index < current ? stage.time : index === current ? "..." : "...";
  return `
    <div class="tl-row ${cls}">
      <div class="tl-mark"><span class="dot"></span></div>
      <div class="tl-stage">${escapeHtml(stage.label)}</div>
      <div class="tl-msg">
        ${escapeHtml(stage.msg)}
        ${(index <= current || failed) && stage.sub ? `<span class="sub">${escapeHtml(stage.sub)}</span>` : ""}
        ${failed && index === current ? `<span class="err">ConnectError: TLS/SSL EOF when calling\nPOST ${RUNTIME.baseUrl}/chat/completions (timeout=120s, retries=3 exhausted)\nhint: 检查代理规则是否将 api.deepseek.com 走可用节点</span>` : ""}
      </div>
      <div class="tl-time">${time}</div>
    </div>`;
}

function renderResult() {
  return `
    <section class="section">
      <div class="section-h">
        <h2>${t().resultTitle}</h2>
        <div class="helper mono-label">${appState.lang === "zh" ? "完成于" : "finished"} 38.6s / 2 ${appState.lang === "zh" ? "轮" : "iter"}</div>
      </div>
      <div class="result-tabs">
        ${renderResultTab("text", appState.lang === "zh" ? "文本" : "Text", "text", "ready", "READY")}
        ${renderResultTab("image", appState.lang === "zh" ? "图片" : "Image", "image", "beta", "BETA")}
        ${renderResultTab("video", appState.lang === "zh" ? "视频" : "Video", "video", "soon", "COMING SOON")}
      </div>
      ${appState.resultTab === "text" ? renderArticle() : renderPlaceholder(appState.resultTab, false)}
    </section>`;
}

function renderResultTab(id, label, iconName, badge, badgeText) {
  return `<button class="rtab ${appState.resultTab === id ? "active" : ""}" data-action="result-tab" data-tab="${id}">${icon(iconName, 12)}${label}<span class="mod-badge ${badge}">${badgeText}</span></button>`;
}

function renderArticle() {
  const article = appState.article || ARTICLE;
  return `
    <article class="article">
      <div class="article-meta">
        <span>TOPIC / ${article.meta.topic}</span>
        <span>AUDIENCE / ${article.meta.audience}</span>
        <span>WORDS / ${article.meta.wordCount}</span>
        <span>READ / ${article.meta.readMinutes} min</span>
      </div>
      <h1>${article.title}</h1>
      <div class="synopsis">${article.synopsis}</div>
      ${article.body.map((block) => block.type === "h2" ? `<h2>${block.text}</h2>` : block.type === "blockquote" ? `<blockquote>${block.text}</blockquote>` : `<p>${block.text}</p>`).join("")}
    </article>
    <div class="article-actions">
      <div class="row wrap">
        <button class="btn-ghost" data-action="copy-md">${icon("upload", 11)}${appState.lang === "zh" ? "复制 Markdown" : "Copy markdown"}</button>
        <button class="btn-ghost" data-action="mock-action">${appState.lang === "zh" ? "下载 .md" : "Download .md"}</button>
        <button class="btn-ghost" data-action="mock-action">${appState.lang === "zh" ? "在 VS Code 打开" : "Open in VS Code"}</button>
      </div>
      <div class="row wrap">
        <button class="btn-ghost" data-action="retry">${icon("refresh", 11)}${appState.lang === "zh" ? "再生成一遍" : "Run again"}</button>
        <button class="btn-primary" data-action="mock-action">${appState.lang === "zh" ? "发布到草稿" : "Save to drafts"}</button>
      </div>
    </div>`;
}

function renderPlaceholder(kind, inline) {
  const isImage = kind === "image";
  const status = isImage ? "beta" : "soon";
  const statusLabel = isImage ? "BETA / PLACEHOLDER" : "COMING SOON";
  const title = isImage
    ? (appState.lang === "zh" ? "图片生成 / 等待后端接入" : "Image generation / backend pending")
    : (appState.lang === "zh" ? "视频生成 / 暂未开放" : "Video generation / not open");
  const desc = isImage
    ? (appState.lang === "zh" ? "图像 Agent 会读取最终文章里的关键概念，挑出 3 到 5 张示意图来强化讲解。接口接通后，这里会直接显示生成图组；当前先展示用户可以预期到什么。" : "Image Agent will pick key visuals from the final article. Once the endpoint is live, this surface will show the rendered set.")
    : (appState.lang === "zh" ? "视频 Agent 会基于编辑后的文章生成 60 到 90 秒的解说短视频。视频后端排在后续版本，目前仅保留入口。" : "Video Agent will build a 60 to 90s narrated short in a later release. Entry-only for now.");
  return `
    <div class="placeholder-card">
      <div class="ph-visual">${isImage ? "IMG / PLACEHOLDER" : "VIDEO / COMING SOON"}</div>
      <div class="ph-body">
        <div class="ph-status ${status}">${icon("lock", 10)}${statusLabel}</div>
        <h3>${title}</h3>
        <div class="ph-desc">${desc}</div>
        ${inline ? "" : `
          <div class="ph-plan">
            <div class="line"><span class="k">backend</span><span class="v">${isImage ? "POST /api/generate?modality=image (规划中)" : "POST /api/generate?modality=video (未规划)"}</span></div>
            <div class="line"><span class="k">artifact</span><span class="v">${isImage ? "image/png / 多张 / path[]" : "video/mp4 / 60-90s / path"}</span></div>
            <div class="line"><span class="k">contract</span><span class="v">${appState.lang === "zh" ? "前端只消费已生成 artifact，不重写流水线逻辑" : "Frontend consumes artifacts; it does not run the pipeline."}</span></div>
            <div class="line"><span class="k">eta</span><span class="v">${isImage ? "v1.2 / 2026 Q3" : "v1.4 / 2026 Q4"}</span></div>
          </div>
          <div class="row wrap">
            <button class="btn-primary" disabled>${icon("lock", 11)}${appState.lang === "zh" ? "生成（未开放）" : "Generate (locked)"}</button>
            <button class="btn-ghost" data-action="mock-action">${appState.lang === "zh" ? "加入等待名单" : "Join waitlist"}</button>
            <button class="btn-ghost" data-action="mock-action">${appState.lang === "zh" ? "查看 mock 输出" : "View mock output"}</button>
          </div>`}
      </div>
    </div>`;
}

function renderMetaPanel() {
  if (["empty", "filled"].includes(appState.view)) return renderMetaEmpty();
  const iterations = appState.view === "success" ? ITERATIONS : appState.view === "failed" ? ITERATIONS.slice(0, 1) : ITERATIONS.slice(0, Math.max(0, Math.min(2, Math.floor(appState.currentIdx / 3))));
  const currentIter = appState.view === "running" ? Math.min(3, Math.floor(appState.currentIdx / 3) + 1) : appState.view === "failed" ? 2 : 2;
  return `
    <aside class="col meta" aria-label="Run metadata">
      ${renderRunMeta()}
      <div class="meta-section">
        <h3><span>ITERATIONS</span><span class="h-act mono-label">${currentIter}/3</span></h3>
        ${iterations.map(renderIteration).join("")}
        ${appState.view === "running" && currentIter > iterations.length ? `<div class="iter-row"><div class="iter-num">#${currentIter}</div><div><div class="iter-label">in progress</div><div class="iter-value" style="color:var(--ink-3)">等待 Student Agent 完成评估...</div></div><div class="clarity" style="color:var(--ink-4)">...</div></div>` : ""}
      </div>
      ${renderFactCheck()}
      ${renderMemoryUpdates()}
      ${renderArtifacts()}
    </aside>`;
}

function renderMetaEmpty() {
  return `
    <aside class="col meta" aria-label="Runtime metadata">
      <div class="meta-section">
        <h3>RUNTIME</h3>
        <div class="kv-block">
          <div class="kv"><span class="k">backend</span><span class="v">${RUNTIME.backend}</span></div>
          <div class="kv"><span class="k">model</span><span class="v">${RUNTIME.model}</span></div>
          <div class="kv"><span class="k">base_url</span><span class="v" style="font-size:10px">${RUNTIME.baseUrl}</span></div>
          <div class="kv"><span class="k">max_iter</span><span class="v">${RUNTIME.maxIterations}</span></div>
          <div class="kv"><span class="k">threshold</span><span class="v">clarity >= ${RUNTIME.clarityThreshold}</span></div>
          <div class="kv"><span class="k">data_dir</span><span class="v" style="font-size:10px">${RUNTIME.dataDir}</span></div>
        </div>
      </div>
      <div class="meta-section">
        <h3>PIPELINE</h3>
        <div class="kv-block" style="gap:8px">
          ${["Teacher","Student","Aggregator","Fact check","Editor"].map((x, i) => `<div class="kv"><span class="k">${String(i + 1).padStart(2, "0")}</span><span class="v">${x}</span></div>`).join("")}
        </div>
        <div class="helper" style="font-size:11px;margin-top:8px;line-height:1.5">${appState.lang === "zh" ? "迭代会在 clarity 达到阈值且 must-fix 为 0 时提前停止，最多 3 轮。" : "Loop stops early when clarity meets threshold and must-fix is empty. Up to 3 rounds."}</div>
      </div>
      <div class="meta-section">
        <h3>USER MEMORY / student-001</h3>
        <div class="kv-block">
          <div class="kv"><span class="k">knowledge</span><span class="v">4 条</span></div>
          <div class="kv"><span class="k">misconceptions</span><span class="v">2 条</span></div>
          <div class="kv"><span class="k">preferences</span><span class="v">3 条</span></div>
          <div class="kv"><span class="k">last_run</span><span class="v">2 天前</span></div>
        </div>
        <button class="btn-ghost" style="width:100%;justify-content:center;margin-top:8px" data-action="mock-action">${icon("memory", 11)}${appState.lang === "zh" ? "查看认知记忆" : "Open memory"}</button>
      </div>
    </aside>`;
}

function renderRunMeta() {
  return `
    <div class="meta-section">
      <h3>RUN</h3>
      <div class="kv-block">
        <div class="kv"><span class="k">run_id</span><span class="v">${currentRunId().slice(0, 28)}</span></div>
        <div class="kv"><span class="k">backend</span><span class="v">${RUNTIME.backend}</span></div>
        <div class="kv"><span class="k">model</span><span class="v">${RUNTIME.model}</span></div>
        <div class="kv"><span class="k">user</span><span class="v">${escapeHtml(appState.params.userId)}</span></div>
        <div class="kv"><span class="k">audience</span><span class="v">${escapeHtml(appState.params.audience)}</span></div>
        <div class="kv"><span class="k">started</span><span class="v">14:23:08Z</span></div>
      </div>
    </div>`;
}

function renderIteration(iteration) {
  return `
    <div class="iter-row">
      <div class="iter-num">#${iteration.n}</div>
      <div>
        <div class="iter-label">clarity / interest / must-fix</div>
        <div class="iter-value">${iteration.clarity}/10 / ${iteration.interest}/10 / ${iteration.mustFix}</div>
      </div>
      <div class="clarity">${Array.from({ length: 10 }, (_, i) => `<span class="seg ${i < iteration.clarity ? "on" : ""}"></span>`).join("")}</div>
    </div>`;
}

function renderFactCheck() {
  if (appState.view === "running") {
    return `<div class="meta-section"><h3>FACT CHECK</h3><div class="meta-empty">${appState.lang === "zh" ? "事实检查尚未开始" : "Fact check pending"}</div></div>`;
  }
  if (appState.view === "failed") {
    return `<div class="meta-section"><h3>FACT CHECK</h3><div class="fact-card"><div class="fact-row block">${icon("x", 11)}${appState.lang === "zh" ? "运行中断，无事实检查结果" : "Run aborted / no fact check"}</div></div></div>`;
  }
  return `
    <div class="meta-section">
      <h3>FACT CHECK</h3>
      <div class="fact-card">
        <div class="fact-row ok">${icon("check", 11)}0 blocking issues</div>
        <div class="fact-row warning">${icon("sparkle", 11)}1 warning</div>
        <div class="fact-item">“事件视界以内向外的方向不存在”表述偏硬，建议改为“所有未来路径都指向中心”，避免给读者“方向消失”的错觉。</div>
      </div>
    </div>`;
}

function renderMemoryUpdates() {
  const body = appState.view === "success"
    ? MEMORY_UPDATES.map((m) => `
      <div class="memory-update">
        <div class="mu-head"><span class="op ${m.op === "update" ? "update" : ""}">${m.op === "update" ? "~" : "+"}</span><span>${m.section}</span><span style="color:var(--ink-4)">/ ${m.tags.join(", ")}</span><span style="margin-left:auto">conf ${m.confidence.toFixed(2)}</span></div>
        <div class="mu-title">${m.title}</div>
        <div class="mu-sum">${m.summary}</div>
      </div>`).join("")
    : `<div class="meta-empty">${appState.view === "running" ? (appState.lang === "zh" ? "生成完成后会写入用户认知记忆" : "Memory writes after run completes") : (appState.lang === "zh" ? "运行未完成，无记忆更新" : "Run incomplete / no memory updates")}</div>`;
  return `<div class="meta-section"><h3><span>MEMORY UPDATES</span><button class="h-act" data-action="mock-action">${appState.lang === "zh" ? "查看全部" : "View all"}</button></h3>${body}</div>`;
}

function renderArtifacts() {
  return `
    <div class="meta-section">
      <h3>ARTIFACTS</h3>
      <div class="kv-block">
        <div class="kv"><span class="k">text</span><span class="v">${appState.view === "success" ? "article.md" : "..."}</span></div>
        <div class="kv"><span class="k">image</span><span class="v" style="color:var(--ink-4)">locked</span></div>
        <div class="kv"><span class="k">video</span><span class="v" style="color:var(--ink-4)">locked</span></div>
      </div>
    </div>`;
}

function renderSettingsModal() {
  return `
    <div class="modal-bg" data-action="close-overlays">
      <section class="modal" role="dialog" aria-modal="true" aria-labelledby="settings-title" data-modal>
        <div class="modal-head">
          <h2 id="settings-title">${appState.lang === "zh" ? "设置 / 安装" : "Settings"}</h2>
          <button class="modal-close" data-action="close-overlays" aria-label="Close">${icon("x")}</button>
        </div>
        <div class="modal-body">
          <div class="setting-block">
            <div class="setting-label">${appState.lang === "zh" ? "模型供应商" : "Provider"}</div>
            <div class="provider-row">
              ${[
                ["deepseek", "DeepSeek", "deepseek-v4-pro"],
                ["openai", "OpenAI-compatible", "gpt-4o / claude / 自部署"],
                ["mock", "Mock", appState.lang === "zh" ? "无需 API key" : "No API key"],
              ].map(([id, name, desc]) => `<button class="provider-card ${appState.provider === id ? "selected" : ""}" data-provider="${id}"><span class="pname">${name}</span><span class="pdesc">${desc}</span></button>`).join("")}
            </div>
          </div>
          ${appState.provider === "mock" ? "" : `
            <div class="setting-block">
              <label class="setting-label" for="api-key">API KEY</label>
              <input id="api-key" class="text-field" type="password" data-field="apiKey" value="${escapeHtml(appState.apiKey)}" />
              <div class="field-help">${appState.lang === "zh" ? "保存到 ~/.config/pop-agent/config.json（权限 0600），界面只展示脱敏后的密钥。" : "Saved to ~/.config/pop-agent/config.json (0600). Masked in the UI."}</div>
            </div>
            <div class="setting-block"><label class="setting-label" for="base-url">BASE URL</label><input id="base-url" class="text-field" value="${RUNTIME.baseUrl}" /></div>
            <div class="setting-block"><label class="setting-label" for="model">MODEL</label><input id="model" class="text-field" value="${RUNTIME.model}" /></div>`}
          <div class="setting-grid">
            <div class="setting-block"><label class="setting-label" for="max-iter">${appState.lang === "zh" ? "最大迭代轮数" : "Max iterations"}</label><input id="max-iter" class="text-field" type="number" value="${RUNTIME.maxIterations}" /></div>
            <div class="setting-block"><label class="setting-label" for="threshold">${appState.lang === "zh" ? "清晰度阈值" : "Clarity threshold"}</label><input id="threshold" class="text-field" type="number" value="${RUNTIME.clarityThreshold}" /></div>
          </div>
          <div class="setting-grid">
            <div class="setting-block"><label class="setting-label" for="ui-lang">UI LANGUAGE</label><select id="ui-lang" class="text-field" data-field="lang"><option value="zh" ${appState.lang === "zh" ? "selected" : ""}>中文</option><option value="en" ${appState.lang === "en" ? "selected" : ""}>English</option></select></div>
            <div class="setting-block"><label class="setting-label" for="density">DENSITY</label><select id="density" class="text-field" data-field="density"><option value="compact" ${appState.density === "compact" ? "selected" : ""}>compact</option><option value="normal" ${appState.density === "normal" ? "selected" : ""}>normal</option><option value="comfy" ${appState.density === "comfy" ? "selected" : ""}>comfy</option></select></div>
          </div>
          <div class="setting-block"><label class="setting-label" for="data-dir">${appState.lang === "zh" ? "数据目录" : "Data directory"}</label><input id="data-dir" class="text-field" value="${RUNTIME.dataDir}" /><div class="field-help">${appState.lang === "zh" ? "所有 run 与用户记忆都会保存在这里。" : "All runs and user memory live here."}</div></div>
          <div class="connection-status"><span class="ok"></span>${appState.lang === "zh" ? "上次连接测试通过 / 7 分钟前 / 1.2s" : "Last test passed / 7 min ago / 1.2s"}</div>
        </div>
        <div class="modal-foot">
          <span class="hint">${appState.lang === "zh" ? "配置文件: ~/.config/pop-agent/config.json" : "Config: ~/.config/pop-agent/config.json"}</span>
          <div class="row"><button class="btn-ghost" data-action="close-overlays">${appState.lang === "zh" ? "取消" : "Cancel"}</button><button class="btn-ghost" data-action="mock-action">${appState.lang === "zh" ? "保存当前配置" : "Save"}</button><button class="btn-primary" data-action="mock-action">${appState.lang === "zh" ? "测试并保存" : "Test & save"}</button></div>
        </div>
      </section>
    </div>`;
}

function renderHistoryOverlay() {
  const q = appState.historySearch.trim().toLowerCase();
  const runs = q ? RUNS.filter((run) => `${run.title} ${run.topic} ${run.audience} ${run.id}`.toLowerCase().includes(q)) : RUNS;
  return `
    <div class="modal-bg history-overlay" data-action="close-overlays">
      <section class="modal" role="dialog" aria-modal="true" aria-labelledby="history-title" data-modal>
        <div class="modal-head">
          <h2 id="history-title">${appState.lang === "zh" ? "历史记录 / Runs" : "History / Runs"}</h2>
          <button class="modal-close" data-action="close-overlays" aria-label="Close">${icon("x")}</button>
        </div>
        <div class="modal-body" style="padding-top:8px">
          <div class="search-row" style="margin-bottom:12px">${icon("search", 12)}<label class="sr-only" for="history-search">Search history</label><input id="history-search" data-field="historySearch" value="${escapeHtml(appState.historySearch)}" placeholder="${appState.lang === "zh" ? "搜索 run id / 主题 / 读者..." : "Search run id / topic / audience..."}" /></div>
          <div class="history-header"><span>TITLE / RUN ID</span><span>STATUS</span><span>BACKEND</span><span>WHEN</span></div>
          ${runs.map((run) => `
            <button class="history-row" data-run-id="${run.id}">
              <span><span class="h-title">${escapeHtml(run.title)}</span><span class="h-sub">${run.id} / ${run.audience}</span></span>
              <span class="run-status ${run.status}"><span class="ind"></span>${run.status.toUpperCase()}</span>
              <span class="h-col">${run.backend}</span>
              <span class="h-col">${run.when}</span>
            </button>`).join("")}
          ${runs.length ? "" : `<div class="meta-empty" style="margin-top:14px">${appState.lang === "zh" ? "没有匹配的 run。" : "No matching runs."}</div>`}
        </div>
        <div class="modal-foot"><span class="hint">esc ${appState.lang === "zh" ? "关闭" : "close"}</span><button class="btn-ghost" data-action="close-overlays">${appState.lang === "zh" ? "关闭" : "Close"}</button></div>
      </section>
    </div>`;
}

function bindEvents() {
  document.querySelectorAll("[data-action]").forEach((element) => {
    element.addEventListener("click", onAction);
  });
  document.querySelectorAll("[data-field]").forEach((element) => {
    element.addEventListener("input", onField);
    element.addEventListener("change", onField);
  });
  document.querySelectorAll("[data-param]").forEach((element) => {
    element.addEventListener("input", onParam);
    element.addEventListener("change", onParam);
  });
  document.querySelectorAll("[data-run-id]").forEach((element) => {
    element.addEventListener("click", onPickRun);
  });
  document.querySelectorAll("[data-provider]").forEach((element) => {
    element.addEventListener("click", () => {
      appState.provider = element.dataset.provider;
      render();
    });
  });
  const file = document.getElementById("file-input");
  if (file) file.addEventListener("change", onFile);
  document.querySelectorAll("[data-modal]").forEach((modal) => {
    modal.addEventListener("click", (event) => event.stopPropagation());
  });
}

function onAction(event) {
  const action = event.currentTarget.dataset.action;
  if (action === "new-run") newRun();
  if (action === "open-settings") { appState.settingsOpen = true; render(); }
  if (action === "open-history") { appState.historyOpen = true; render(); requestAnimationFrame(() => document.getElementById("history-search")?.focus()); }
  if (action === "close-overlays") closeOverlays();
  if (action === "input-mode") { appState.inputMode = event.currentTarget.dataset.mode; touchFilled(); render(); }
  if (action === "modality") { appState.modality = event.currentTarget.dataset.modality; render(); }
  if (action === "result-tab") { appState.resultTab = event.currentTarget.dataset.tab; render(); }
  if (action === "generate") generate();
  if (action === "stop") { stopProgress(); appState.view = "filled"; render(); }
  if (action === "retry") generate();
  if (action === "choose-file") document.getElementById("file-input")?.click();
  if (action === "paste-clipboard") pasteClipboard();
  if (action === "toggle-lang") { appState.lang = appState.lang === "zh" ? "en" : "zh"; render(); }
  if (action === "cycle-density") cycleDensity();
  if (action === "copy-md") copyMarkdown();
  if (action === "mock-action") showToast(appState.lang === "zh" ? "Mock 模式下已记录这个操作" : "Recorded in mock mode");
}

function onField(event) {
  const field = event.currentTarget.dataset.field;
  appState[field] = event.currentTarget.value;
  if (["source", "prompt"].includes(field)) touchFilled();
  render();
}

function onParam(event) {
  const param = event.currentTarget.dataset.param;
  appState.params[param] = param === "iterations" ? Number(event.currentTarget.value || 1) : event.currentTarget.value;
  touchFilled();
  render();
}

function onPickRun(event) {
  const id = event.currentTarget.dataset.runId;
  const run = RUNS.find((item) => item.id === id);
  if (!run) return;
  appState.activeRunId = id;
  appState.historyOpen = false;
  appState.params.topic = run.topic;
  appState.params.audience = run.audience;
  appState.view = run.status === "success" ? "success" : run.status === "failed" ? "failed" : "running";
  if (appState.view === "running") startProgress();
  else stopProgress();
  render();
}

function onFile(event) {
  const file = event.currentTarget.files?.[0];
  if (!file) return;
  if (file.name.toLowerCase().endsWith(".pdf")) {
    showToast(appState.lang === "zh" ? "PDF 解析接口尚未接入，已保留上传入口" : "PDF parsing is not wired yet");
    return;
  }
  file.text().then((text) => {
    appState.source = text;
    appState.inputMode = "source";
    touchFilled();
    render();
  });
}

function newRun() {
  stopProgress();
  appState.view = "empty";
  appState.activeRunId = "";
  appState.source = "";
  appState.prompt = "";
  appState.resultTab = "text";
  appState.apiRunId = "";
  appState.article = ARTICLE;
  render();
}

function touchFilled() {
  if (appState.view === "empty") appState.view = "filled";
}

function generate() {
  if (appState.modality !== "text") {
    showToast(appState.lang === "zh" ? "该模态当前为占位入口" : "This modality is currently a placeholder");
    return;
  }
  appState.view = "running";
  appState.activeRunId = RUNS[0].id;
  appState.currentIdx = 0;
  appState.elapsed = 0;
  appState.thinkIdx = 0;
  appState.apiRunId = "";
  appState.article = ARTICLE;
  startProgress();
  render();
  if (shouldUseRealApi()) {
    createRunViaApi()
      .then(applyApiResult)
      .catch(() => {
        stopProgress();
        appState.view = "failed";
        render();
      });
  }
}

function startProgress() {
  stopProgress();
  progressTimer = setInterval(() => {
    appState.elapsed = Math.round((appState.elapsed + 0.1) * 10) / 10;
    updateElapsedOnly();
  }, 100);
  thinkingTimer = setInterval(() => {
    appState.thinkIdx = (appState.thinkIdx + 1) % THINKING.length;
    render();
  }, 4200);
  scheduleNextStage();
}

function scheduleNextStage() {
  const index = appState.currentIdx;
  if (index >= STAGES.length) {
    if (shouldUseRealApi()) {
      render();
      return;
    }
    appState.view = "success";
    appState.resultTab = "text";
    stopProgress();
    render();
    return;
  }
  const delay = Math.max(500, STAGES[index].dur * 0.22);
  stageTimer = setTimeout(() => {
    appState.currentIdx += 1;
    render();
    scheduleNextStage();
  }, delay);
}

function stopProgress() {
  if (progressTimer) clearInterval(progressTimer);
  if (stageTimer) clearTimeout(stageTimer);
  if (thinkingTimer) clearInterval(thinkingTimer);
  progressTimer = null;
  stageTimer = null;
  thinkingTimer = null;
}

function updateElapsedOnly() {
  const helper = document.querySelector(".section-h .helper");
  if (helper && appState.view === "running") {
    const iter = Math.min(3, Math.max(1, Math.floor(appState.currentIdx / 3) + 1));
    helper.textContent = appState.lang === "zh"
      ? `第 ${iter} / ${appState.params.iterations} 轮迭代 / ${appState.elapsed.toFixed(1)}s`
      : `iter ${iter}/${appState.params.iterations} / ${appState.elapsed.toFixed(1)}s`;
  }
}

function closeOverlays() {
  appState.settingsOpen = false;
  appState.historyOpen = false;
  render();
}

function cycleDensity() {
  const order = ["compact", "normal", "comfy"];
  appState.density = order[(order.indexOf(appState.density) + 1) % order.length];
  render();
}

function currentRunId() {
  if (appState.apiRunId) return appState.apiRunId;
  if (appState.view === "success") return "run_20260515T141802Z_8f3a";
  if (appState.view === "failed") return "run_20260515T143112Z_b2c1";
  return appState.activeRunId || "run_20260515T142308Z_8f3a";
}

function shouldUseRealApi() {
  return new URLSearchParams(window.location.search).get("api") === "real";
}

async function createRunViaApi() {
  const response = await fetch(`${API_BASE}/api/generate`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      topic: appState.params.topic,
      audience: appState.params.audience,
      user_id: appState.params.userId,
      style: appState.params.style,
      source_text: appState.inputMode === "source" ? appState.source : appState.prompt,
      max_iterations: appState.params.iterations,
    }),
  });
  if (!response.ok) throw new Error(`Generation failed: ${response.status}`);
  return response.json();
}

function applyApiResult(result) {
  stopProgress();
  appState.apiRunId = result.run_id || "";
  appState.view = "success";
  appState.resultTab = "text";
  appState.article = mapApiArticle(result);
  render();
}

function mapApiArticle(result) {
  const final = result.final_article || {};
  const content = String(final.content || "").trim();
  const paragraphs = content
    ? content.split(/\n{2,}/).map((text) => ({ type: "p", text: escapeHtml(text) }))
    : ARTICLE.body;
  return {
    title: final.title || ARTICLE.title,
    synopsis: final.synopsis || ARTICLE.synopsis,
    meta: {
      topic: result.topic || appState.params.topic,
      audience: result.audience || appState.params.audience,
      wordCount: content ? content.length : ARTICLE.meta.wordCount,
      readMinutes: Math.max(1, Math.round((content.length || ARTICLE.meta.wordCount) / 500)),
    },
    body: paragraphs,
  };
}

async function pasteClipboard() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) {
      appState.source = text;
      appState.inputMode = "source";
      touchFilled();
      render();
    }
  } catch {
    showToast(appState.lang === "zh" ? "浏览器未授权读取剪贴板" : "Clipboard permission was not granted");
  }
}

async function copyMarkdown() {
  const article = appState.article || ARTICLE;
  const md = `# ${article.title}\n\n${article.synopsis}\n\n${article.body.map((block) => {
    if (block.type === "h2") return `## ${block.text}`;
    if (block.type === "blockquote") return `> ${block.text}`;
    return block.text.replace(/<[^>]+>/g, "");
  }).join("\n\n")}`;
  try {
    await navigator.clipboard.writeText(md);
    showToast(appState.lang === "zh" ? "Markdown 已复制" : "Markdown copied");
  } catch {
    showToast(appState.lang === "zh" ? "复制失败，浏览器未授权" : "Copy failed; browser permission denied");
  }
}

function showToast(message) {
  appState.toast = message;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    appState.toast = "";
    render();
  }, 2200);
  render();
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeOverlays();
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "n") {
    event.preventDefault();
    newRun();
  }
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    event.preventDefault();
    generate();
  }
});

window.PopAgentWebV1 = { STATE_ORDER, RUNTIME, RUNS, STAGES, ITERATIONS, MEMORY_UPDATES, createRunViaApi };
render();
