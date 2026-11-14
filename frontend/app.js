// Frontend Application Logic for CO4031 Academic Data Warehouse & DSS
const API_BASE = "";

let metadataCache = null;
let olapOutcomeChartInstance = null;
let olapRateChartInstance = null;
let dssWhatIfChartInstance = null;
let featureImportanceChartInstance = null;

// Switch active UI tab
function switchTab(tabName) {
    const tabs = ["olap", "dss", "early", "dw"];
    tabs.forEach((t) => {
        const sec = document.getElementById(`tab-${t}`);
        const btn = document.getElementById(`tab-btn-${t}`);
        if (t === tabName) {
            sec.classList.remove("hidden");
            btn.classList.add("active");
            btn.classList.remove("text-slate-300");
        } else {
            sec.classList.add("hidden");
            btn.classList.remove("active");
            btn.classList.add("text-slate-300");
        }
    });

    if (tabName === "olap") {
        runOlapQuery();
    } else if (tabName === "dss") {
        loadStudentIntoDss();
    } else if (tabName === "early") {
        loadEarlyWarningList();
    } else if (tabName === "dw") {
        loadModelMetricsAndImportance();
    }
}

// Initialize dropdowns from /records/metadata
async function initMetadata() {
    try {
        const res = await fetch(`${API_BASE}/records/metadata`);
        const json = await res.json();
        if (json.code !== "OK") return;
        metadataCache = json.data;

        const courses = metadataCache.courses || {};
        const courseSelectors = ["olap-filter-course", "dss-course", "ew-filter-course", "ins-course"];

        courseSelectors.forEach((selId) => {
            const el = document.getElementById(selId);
            if (!el) return;
            const keepFirst = selId.includes("filter");
            const firstHtml = keepFirst ? `<option value="">Tất cả</option>` : "";
            const optionsHtml = Object.entries(courses)
                .map(([id, name]) => `<option value="${id}">${name} (#${id})</option>`)
                .join("");
            el.innerHTML = firstHtml + optionsHtml;
        });

        const fillSelect = (id, mapObj) => {
            const el = document.getElementById(id);
            if (!el || !mapObj) return;
            el.innerHTML = Object.entries(mapObj)
                .map(([k, v]) => `<option value="${k}">${v}</option>`)
                .join("");
        };
        fillSelect("ins-marital", metadataCache.marital_statuses);
        fillSelect("ins-nationality", metadataCache.nationalities);
        fillSelect("ins-app-mode", metadataCache.application_modes);
    } catch (err) {
        console.error("Failed to load metadata:", err);
    }
}

// ============================================================================
// TAB 1: OLAP CUBE ANALYTICS
// ============================================================================

function buildOlapFilters() {
    const filters = {};
    const courseVal = document.getElementById("olap-filter-course").value;
    const genderVal = document.getElementById("olap-filter-gender").value;
    const scholVal = document.getElementById("olap-filter-scholarship").value;
    const debtorVal = document.getElementById("olap-filter-debtor").value;

    if (courseVal !== "") {
        filters.course_id = { type: "values", values: [parseInt(courseVal, 10)] };
    }
    if (genderVal !== "") {
        filters.gender_id = { type: "values", values: [parseInt(genderVal, 10)] };
    }
    if (scholVal !== "") {
        filters.scholarship_holder = { type: "values", values: [scholVal === "true"] };
    }
    if (debtorVal !== "") {
        filters.debtor = { type: "values", values: [debtorVal === "true"] };
    }
    return filters;
}

function resetOlapFilters() {
    document.getElementById("olap-dim-1").value = "course_id";
    document.getElementById("olap-dim-2").value = "";
    document.getElementById("olap-filter-course").value = "";
    document.getElementById("olap-filter-gender").value = "";
    document.getElementById("olap-filter-scholarship").value = "";
    document.getElementById("olap-filter-debtor").value = "";
    runOlapQuery();
}

async function runOlapQuery() {
    const dim1 = document.getElementById("olap-dim-1").value;
    const dim2 = document.getElementById("olap-dim-2").value;
    const groupBy = [dim1];
    if (dim2 && dim2 !== dim1) {
        groupBy.push(dim2);
    }

    const filters = buildOlapFilters();

    try {
        const res = await fetch(`${API_BASE}/records/olap/cube`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ group_by: groupBy, filters, include_records: false }),
        });
        const json = await res.json();
        if (json.code !== "OK") return;

        const { stats, groups } = json.data;
        renderOlapKpis(stats);
        renderOlapCharts(groups, groupBy);
        renderOlapTable(groups, groupBy);
    } catch (err) {
        console.error("OLAP Query Error:", err);
    }
}

function renderOlapKpis(stats) {
    document.getElementById("kpi-total").textContent = stats.count.toLocaleString();
    document.getElementById("kpi-enrolled-sub").textContent =
        `Đang theo học (Enrolled): ${stats.enrolled.toLocaleString()} SV (${(stats.enrolled_rate * 100).toFixed(1)}%)`;

    document.getElementById("kpi-dropout-rate").textContent = `${(stats.dropout_rate * 100).toFixed(2)}%`;
    document.getElementById("kpi-dropout-count").textContent = `Số lượng bỏ học: ${stats.dropouts.toLocaleString()} SV`;

    document.getElementById("kpi-grad-rate").textContent = `${(stats.graduation_rate * 100).toFixed(2)}%`;
    document.getElementById("kpi-grad-count").textContent = `Số lượng tốt nghiệp: ${stats.graduated.toLocaleString()} SV`;

    document.getElementById("kpi-avg-grades").textContent = `${stats.avg_1st_sem_grade} / ${stats.avg_2nd_sem_grade}`;
    document.getElementById("kpi-approval-rate").textContent =
        `Tỷ lệ qua môn Kỳ 2: ${(stats.avg_2nd_sem_approval_rate * 100).toFixed(1)}%`;
}

function formatGroupLabel(dimensions, groupBy) {
    return groupBy
        .map((dim) => {
            const lbl = dimensions[`${dim}_label`];
            return lbl !== undefined ? lbl : `${dim}: ${dimensions[dim]}`;
        })
        .join(" • ");
}

function renderOlapCharts(groups, groupBy) {
    const topGroups = groups.slice(0, 12);
    const labels = topGroups.map((g) => {
        const full = formatGroupLabel(g.dimensions, groupBy);
        return full.length > 26 ? full.slice(0, 24) + "…" : full;
    });

    const dropouts = topGroups.map((g) => g.metrics.dropouts);
    const graduated = topGroups.map((g) => g.metrics.graduated);
    const enrolled = topGroups.map((g) => g.metrics.enrolled);
    const dropoutRates = topGroups.map((g) => +(g.metrics.dropout_rate * 100).toFixed(1));
    const approvalRates = topGroups.map((g) => +(g.metrics.avg_2nd_sem_approval_rate * 100).toFixed(1));

    const ctx1 = document.getElementById("olapOutcomeChart").getContext("2d");
    if (olapOutcomeChartInstance) olapOutcomeChartInstance.destroy();
    olapOutcomeChartInstance = new Chart(ctx1, {
        type: "bar",
        data: {
            labels,
            datasets: [
                { label: "Bỏ học (Dropout)", data: dropouts, backgroundColor: "#dc2626" },
                { label: "Tốt nghiệp (Graduate)", data: graduated, backgroundColor: "#16a34a" },
                { label: "Đang học (Enrolled)", data: enrolled, backgroundColor: "#3b82f6" },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: true, ticks: { font: { size: 11 } } },
                y: { stacked: true, beginAtZero: true },
            },
            plugins: { legend: { position: "top" } },
        },
    });

    const ctx2 = document.getElementById("olapRateChart").getContext("2d");
    if (olapRateChartInstance) olapRateChartInstance.destroy();
    olapRateChartInstance = new Chart(ctx2, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Tỷ lệ Bỏ học (%)",
                    data: dropoutRates,
                    backgroundColor: "rgba(220, 38, 38, 0.8)",
                    borderRadius: 4,
                },
                {
                    label: "Tỷ lệ Qua môn Kỳ 2 (%)",
                    data: approvalRates,
                    backgroundColor: "rgba(37, 99, 235, 0.75)",
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100, ticks: { callback: (v) => v + "%" } },
                x: { ticks: { font: { size: 11 } } },
            },
            plugins: { legend: { position: "top" } },
        },
    });
}

function renderOlapTable(groups, groupBy) {
    document.getElementById("olap-group-count").textContent = `${groups.length} nhóm`;
    const tbody = document.getElementById("olap-table-body");
    tbody.innerHTML = groups
        .map((g) => {
            const m = g.metrics;
            const label = formatGroupLabel(g.dimensions, groupBy);
            const dropPct = (m.dropout_rate * 100).toFixed(1);
            const dropColor =
                m.dropout_rate >= 0.45
                    ? "text-red-600 font-bold"
                    : m.dropout_rate >= 0.25
                    ? "text-amber-600 font-semibold"
                    : "text-emerald-600 font-semibold";
            return `
            <tr class="hover:bg-slate-50/90">
                <td class="py-2.5 px-4 font-medium text-slate-800">${label}</td>
                <td class="py-2.5 px-3 text-right font-semibold">${m.count}</td>
                <td class="py-2.5 px-3 text-right text-red-600">${m.dropouts}</td>
                <td class="py-2.5 px-3 text-right ${dropColor}">${dropPct}%</td>
                <td class="py-2.5 px-3 text-right text-emerald-600">${m.graduated}</td>
                <td class="py-2.5 px-3 text-right text-blue-600">${m.enrolled}</td>
                <td class="py-2.5 px-3 text-right">${m.avg_admission_grade}</td>
                <td class="py-2.5 px-3 text-right">${m.avg_1st_sem_grade}</td>
                <td class="py-2.5 px-3 text-right">${m.avg_2nd_sem_grade}</td>
                <td class="py-2.5 px-4 text-right font-medium">${(m.avg_2nd_sem_approval_rate * 100).toFixed(1)}%</td>
            </tr>`;
        })
        .join("");
}

// ============================================================================
// TAB 2: DSS PREDICTION & WHAT-IF SIMULATOR
// ============================================================================

function quickSelectStudent(studentId) {
    document.getElementById("dss-student-id").value = studentId;
    loadStudentIntoDss();
}

async function loadStudentIntoDss() {
    const sid = parseInt(document.getElementById("dss-student-id").value || "1", 10);
    try {
        const res = await fetch(`${API_BASE}/dss/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ student_id: sid }),
        });
        const json = await res.json();
        if (json.code !== "OK") return;

        const data = json.data;
        const p = data.student_profile;

        // Populate form fields with this student's DW record
        document.getElementById("dss-course").value = String(p.course_id || 9119);
        document.getElementById("dss-gender").value = String(p.gender_id ?? 1);
        document.getElementById("dss-age").value = p.age_at_enrollment ?? 19;
        document.getElementById("dss-adm-grade").value = p.admission_grade ?? 125;
        document.getElementById("dss-prev-grade").value = p.previous_qualification_grade ?? 125;
        document.getElementById("dss-tuition-ok").checked = Boolean(p.tuition_fees_up_to_date);
        document.getElementById("dss-debtor").checked = Boolean(p.debtor);
        document.getElementById("dss-scholarship").checked = Boolean(p.scholarship_holder);
        document.getElementById("dss-s1-enr").value = p.cu_1st_sem_enrolled ?? 6;
        document.getElementById("dss-s1-app").value = p.cu_1st_sem_approved ?? 5;
        document.getElementById("dss-s1-grade").value = p.cu_1st_sem_grade ?? 12.0;
        document.getElementById("dss-s2-enr").value = p.cu_2nd_sem_enrolled ?? 6;
        document.getElementById("dss-s2-app").value = p.cu_2nd_sem_approved ?? 5;
        document.getElementById("dss-s2-grade").value = p.cu_2nd_sem_grade ?? 12.0;

        renderDssPredictionResult(data);
    } catch (err) {
        console.error("Failed to load student into DSS:", err);
    }
}

async function runDssCustomPrediction() {
    const payload = {
        course_id: parseInt(document.getElementById("dss-course").value || "9119", 10),
        gender_id: parseInt(document.getElementById("dss-gender").value || "1", 10),
        age_at_enrollment: parseInt(document.getElementById("dss-age").value || "19", 10),
        admission_grade: parseFloat(document.getElementById("dss-adm-grade").value || "125"),
        previous_qualification_grade: parseFloat(document.getElementById("dss-prev-grade").value || "125"),
        tuition_fees_up_to_date: document.getElementById("dss-tuition-ok").checked,
        debtor: document.getElementById("dss-debtor").checked,
        scholarship_holder: document.getElementById("dss-scholarship").checked,
        cu_1st_sem_enrolled: parseInt(document.getElementById("dss-s1-enr").value || "0", 10),
        cu_1st_sem_approved: parseInt(document.getElementById("dss-s1-app").value || "0", 10),
        cu_1st_sem_grade: parseFloat(document.getElementById("dss-s1-grade").value || "0"),
        cu_1st_sem_evaluations: parseInt(document.getElementById("dss-s1-enr").value || "0", 10),
        cu_2nd_sem_enrolled: parseInt(document.getElementById("dss-s2-enr").value || "0", 10),
        cu_2nd_sem_approved: parseInt(document.getElementById("dss-s2-app").value || "0", 10),
        cu_2nd_sem_grade: parseFloat(document.getElementById("dss-s2-grade").value || "0"),
        cu_2nd_sem_evaluations: parseInt(document.getElementById("dss-s2-enr").value || "0", 10),
    };

    try {
        const res = await fetch(`${API_BASE}/dss/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const json = await res.json();
        if (json.code === "OK") {
            renderDssPredictionResult(json.data);
        }
    } catch (err) {
        console.error("Custom DSS Prediction Error:", err);
    }
}

function renderDssPredictionResult(data) {
    const pct = (data.dropout_probability * 100).toFixed(1);
    const badge = document.getElementById("dss-out-badge");
    const probEl = document.getElementById("dss-out-prob");
    const barEl = document.getElementById("dss-prob-bar");

    probEl.textContent = `${pct}%`;
    barEl.style.width = `${Math.min(100, Math.max(2, pct))}%`;

    badge.className = "text-xs font-bold px-2.5 py-0.5 rounded-full ";
    if (data.risk_level === "HIGH") {
        badge.classList.add("badge-high");
        badge.textContent = "NGUY CƠ CAO (HIGH)";
        probEl.className = "text-3xl font-extrabold text-red-600";
        barEl.className = "h-full bg-red-600 transition-all duration-500";
    } else if (data.risk_level === "MEDIUM") {
        badge.classList.add("badge-medium");
        badge.textContent = "NGUY CƠ TRUNG BÌNH (MEDIUM)";
        probEl.className = "text-3xl font-extrabold text-amber-600";
        barEl.className = "h-full bg-amber-500 transition-all duration-500";
    } else {
        badge.classList.add("badge-low");
        badge.textContent = "NGUY CƠ THẤP (LOW)";
        probEl.className = "text-3xl font-extrabold text-emerald-600";
        barEl.className = "h-full bg-emerald-600 transition-all duration-500";
    }

    const sidLabel = data.student_id ? `Sinh viên #${data.student_id} (${data.current_status})` : "Mô phỏng What-If tùy chỉnh";
    document.getElementById("dss-out-subtitle").textContent = `${sidLabel} - Ngành: ${data.course_label || "N/A"}`;

    // Risk factors
    const rfList = document.getElementById("dss-risk-factors");
    if (!data.risk_factors || data.risk_factors.length === 0) {
        rfList.innerHTML = `<li class="text-emerald-700 font-medium">Không phát hiện yếu tố rủi ro nghiêm trọng nào.</li>`;
    } else {
        rfList.innerHTML = data.risk_factors.map((f) => `<li>${f.detail}</li>`).join("");
    }

    // Recommendations
    const recList = document.getElementById("dss-recommendations");
    recList.innerHTML = (data.recommendations || []).map((r) => `<li>${r}</li>`).join("");

    // What-If Scenarios
    const scenarios = data.what_if_scenarios || [];
    const scGrid = document.getElementById("dss-scenarios-grid");
    scGrid.innerHTML = scenarios
        .map((sc) => {
            const newPct = (sc.new_dropout_probability * 100).toFixed(1);
            const deltaPct = (sc.probability_delta * 100).toFixed(1);
            const deltaStr = sc.probability_delta <= 0 ? `${deltaPct}%` : `+${deltaPct}%`;
            return `
            <div class="p-3.5 rounded-xl border border-slate-200 bg-slate-50/70 flex flex-col justify-between">
                <div>
                    <div class="text-xs font-bold text-slate-800">${sc.name}</div>
                    <div class="text-[11px] text-slate-500 mt-1">Rủi ro mới: <span class="font-bold text-slate-900">${newPct}%</span> (${sc.new_risk_level})</div>
                </div>
                <div class="mt-2 pt-2 border-t border-slate-200/80 flex items-center justify-between">
                    <span class="text-[11px] text-slate-500">Mức giảm rủi ro:</span>
                    <span class="text-xs font-extrabold text-emerald-600">${deltaStr}</span>
                </div>
            </div>`;
        })
        .join("");

    // What-if Chart
    const chartLabels = ["Hiện tại (Baseline)", ...scenarios.map((s) => s.name)];
    const chartValues = [
        +(data.dropout_probability * 100).toFixed(1),
        ...scenarios.map((s) => +(s.new_dropout_probability * 100).toFixed(1)),
    ];
    const chartColors = ["#dc2626", "#f59e0b", "#3b82f6", "#16a34a"];

    const ctx = document.getElementById("dssWhatIfChart").getContext("2d");
    if (dssWhatIfChartInstance) dssWhatIfChartInstance.destroy();
    dssWhatIfChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: "Xác suất Bỏ học (%)",
                    data: chartValues,
                    backgroundColor: chartColors.slice(0, chartValues.length),
                    borderRadius: 6,
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { beginAtZero: true, max: 100, ticks: { callback: (v) => v + "%" } },
            },
            plugins: { legend: { display: false } },
        },
    });
}

// ============================================================================
// TAB 3: EARLY WARNING SYSTEM
// ============================================================================

let ewCurrentPage = 1;
let ewTotalPages = 1;

function changeEwPage(delta) {
    const nextPage = ewCurrentPage + delta;
    if (nextPage < 1 || nextPage > ewTotalPages) return;
    ewCurrentPage = nextPage;
    loadEarlyWarningList();
}

async function loadEarlyWarningList() {
    const courseId = document.getElementById("ew-filter-course").value;
    const riskLevel = document.getElementById("ew-filter-risk").value;
    const limitVal = document.getElementById("ew-limit").value || "all";
    const pageSize = parseInt(document.getElementById("ew-page-size").value || "30", 10);

    const payload = {
        limit: limitVal === "all" ? 0 : parseInt(limitVal, 10),
        page: ewCurrentPage,
        page_size: pageSize,
    };
    if (courseId !== "") payload.course_id = parseInt(courseId, 10);
    if (riskLevel !== "") payload.risk_level = riskLevel;

    try {
        const res = await fetch(`${API_BASE}/dss/early-warning`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const json = await res.json();
        if (json.code !== "OK") return;

        const { summary, pagination, students } = json.data;
        document.getElementById("ew-total").textContent = summary.total_enrolled.toLocaleString();
        document.getElementById("ew-high").textContent = summary.HIGH.toLocaleString();
        document.getElementById("ew-medium").textContent = summary.MEDIUM.toLocaleString();
        document.getElementById("ew-low").textContent = summary.LOW.toLocaleString();

        if (pagination) {
            ewCurrentPage = pagination.page;
            ewTotalPages = pagination.total_pages;
            const startNum = pagination.total === 0 ? 0 : (pagination.page - 1) * pagination.page_size + 1;
            const endNum = Math.min(pagination.page * pagination.page_size, pagination.total);
            document.getElementById("ew-pagination-info").textContent =
                `Đang hiển thị ${startNum}-${endNum}/${pagination.total.toLocaleString()} sinh viên`;
            document.getElementById("ew-page-label").textContent = `Trang ${pagination.page} / ${pagination.total_pages}`;
            document.getElementById("ew-prev-btn").disabled = pagination.page <= 1;
            document.getElementById("ew-next-btn").disabled = pagination.page >= pagination.total_pages;
        }

        const tbody = document.getElementById("ew-table-body");
        tbody.innerHTML = students
            .map((s) => {
                const probPct = (s.dropout_probability * 100).toFixed(1);
                const badgeCls =
                    s.risk_level === "HIGH"
                        ? "badge-high"
                        : s.risk_level === "MEDIUM"
                        ? "badge-medium"
                        : "badge-low";
                const finTags = [];
                if (!s.tuition_fees_up_to_date) finTags.push(`<span class="text-red-600 font-semibold">Trễ HP</span>`);
                if (s.debtor) finTags.push(`<span class="text-red-600 font-semibold">Nợ HP</span>`);
                if (s.scholarship_holder) finTags.push(`<span class="text-emerald-600 font-semibold">Học bổng</span>`);
                const finHtml = finTags.length ? finTags.join(", ") : `<span class="text-slate-500">Bình thường</span>`;

                const factorsHtml = (s.top_risk_factors && s.top_risk_factors.length)
                    ? s.top_risk_factors.map((f) => `<div>• ${f}</div>`).join("")
                    : `<span class="text-slate-400">-</span>`;

                return `
                <tr class="hover:bg-slate-50 align-top">
                    <td class="py-2.5 px-4 font-bold text-slate-900">#${s.student_id}</td>
                    <td class="py-2.5 px-3 font-medium text-slate-800">${s.course_label}</td>
                    <td class="py-2.5 px-2 text-slate-600 whitespace-nowrap">${s.age_at_enrollment}/${s.gender}</td>
                    <td class="py-2.5 px-3 whitespace-nowrap">${finHtml}</td>
                    <td class="py-2.5 px-3 text-center whitespace-nowrap">${s.cu_1st_sem_approved}/${s.cu_1st_sem_enrolled} - ${s.cu_1st_sem_grade}</td>
                    <td class="py-2.5 px-3 text-center whitespace-nowrap">${s.cu_2nd_sem_approved}/${s.cu_2nd_sem_enrolled} - ${s.cu_2nd_sem_grade}</td>
                    <td class="py-2.5 px-3 text-center font-extrabold text-red-600 whitespace-nowrap">${probPct}%</td>
                    <td class="py-2.5 px-3 whitespace-nowrap"><span class="px-2 py-0.5 rounded-full text-[11px] font-bold ${badgeCls}">${s.risk_level}</span></td>
                    <td class="py-2.5 px-3 text-left text-slate-600 min-w-[260px] max-w-md whitespace-normal leading-relaxed space-y-0.5">${factorsHtml}</td>
                    <td class="py-2.5 px-4 text-center whitespace-nowrap">
                        <button onclick="inspectStudentInDss(${s.student_id})" class="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200">
                            Phân tích
                        </button>
                    </td>
                </tr>`;
            })
            .join("");
    } catch (err) {
        console.error("Early Warning Error:", err);
    }
}

function inspectStudentInDss(studentId) {
    document.getElementById("dss-student-id").value = studentId;
    switchTab("dss");
}

// ============================================================================
// TAB 4: DW MODEL METRICS, FEATURE IMPORTANCE & INSERT NEW RECORD
// ============================================================================

async function loadModelMetricsAndImportance(retrain = false) {
    try {
        const url = retrain ? `${API_BASE}/dss/retrain` : `${API_BASE}/dss/model-info`;
        const method = retrain ? "POST" : "GET";
        const res = await fetch(url, { method });
        const json = await res.json();
        if (json.code !== "OK") return;

        const { metrics, feature_importance } = json.data;
        document.getElementById("m-acc").textContent = `${(metrics.accuracy * 100).toFixed(2)}%`;
        document.getElementById("m-prec").textContent = `${(metrics.precision * 100).toFixed(2)}%`;
        document.getElementById("m-rec").textContent = `${(metrics.recall * 100).toFixed(2)}%`;
        document.getElementById("m-f1").textContent = `${(metrics.f1_score * 100).toFixed(2)}%`;
        document.getElementById("m-auc").textContent = `${(metrics.roc_auc * 100).toFixed(2)}%`;
        document.getElementById("m-split").textContent = `${metrics.train_size} / ${metrics.test_size}`;

        const cm = metrics.confusion_matrix;
        document.getElementById("cm-tp").textContent = cm.true_positive_dropout;
        document.getElementById("cm-tn").textContent = cm.true_negative_graduate;
        document.getElementById("cm-fp").textContent = cm.false_positive_dropout;
        document.getElementById("cm-fn").textContent = cm.false_negative_dropout;

        const topFeatures = feature_importance.slice(0, 10);
        const labels = topFeatures.map((f) => f.label.split(" (")[0]);
        const values = topFeatures.map((f) => f.importance_pct);
        const colors = topFeatures.map((f) =>
            f.direction === "increases_dropout_risk" ? "rgba(220, 38, 38, 0.82)" : "rgba(22, 163, 74, 0.82)"
        );

        const ctx = document.getElementById("featureImportanceChart").getContext("2d");
        if (featureImportanceChartInstance) featureImportanceChartInstance.destroy();
        featureImportanceChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [
                    {
                        label: "Tỷ trọng ảnh hưởng (%)",
                        data: values,
                        backgroundColor: colors,
                        borderRadius: 5,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: true, ticks: { callback: (v) => v + "%" } },
                },
                plugins: { legend: { display: false } },
            },
        });
    } catch (err) {
        console.error("Failed to load model metrics:", err);
    }
}

function retrainDssModel() {
    loadModelMetricsAndImportance(true);
}

async function insertNewStudentRecord() {
    const statusEl = document.getElementById("insert-status-msg");

    const enr1 = parseInt(document.getElementById("ins-enr1").value, 10);
    const enr2 = parseInt(document.getElementById("ins-enr2").value, 10);
    const app1 = parseInt(document.getElementById("ins-app1").value, 10);
    const app2 = parseInt(document.getElementById("ins-app2").value, 10);
    const appOrder = parseInt(document.getElementById("ins-app-order").value, 10);
    const age = parseInt(document.getElementById("ins-age").value, 10);
    const admGrade = parseFloat(document.getElementById("ins-adm").value);
    const prevGrade = parseFloat(document.getElementById("ins-prev-grade").value);
    const grade1 = parseFloat(document.getElementById("ins-grade1").value);
    const grade2 = parseFloat(document.getElementById("ins-grade2").value);
    const unemp = parseFloat(document.getElementById("ins-unemp").value);
    const infl = parseFloat(document.getElementById("ins-infl").value);
    const gdp = parseFloat(document.getElementById("ins-gdp").value);

    // Client-side required & range validation
    const errors = [];
    if ([enr1, enr2, app1, app2, appOrder, age, admGrade, prevGrade, grade1, grade2, unemp, infl, gdp].some(Number.isNaN)) {
        errors.push("Vui lòng nhập đầy đủ tất cả các trường thông số");
    }
    if (age < 16 || age > 100) errors.push("Tuổi nhập học phải từ 16 đến 100");
    if (appOrder < 1) errors.push("Thứ tự nguyện vọng phải >= 1");
    if (admGrade < 0 || admGrade > 200 || prevGrade < 0 || prevGrade > 200) errors.push("Điểm trúng tuyển/bằng trước phải từ 0 đến 200");
    if (grade1 < 0 || grade1 > 20 || grade2 < 0 || grade2 > 20) errors.push("Điểm TB Kỳ 1 & Kỳ 2 phải từ 0 đến 20");
    if (enr1 < 0 || enr2 < 0 || app1 < 0 || app2 < 0) errors.push("Số môn đăng ký và số môn đạt không được âm");
    if (unemp < -100 || unemp > 100 || infl < -100 || infl > 100 || gdp < -100 || gdp > 100) errors.push("Chỉ số kinh tế vĩ mô phải nằm trong khoảng từ -100 đến 100");

    if (errors.length > 0) {
        statusEl.textContent = `${errors[0]}`;
        statusEl.className = "text-xs font-semibold text-red-600";
        return;
    }

    statusEl.textContent = "Đang lưu vào Data Warehouse...";
    statusEl.className = "text-xs font-semibold text-blue-600";

    const record = {
        marital_status_id: parseInt(document.getElementById("ins-marital").value || "1", 10),
        application_mode_id: parseInt(document.getElementById("ins-app-mode").value || "1", 10),
        application_order: appOrder,
        course_id: parseInt(document.getElementById("ins-course").value || "9119", 10),
        daytime_evening_attendance_id: parseInt(document.getElementById("ins-attendance").value || "1", 10),
        previous_qualification_grade: prevGrade,
        nationality_id: parseInt(document.getElementById("ins-nationality").value || "1", 10),
        admission_grade: admGrade,
        gender_id: parseInt(document.getElementById("ins-gender").value || "1", 10),
        age_at_enrollment: age,
        displaced: document.getElementById("ins-displaced").checked,
        international: document.getElementById("ins-international").checked,
        educational_special_needs: document.getElementById("ins-special-needs").checked,
        debtor: document.getElementById("ins-debtor").checked,
        tuition_fees_up_to_date: document.getElementById("ins-tuition-ok").checked,
        scholarship_holder: document.getElementById("ins-scholarship").checked,
        unemployment_rate: unemp,
        inflation_rate: infl,
        gdp: gdp,
        cu_1st_sem_credited: 0,
        cu_1st_sem_enrolled: enr1,
        cu_1st_sem_evaluations: enr1,
        cu_1st_sem_approved: app1,
        cu_1st_sem_grade: grade1,
        cu_1st_sem_without_evaluations: 0,
        cu_2nd_sem_credited: 0,
        cu_2nd_sem_enrolled: enr2,
        cu_2nd_sem_evaluations: enr2,
        cu_2nd_sem_approved: app2,
        cu_2nd_sem_grade: grade2,
        cu_2nd_sem_without_evaluations: 0,
        target_outcome_id: parseInt(document.getElementById("ins-target").value || "2", 10),
    };

    try {
        const res = await fetch(`${API_BASE}/records`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify([record]),
        });
        const json = await res.json();
        if (json.code === "OK") {
            const newId = json.data?.[0]?.[0] || "mới";
            statusEl.textContent = `Đã thêm thành công Sinh viên #${newId} vào Kho dữ liệu!`;
            statusEl.className = "text-xs font-semibold text-emerald-600";
        } else {
            statusEl.textContent = `${json.message || "Không thể kết nối PostgreSQL"}`;
            statusEl.className = "text-xs font-semibold text-amber-600";
        }
    } catch (err) {
        statusEl.textContent = `Lỗi: ${err.message}`;
        statusEl.className = "text-xs font-semibold text-red-600";
    }
}

// Bootstrap on page load
window.addEventListener("DOMContentLoaded", async () => {
    await initMetadata();
    await runOlapQuery();
});
