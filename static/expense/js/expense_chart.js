// ===============================
// 世帯用
// ===============================

// カテゴリー別支出 円グラフ
const categoryLabels = JSON.parse(
    document.getElementById("chart-labels").textContent
);

const categoryValues = JSON.parse(
    document.getElementById("chart-values").textContent
);

new Chart(
    document.getElementById("categoryChart"),
    {
        type: "pie",

        data: {
            labels: categoryLabels,

            datasets: [
                {
                    data: categoryValues,
                }
            ],
        },
    }
);


// 細かいカテゴリ 横棒グラフ
const detailCategoryLabels = JSON.parse(
    document.getElementById(
        "detail-chart-labels"
    ).textContent
);

const detailCategoryValues = JSON.parse(
    document.getElementById(
        "detail-chart-values"
    ).textContent
);

new Chart(
    document.getElementById(
        "detailCategoryChart"
    ),
    {
        type: "bar",

        data: {
            labels: detailCategoryLabels,

            datasets: [
                {
                    label: "支出",
                    data: detailCategoryValues,
                }
            ],
        },

        options: {
            indexAxis: "y",
        },
    }
);


// 月別支出
const monthlyLabels = JSON.parse(
    document.getElementById(
        "monthly-labels"
    ).textContent
);

const monthlyValues = JSON.parse(
    document.getElementById(
        "monthly-values"
    ).textContent
);

new Chart(
    document.getElementById("monthlyChart"),
    {
        type: "line",

        data: {
            labels: monthlyLabels,

            datasets: [
                {
                    label: "月別支出",
                    data: monthlyValues,
                }
            ],
        },
    }
);


// 食費推移
const foodMonthlyLabels = JSON.parse(
    document.getElementById(
        "food-monthly-labels"
    ).textContent
);

const foodOutValues = JSON.parse(
    document.getElementById(
        "food-out-values"
    ).textContent
);

const foodHomeValues = JSON.parse(
    document.getElementById(
        "food-home-values"
    ).textContent
);

new Chart(
    document.getElementById("foodChart"),
    {
        type: "line",

        data: {
            labels: foodMonthlyLabels,

            datasets: [
                {
                    label: "外食",
                    data: foodOutValues,
                },

                {
                    label: "自炊",
                    data: foodHomeValues,
                }
            ],
        },
    }
);


// 利用者別
const ownerLabels = JSON.parse(
    document.getElementById(
        "owner-labels"
    ).textContent
);

const ownerValues = JSON.parse(
    document.getElementById(
        "owner-values"
    ).textContent
);

new Chart(
    document.getElementById("ownerChart"),
    {
        type: "pie",

        data: {
            labels: ownerLabels,

            datasets: [
                {
                    data: ownerValues,
                }
            ],
        },
    }
);


// 月間収支
const profitLabels = JSON.parse(
    document.getElementById(
        "profit-labels"
    ).textContent
);

const profitIncomeValues = JSON.parse(
    document.getElementById(
        "profit-income-values"
    ).textContent
);

const profitExpenseValues = JSON.parse(
    document.getElementById(
        "profit-expense-values"
    ).textContent
);

const profitValues = JSON.parse(
    document.getElementById(
        "profit-values"
    ).textContent
);

new Chart(
    document.getElementById("profitChart"),
    {
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
                    label: "収支",
                    data: profitValues,
                    type: "line",
                }
            ],
        },
    }
);


// ===============================
// 個人用
// ===============================

// 個人 カテゴリー別支出
const myCategoryLabels = JSON.parse(
    document.getElementById(
        "my-chart-labels"
    ).textContent
);

const myCategoryValues = JSON.parse(
    document.getElementById(
        "my-chart-values"
    ).textContent
);

new Chart(
    document.getElementById(
        "myCategoryChart"
    ),
    {
        type: "pie",

        data: {
            labels: myCategoryLabels,

            datasets: [
                {
                    data: myCategoryValues,
                }
            ],
        },
    }
);


// 個人 細かいカテゴリー
const myDetailCategoryLabels = JSON.parse(
    document.getElementById(
        "my-detail-chart-labels"
    ).textContent
);

const myDetailCategoryValues = JSON.parse(
    document.getElementById(
        "my-detail-chart-values"
    ).textContent
);

new Chart(
    document.getElementById(
        "myDetailCategoryChart"
    ),
    {
        type: "bar",

        data: {
            labels: myDetailCategoryLabels,

            datasets: [
                {
                    label: "支出",
                    data: myDetailCategoryValues,
                }
            ],
        },

        options: {
            indexAxis: "y",
        },
    }
);


// 個人 月別支出
const myMonthlyLabels = JSON.parse(
    document.getElementById(
        "my-monthly-labels"
    ).textContent
);

const myMonthlyValues = JSON.parse(
    document.getElementById(
        "my-monthly-values"
    ).textContent
);

new Chart(
    document.getElementById(
        "myMonthlyChart"
    ),
    {
        type: "line",

        data: {
            labels: myMonthlyLabels,

            datasets: [
                {
                    label: "月別支出",
                    data: myMonthlyValues,
                }
            ],
        },
    }
);


// 個人 食費推移
const myFoodMonthlyLabels = JSON.parse(
    document.getElementById(
        "my-food-monthly-labels"
    ).textContent
);

const myFoodOutValues = JSON.parse(
    document.getElementById(
        "my-food-out-values"
    ).textContent
);

const myFoodHomeValues = JSON.parse(
    document.getElementById(
        "my-food-home-values"
    ).textContent
);

new Chart(
    document.getElementById(
        "myFoodChart"
    ),
    {
        type: "line",

        data: {
            labels: myFoodMonthlyLabels,

            datasets: [
                {
                    label: "外食",
                    data: myFoodOutValues,
                },

                {
                    label: "自炊",
                    data: myFoodHomeValues,
                }
            ],
        },
    }
);


// 個人 月間収支
const myProfitLabels = JSON.parse(
    document.getElementById(
        "my-profit-labels"
    ).textContent
);

const myProfitIncomeValues = JSON.parse(
    document.getElementById(
        "my-profit-income-values"
    ).textContent
);

const myProfitExpenseValues = JSON.parse(
    document.getElementById(
        "my-profit-expense-values"
    ).textContent
);

const myProfitValues = JSON.parse(
    document.getElementById(
        "my-profit-values"
    ).textContent
);

new Chart(
    document.getElementById(
        "myProfitChart"
    ),
    {
        type: "bar",

        data: {
            labels: myProfitLabels,

            datasets: [
                {
                    label: "収入",
                    data: myProfitIncomeValues,
                },

                {
                    label: "支出",
                    data: myProfitExpenseValues,
                },

                {
                    label: "収支",
                    data: myProfitValues,
                    type: "line",
                }
            ],
        },
    }
);