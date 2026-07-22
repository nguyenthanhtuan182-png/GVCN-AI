// =====================================
// GVCN AI - Version 2.0
// script.js
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("GVCN AI đã khởi động.");

    // ==============================
    // Tooltip Bootstrap
    // ==============================

    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );

    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ==============================
    // Popover Bootstrap
    // ==============================

    const popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );

    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // ==============================
    // Hiệu ứng Card
    // ==============================

    const cards = document.querySelectorAll(".card");

    cards.forEach(card => {

        card.addEventListener("mouseenter", () => {

            card.style.transform = "translateY(-5px)";

        });

        card.addEventListener("mouseleave", () => {

            card.style.transform = "translateY(0px)";

        });

    });

    // ==============================
    // Upload Box
    // ==============================

    const uploadBox = document.querySelector(".upload-box");

    if (uploadBox) {

        uploadBox.addEventListener("dragover", function (e) {

            e.preventDefault();

            uploadBox.style.borderColor = "#2563eb";

        });

        uploadBox.addEventListener("dragleave", function () {

            uploadBox.style.borderColor = "#cbd5e1";

        });

        uploadBox.addEventListener("drop", function () {

            uploadBox.style.borderColor = "#16a34a";

        });

    }

    // ==============================
    // Tìm kiếm bảng
    // ==============================

    const searchInput = document.getElementById("searchInput");

    if (searchInput) {

        searchInput.addEventListener("keyup", function () {

            let keyword = this.value.toLowerCase();

            let rows = document.querySelectorAll("tbody tr");

            rows.forEach(row => {

                row.style.display =
                    row.innerText.toLowerCase().includes(keyword)
                        ? ""
                        : "none";

            });

        });

    }

});


// =====================================
// Hàm thông báo
// =====================================

function showMessage(message) {

    alert(message);

}


// =====================================
// Xác nhận xóa
// =====================================

function confirmDelete(name) {

    return confirm("Bạn có chắc muốn xóa " + name + " ?");

}


// =====================================
// Loading
// =====================================

function showLoading() {

    console.log("Loading...");

}


// =====================================
// Hoàn thành
// =====================================

function hideLoading() {

    console.log("Done.");

}