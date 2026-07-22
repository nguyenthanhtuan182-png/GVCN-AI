document.addEventListener("DOMContentLoaded", function () {

    const select = document.querySelector('select[name="data_type"]');
    const downloadBtn = document.getElementById("downloadTemplate");
    const guide = document.getElementById("requiredColumns");

    const templates = {

        students: {
            file: "/download-template/students",
            columns: [
                "Họ tên",
                "Ngày sinh",
                "Giới tính",
                "Lớp",
                "Địa chỉ",
                "SĐT PH"
            ]
        },

        academic: {
            file: "/download-template/academic",
            columns: [
                "Mã HS",
                "Họ tên",
                "Lớp",
                "Toán",
                "Ngữ văn",
                "Tiếng Anh",
                "Điểm TB",
                "Học lực"
            ]
        },

        attendance: {
            file: "/download-template/attendance",
            columns: [
                "Mã HS",
                "Họ tên",
                "Lớp",
                "Ngày nghỉ",
                "Có phép",
                "Không phép"
            ]
        },

        conduct: {
            file: "/download-template/conduct",
            columns: [
                "Mã HS",
                "Họ tên",
                "Lớp",
                "Hạnh kiểm",
                "Vi phạm",
                "Ghi chú"
            ]
        },

        parents: {
            file: "/download-template/parents",
            columns: [
                "Họ tên HS",
                "Họ tên cha",
                "SĐT cha",
                "Họ tên mẹ",
                "SĐT mẹ",
                "Địa chỉ"
            ]
        },

        survey: {
            file: "/download-template/survey",
            columns: [
                "Họ tên",
                "Lớp",
                "Nội dung khảo sát"
            ]
        },

        other: {
            file: "#",
            columns: [
                "Không có file mẫu"
            ]
        }

    };

    function updateGuide() {

        const type = select.value;
        const data = templates[type];

        downloadBtn.href = data.file;

        guide.innerHTML = "";

        const title = document.createElement("h6");
        title.className = "mb-3";
        title.innerHTML = '<i class="bi bi-list-check"></i> Các cột bắt buộc';

        guide.appendChild(title);

        const box = document.createElement("div");
        box.className = "d-flex flex-wrap gap-2";

        data.columns.forEach(function (item) {

            const badge = document.createElement("span");

            badge.className =
                "badge rounded-pill text-bg-primary px-3 py-2";

            badge.style.fontSize = "14px";

            badge.innerHTML = item;

            box.appendChild(badge);

        });

        guide.appendChild(box);

    }

    updateGuide();

    select.addEventListener("change", updateGuide);

});