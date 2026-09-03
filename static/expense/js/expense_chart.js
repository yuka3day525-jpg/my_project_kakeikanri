console.log("expense_chart.js 読み込み成功");

// 円グラフ
const chartLabels = JSON.parse(
    document.getElementById("chart-labels").textContent
);

const chartValues = JSON.parse(
    document.getElementById("chart-values").textContent
);

const ctx = document.getElementById("categoryChart");

new Chart(ctx, {
    type: "pie",

    data: {
        labels: chartLabels,

        datasets: [{
            data: chartValues,
        }]
    },
    
    options: {
    responsive: true,
    maintainAspectRatio: false,
    }
});

// ユーザー別
const ownerLabels = JSON.parse(
    document.getElementById("owner-labels").textContent
);

const ownerValues = JSON.parse(
    document.getElementById("owner-values").textContent
);

const ownerCtx = document.getElementById("ownerChart");

new Chart(ownerCtx, {
    type: "pie",

    data: {
        labels: ownerLabels,

        datasets: [{
            data: ownerValues,
        }]
    },

    options: {
    responsive: true,
    maintainAspectRatio: false,
    }
});

// --------------------
// 月ごとの支出推移
// --------------------
console.log(document.getElementById("monthly-labels"));
console.log(document.getElementById("monthly-values"));
console.log(document.getElementById("monthlyChart"));

const monthlyLabels = JSON.parse(
    document.getElementById("monthly-labels").textContent
);

const monthlyValues = JSON.parse(
    document.getElementById("monthly-values").textContent
);

const monthlyCtx = document.getElementById("monthlyChart");

new Chart(monthlyCtx, {
    type: "line",

    data: {
        labels: monthlyLabels,

        datasets: [{
            label: "月ごとの支出",
            data: monthlyValues,
        }]
    },

    options: {
    responsive: true,
    maintainAspectRatio: false,
    }
});