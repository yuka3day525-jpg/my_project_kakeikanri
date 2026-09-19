const menuButton =
    document.getElementById("menuButton");

const sideMenu =
    document.getElementById("sideMenu");

const menuClose =
    document.getElementById("menuClose");

const menuOverlay =
    document.getElementById("menuOverlay");


function openMenu() {
    sideMenu.classList.add("open");
    menuOverlay.classList.add("open");
}


function closeMenu() {
    sideMenu.classList.remove("open");
    menuOverlay.classList.remove("open");
}


menuButton.addEventListener(
    "click",
    openMenu
);


menuClose.addEventListener(
    "click",
    closeMenu
);


menuOverlay.addEventListener(
    "click",
    closeMenu
);

// ========================================
// CSVアップロード中の表示
// ========================================

const csvUploadForm =
    document.getElementById("csvUploadForm");

if (csvUploadForm) {

    const uploadButton =
        document.getElementById("uploadButton");

    const uploadLoading =
        document.getElementById("uploadLoading");

    csvUploadForm.addEventListener("submit", () => {

        // 読み込み中の表示を出す
        uploadLoading.hidden = false;

        // ボタンの文字を変更
        uploadButton.textContent =
            "取り込み中...";

        // 二重送信を防ぐ
        uploadButton.disabled = true;

    });

}
