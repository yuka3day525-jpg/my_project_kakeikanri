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

        options: {
            responsive: true,
            maintainAspectRatio: false,
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
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
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

        options: {
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
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
        options: {
            responsive: true,
            maintainAspectRatio: false,
        },
    }
);

// ========================================
// 世帯 / 個人 タブ切り替え
// ========================================

const tabButtons =
    document.querySelectorAll(".view-tab");

const tabPanels =
    document.querySelectorAll(".tab-panel");


tabButtons.forEach((button) => {

    button.addEventListener("click", () => {

        const selectedTab =
            button.dataset.tab;


        // ボタンのactiveを一旦全部消す
        tabButtons.forEach((tabButton) => {
            tabButton.classList.remove("active");
        });


        // パネルも全部非表示
        tabPanels.forEach((panel) => {
            panel.classList.remove("active");
        });


        // 押したボタンをactive
        button.classList.add("active");


        // 対応する画面だけ表示
        document
            .getElementById(
                `${selectedTab}-panel`
            )
            .classList.add("active");


        // 非表示だったChart.jsを再調整
        if (typeof Chart !== "undefined") {

            Object.values(
                Chart.instances
            ).forEach((chart) => {
                chart.resize();
            });

        }

    });

});


// ========================================
// カテゴリー記憶 全選択
// ========================================

const selectAllButtons =
    document.querySelectorAll(
        ".select-all-button"
    );


selectAllButtons.forEach((button) => {

    button.addEventListener("click", () => {

        // このボタンが入っているformだけ取得
        const form =
            button.closest("form");


        // selected_expenses か selected_banks
        const checkboxName =
            button.dataset.checkboxName;


        // このformの中だけから探す
        const checkboxes =
            form.querySelectorAll(
                `input[name="${checkboxName}"]`
            );


        // 全部チェックされているか
        const allChecked =
            Array.from(checkboxes)
                .every(
                    checkbox =>
                        checkbox.checked
                );


        // 全部チェック済みなら解除
        // そうでなければ全部選択
        checkboxes.forEach((checkbox) => {

            checkbox.checked =
                !allChecked;

        });


        // ボタン文字変更
        if (allChecked) {

            button.textContent =
                "すべて選択";

        } else {

            button.textContent =
                "すべて解除";

        }

    });

});