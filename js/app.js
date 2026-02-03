/**
 * CDP Demo - Frontend Application
 */

// API Base URL (Vercel'de otomatik, local'de değiştir)
const API_BASE = window.location.hostname === 'localhost'
    ? 'http://localhost:3000/api'
    : '/api';

// Demo verileri (API çalışmazsa fallback)
const DEMO_DATA = {
    summary: {
        total_customers: 1000,
        total_revenue: 28500000,
        premium_customers: 153,
        app_users: 353
    },
    segments: [
        { key: "premium_fuel_lovers", name: "Premium Yakıt Severler", description: "Son 90 günde 3+ kez premium yakıt alan", count: 478, percentage: 47.8, total_revenue: 18955420, has_app_pct: 35.8 },
        { key: "high_value_customers", name: "Yüksek Değerli Müşteriler", description: "Son 90 günde 5000 TL üzeri harcama", count: 900, percentage: 90.0, total_revenue: 25790604, has_app_pct: 35.7 },
        { key: "app_active_users", name: "Aktif App Kullanıcıları", description: "App'i olan ve aktif kullanan", count: 322, percentage: 32.2, total_revenue: 8535360, has_app_pct: 100.0 },
        { key: "churn_risk", name: "Churn Riski", description: "Eskiden düzenli gelip artık gelmeyen", count: 1, percentage: 0.1, total_revenue: 0, has_app_pct: 100.0 },
        { key: "istanbul_premium", name: "İstanbul Premium", description: "İstanbul'daki premium müşteriler", count: 30, percentage: 3.0, total_revenue: 1925189, has_app_pct: 33.3 },
        { key: "market_shoppers", name: "Market Alışverişçileri", description: "Son 30 günde 3+ market alışverişi", count: 0, percentage: 0, total_revenue: 0, has_app_pct: 0 },
        { key: "email_reachable", name: "Email ile Ulaşılabilir", description: "Email opt-in vermiş premium", count: 106, percentage: 10.6, total_revenue: 6460362, has_app_pct: 34.9 }
    ],
    cities: {
        "İstanbul": 200,
        "Ankara": 200,
        "İzmir": 200,
        "Bursa": 200,
        "Antalya": 200
    }
};

// Format helpers
const formatNumber = (num) => num.toLocaleString('tr-TR');
const formatCurrency = (num) => '₺' + formatNumber(Math.round(num));
const formatPercent = (num) => '%' + num.toFixed(1);

// Chart instances
let segmentChart = null;
let cityChart = null;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    setupUploadForm();
    loadPlatformStatus();
});

// Load data from API or use demo
async function loadData() {
    let data = DEMO_DATA;

    try {
        const response = await fetch(`${API_BASE}/segments`);
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                data = {
                    summary: result.summary,
                    segments: result.segments,
                    cities: result.summary.cities
                };
            }
        }
    } catch (err) {
        console.log('API unavailable, using demo data');
    }

    updateKPIs(data.summary);
    updateSegmentsTable(data.segments);
    updateCharts(data);
    populateSegmentSelect(data.segments);
}

// Update KPI cards
function updateKPIs(summary) {
    document.getElementById('kpi-customers').textContent = formatNumber(summary.total_customers);
    document.getElementById('kpi-revenue').textContent = formatCurrency(summary.total_revenue);
    document.getElementById('kpi-premium').textContent = formatNumber(summary.premium_customers);
    document.getElementById('kpi-app').textContent = formatNumber(summary.app_users);
}

// Update segments table
function updateSegmentsTable(segments) {
    const tbody = document.getElementById('segmentsBody');
    tbody.innerHTML = segments.map(seg => `
        <tr class="fade-in">
            <td><strong>${seg.name}</strong></td>
            <td class="text-muted">${seg.description}</td>
            <td class="text-end">${formatNumber(seg.count)}</td>
            <td class="text-end">${formatPercent(seg.percentage)}</td>
            <td class="text-end">${formatCurrency(seg.total_revenue)}</td>
            <td class="text-end">${formatPercent(seg.has_app_pct)}</td>
        </tr>
    `).join('');
}

// Update charts
function updateCharts(data) {
    // Segment distribution pie chart
    const segmentCtx = document.getElementById('segmentChart').getContext('2d');

    if (segmentChart) segmentChart.destroy();

    // Sadece 0'dan büyük olanları göster
    const filteredSegments = data.segments.filter(s => s.count > 0);

    segmentChart = new Chart(segmentCtx, {
        type: 'doughnut',
        data: {
            labels: filteredSegments.map(s => s.name),
            datasets: [{
                data: filteredSegments.map(s => s.count),
                backgroundColor: [
                    '#0d6efd', '#198754', '#ffc107', '#dc3545',
                    '#0dcaf0', '#6f42c1', '#fd7e14'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                }
            },
            cutout: '60%'
        }
    });

    // City distribution bar chart
    const cityCtx = document.getElementById('cityChart').getContext('2d');

    if (cityChart) cityChart.destroy();

    const cities = data.cities || DEMO_DATA.cities;

    cityChart = new Chart(cityCtx, {
        type: 'bar',
        data: {
            labels: Object.keys(cities),
            datasets: [{
                label: 'Müşteri Sayısı',
                data: Object.values(cities),
                backgroundColor: '#0d6efd',
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Populate segment select for upload
function populateSegmentSelect(segments) {
    const select = document.getElementById('uploadSegment');
    select.innerHTML = '<option value="">Seçin...</option>' +
        segments.map(s => `<option value="${s.key}">${s.name} (${formatNumber(s.count)})</option>`).join('');
}

// Load platform status
async function loadPlatformStatus() {
    const container = document.getElementById('platformStatus');

    // Demo platform durumu
    const platforms = {
        meta: { name: "Meta", icon: "📘", configured: true },
        google: { name: "Google", icon: "🔍", configured: false },
        tiktok: { name: "TikTok", icon: "🎵", configured: true }
    };

    try {
        const response = await fetch(`${API_BASE}/config`);
        if (response.ok) {
            const result = await response.json();
            if (result.success) {
                Object.keys(result.platforms).forEach(key => {
                    platforms[key] = result.platforms[key];
                });
            }
        }
    } catch (err) {
        console.log('Config API unavailable, using demo status');
    }

    container.innerHTML = `
        <div class="col-12 mb-3">
            <h6 class="text-muted mb-3">Platform Durumları</h6>
        </div>
        ${Object.entries(platforms).map(([key, p]) => `
            <div class="col-md-4 mb-3">
                <div class="platform-card ${p.configured ? 'configured' : 'not-configured'}">
                    <div class="icon">${p.icon}</div>
                    <div class="name">${p.name}</div>
                    <div class="status">${p.configured ? '✅ Hazır' : '❌ Yapılandırılmamış'}</div>
                </div>
            </div>
        `).join('')}
    `;
}

// Setup upload form
function setupUploadForm() {
    const form = document.getElementById('uploadForm');
    const resultPre = document.getElementById('uploadResult');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const platform = document.getElementById('uploadPlatform').value;
        const segment = document.getElementById('uploadSegment').value;
        const dryRun = document.getElementById('dryRun').checked;

        if (!platform || !segment) {
            resultPre.textContent = '❌ Platform ve segment seçin!';
            return;
        }

        resultPre.textContent = '⏳ Yükleniyor...';

        try {
            const response = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform, segment_key: segment, dry_run: dryRun })
            });

            const result = await response.json();

            if (result.success) {
                resultPre.textContent = `✅ Upload Başarılı!

Platform: ${result.platform.toUpperCase()}
Segment: ${result.segment_key}
Audience ID: ${result.audience_id}
Audience Name: ${result.audience_name}
Yüklenen: ${result.uploaded_count} kullanıcı

${result.dry_run ? '⚠️ DRY-RUN: Gerçek upload yapılmadı' : ''}
${result.simulated ? '⚠️ SİMÜLASYON: Credential eksik' : ''}

${result.message}`;
            } else {
                resultPre.textContent = `❌ Hata: ${result.error}`;
            }
        } catch (err) {
            // Fallback - simüle et
            resultPre.textContent = `✅ Upload Simülasyonu Başarılı!

Platform: ${platform.toUpperCase()}
Segment: ${segment}
Audience ID: sim_${platform}_${Date.now()}
Yüklenen: (demo veri)

⚠️ Not: API bağlantısı yok, simülasyon gösteriliyor.
Gerçek upload için Vercel'e deploy edin.`;
        }
    });
}
