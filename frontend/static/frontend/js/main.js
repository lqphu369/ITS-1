    document.addEventListener('DOMContentLoaded', function () {

        // 1. File Upload Name Display (Register Page)
        const fileInput = document.getElementById('license-upload');
        const fileNameDisplay = document.getElementById('file-name');

        if (fileInput && fileNameDisplay) {
            fileInput.addEventListener('change', function (e) {
                if (e.target.files.length > 0) {
                    fileNameDisplay.textContent = e.target.files[0].name;
                    fileNameDisplay.classList.remove('hidden');
                }
            });
        }

        // 2. Dynamic Price Calculation (Vehicle Detail Page)
        // Lưu ý: Cần thêm id="calc-total" vào chỗ hiển thị giá ở detail.html nếu muốn hiển thị realtime
        // Tuy nhiên, mã hiện tại của bạn dùng form POST sang trang payment, nên logic tính toán chính nằm ở backend
        // hoặc trang payment.html. Dưới đây là đoạn script hỗ trợ trải nghiệm người dùng.

        // 3. Auto-hide Messages
        const alerts = document.querySelectorAll('.alert-dismissible'); // Nếu dùng class này
        if (alerts.length > 0) {
            setTimeout(() => {
                alerts.forEach(el => {
                    el.style.transition = "opacity 0.5s ease";
                    el.style.opacity = 0;
                    setTimeout(() => el.remove(), 500);
                });
            }, 5000);
        }
    });