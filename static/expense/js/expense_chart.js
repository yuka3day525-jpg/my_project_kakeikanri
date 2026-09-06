console.log("expense_chart.js 読み込み成功");

//カテゴリー別支出、円グラフ
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

// 細かいカテゴリの横棒グラフ（世帯）
const detailLabels = JSON.parse(
    document.getElementById("detail-chart-labels").textContent
);

const detailValues = JSON.parse(
    document.getElementById("detail-chart-values").textContent
);

const detailCtx = document.getElementById("detailCategoryChart");

new Chart(detailCtx, {
    type: "bar",
    data: {
        labels: detailLabels,
        datasets: [{
            label: "カテゴリ別支出",
            data: detailValues,
        }]
    },
    options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,

        layout: {
            padding: {
                left: 30
            }
        },

        scales: {
            y: {
                ticks: {
                    font: {
                        size: 11
                    }
                }
            }
        }
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


//  世帯支出推移
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
            label: "世帯支出推移",
            data: monthlyValues,
        }]
    },

    options: {
    responsive: true,
    maintainAspectRatio: false,
    }
});


//  食費推移
const foodLabels = JSON.parse(
    document.getElementById("food-monthly-labels").textContent
);

const foodOutValues = JSON.parse(
    document.getElementById("food-out-values").textContent
);

const foodHomeValues = JSON.parse(
    document.getElementById("food-home-values").textContent
);

const foodCtx = document.getElementById("foodChart");

new Chart(foodCtx, {
    type: "line",

    data: {
        labels: foodLabels,

        datasets: [
            {
                label: "外食",
                data: foodOutValues,
                tension: 0.3,
            },
            {
                label: "自炊",
                data: foodHomeValues,
                tension: 0.3,
            }
        ]
    },

    options: {
        responsive: true,

        plugins: {
            title: {
                display: true,
                text: "食費の月別推移"
            }
        },

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// 評価損益
const profitLabels = JSON.parse(
    document.getElementById("profit-labels").textContent
);

const profitIncomeValues = JSON.parse(
    document.getElementById("profit-income-values").textContent
);

const profitExpenseValues = JSON.parse(
    document.getElementById("profit-expense-values").textContent
);

const profitValues = JSON.parse(
    document.getElementById("profit-values").textContent
);

const profitCtx = document.getElementById("profitChart");

new Chart(profitCtx, {
    type: "bar",

    data: {
        labels: profitLabels,
        datasets: [
            {
                label: "収入",
                data: profitIncomeValues,
            },
            {
                label: "支出",
                data: profitExpenseValues,
            },
            {
                label: "損益",
                data: profitValues,
                type: "line",
            }
        ]
    },

    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});