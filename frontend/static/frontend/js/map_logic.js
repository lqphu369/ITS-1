// ======================
// KHAI BÁO BIẾN TOÀN CỤC
// ======================
var map;
var userMarker;
var searchMarker;
var allMarkers = [];
var isUserAction = false;
var userLat = null;
var userLng = null;
var currentRoute = null;

const DEFAULT_LAT = 10.762622;
const DEFAULT_LNG = 106.660172;

// =================================
// 1. HÀM KHỞI TẠO BẢN ĐỒ (INIT MAP)
// =================================
function initMap(vehicleData) {
    map = L.map("map").setView([DEFAULT_LAT, DEFAULT_LNG], 12);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap",
    }).addTo(map);

    function createCarIcon(color) {
        var svgHtml = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="35" height="35">
            <path fill="${color}" stroke="white" stroke-width="20" d="M112 112c0-26.5 21.5-48 48-48h192c26.5 0 48 21.5 48 48v288c0 26.5-21.5 48-48 48H160c-26.5 0-48-21.5-48-48V112z"/>
            <path fill="rgba(255,255,255,0.5)" d="M160 128h192v64H160z"/><circle cx="120" cy="144" r="20" fill="#333"/><circle cx="392" cy="144" r="20" fill="#333"/><circle cx="120" cy="368" r="20" fill="#333"/><circle cx="392" cy="368" r="20" fill="#333"/></svg>`;
        return L.divIcon({
            className: "custom-car-icon",
            html: svgHtml,
            iconSize: [35, 35],
            iconAnchor: [17, 17],
            popupAnchor: [0, -10],
        });
    }

    const icons = {
        green: createCarIcon("#28a745"),
        blue: createCarIcon("#007bff"),
        red: createCarIcon("#dc3545"),
        yellow: createCarIcon("#ffc107"),
    };

    getUserLocation();

    // Vẽ các xe lên bản đồ
    vehicleData.forEach(function (xe) {
        xe.lat = xe.latitude || xe.lat;
        xe.lng = xe.longitude || xe.lng;

        // Nếu không có tọa độ thì bỏ qua 
        if (!xe.lat || !xe.lng) {
            console.warn("Bỏ qua xe do thiếu tọa độ:", xe.name);
            return;
        }

        // Chuẩn hóa trạng thái
        var rawStatus = xe.status ? xe.status.toString() : "available";
        var statusNormal = rawStatus.toLowerCase().trim().replace(/_/g, " ");
        var bookingUrl = "/thue-xe/" + xe.id + "/";

        // 1. CẤU HÌNH MẶC ĐỊNH: AVAILABLE (SẴN SÀNG)
        var statusConfig = {
            label: "Sẵn sàng",
            color: "#28a745",
            icon: icons.green,
            btnText: "THUÊ NGAY",
            btnColor: "#28a745",
            isBookable: true,
            bookingAction: "book_now",
            note: "✅ Xe đang rảnh, có thể nhận ngay!",
        };

        // 2. XỬ LÝ CÁC TRẠNG THÁI KHÁC
        if (statusNormal === "maintenance" || statusNormal === "bao tri") {
            statusConfig = {
                label: "Bảo trì",
                color: "#dc3545",
                icon: icons.red,
                btnText: "ĐANG BẢO TRÌ",
                btnColor: "#dc3545",
                isBookable: false, 
                bookingAction: null,
                note: "⚠️ Xe đang bảo dưỡng. Vui lòng chọn xe khác.",
            };
        } else if (
            statusNormal === "in operation" ||
            statusNormal === "dang hoat dong" ||
            statusNormal === "in use"
        ) {
            var returnTime = new Date();
            returnTime.setHours(returnTime.getHours() + 4);
            var timeStr = returnTime.getHours() + ":00 hôm nay";

            statusConfig = {
                label: "Đang hoạt động",
                color: "#007bff",
                icon: icons.blue,
                btnText: "ĐẶT LỊCH",
                btnColor: "#007bff", 
                isBookable: true, 
                bookingAction: "book_later",
                note: `🔵 Khách trả xe lúc <b>${timeStr}</b>. Bạn có thể đặt sau giờ này.`,
            };
        } else if (statusNormal === "booked" || statusNormal === "da dat") {
            var today = new Date();
            var endDate = new Date(today);
            endDate.setDate(today.getDate() + 3);
            var dateStr = `${today.getDate()}/${today.getMonth() + 1} - ${endDate.getDate()}/${endDate.getMonth() + 1}`;

            statusConfig = {
                label: "Đã có khách",
                color: "#ffc107",
                icon: icons.yellow,
                btnText: "CHỌN NGÀY KHÁC",
                btnColor: "#e0a800",
                isBookable: true,
                bookingAction: "book_alternative",
                note: `🟡 Kín lịch đến <b>${dateStr}</b>. Hãy chọn ngày khác.`,
            };
        }

        var safeName = xe.name.replace(/'/g, "\\'").replace(/"/g, "&quot;");

        // Tạo Marker
        var marker = L.marker([xe.lat, xe.lng], { icon: statusConfig.icon }).addTo(map);
        
        // Gán ID và Status vào marker để dùng cho chức năng Lọc (Filter)
        marker.id = xe.id;
        marker.status = xe.status;
        allMarkers.push(marker);

        // XỬ LÝ URL THÔNG MINH
        var smartBookingUrl = bookingUrl;
        if (statusConfig.bookingAction) {
            smartBookingUrl += "?action=" + statusConfig.bookingAction;
        }

        var popupContent = `
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; min-width: 250px; padding: 5px;">
            <h3 style="margin: 0 0 5px 0; font-size: 16px; color: #2c3e50; font-weight: 700;">${xe.name}</h3>
            <div style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span style="background: #fff; border: 1px solid ${statusConfig.color}; color: ${statusConfig.color}; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">
                    ${statusConfig.label}
                </span>
                <div style="font-size: 12px; color: #666;">
                    <span style="color: #f1c40f;">⭐</span> <b>${xe.rating || 5.0}</b> (${xe.trips || 0})
                </div>
            </div>
            <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid ${statusConfig.color};">
                <div style="color: #d63031; font-size: 18px; font-weight: bold; line-height: 1;">
                    ${parseInt(xe.price).toLocaleString("vi-VN")}đ 
                </div>
                <div style="font-size: 12px; color: #666; margin-top: 4px;">Giá thuê 1 ngày (24h)</div>
            </div>
            <div style="font-size: 12px; margin-bottom: 12px; padding: 5px; background: #f1f1f1; border-radius: 4px; color: #333;">
                ${statusConfig.note}
            </div>
            <div style="display: flex; gap: 5px;">
                <button onclick="openLocationModal('${safeName}', ${xe.lat}, ${xe.lng})" style="flex: 1; cursor:pointer; background: #fff; color: #17a2b8; border: 1px solid #17a2b8; padding: 8px 0; border-radius: 4px; font-weight: 600; font-size: 13px;">📍 Vị trí</button>
                <button onclick="openTermsModal('${safeName}', ${xe.price})" style="flex: 1; cursor:pointer; background: #6c757d; color: white; border: none; padding: 8px 0; border-radius: 4px; font-weight: 600; font-size: 13px;">📄 HĐ</button>
                
                <button onclick="${statusConfig.isBookable ? `window.location.href='${smartBookingUrl}'` : "return false;"}" 
                        style="flex: 2; cursor: ${statusConfig.isBookable ? "pointer" : "not-allowed"}; background: ${statusConfig.btnColor}; color: white; border: none; padding: 8px 0; border-radius: 4px; font-weight: 600; font-size: 13px;">
                    ${statusConfig.btnText}
                </button>
            </div>
        </div>
    `;
        marker.bindPopup(popupContent);
    });
}

// =========================
// 2. LẤY VỊ TRÍ NGƯỜI DÙNG
// =========================
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                userLat = position.coords.latitude;
                userLng = position.coords.longitude;

                var userIcon = L.icon({
                    iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png",
                    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41],
                });

                if (userMarker) {
                    userMarker.setLatLng([userLat, userLng]);
                } else {
                    userMarker = L.marker([userLat, userLng], { icon: userIcon })
                        .addTo(map)
                        .bindPopup("<b>Bạn đang ở đây!</b>")
                        .openPopup();
                }
                // Bay đến vị trí người dùng
                map.flyTo([userLat, userLng], 14, { duration: 1.5 });
            },
            function (error) {
                console.warn("Lỗi GPS:", error.message);
            }
        );
    }
}

// ===================================
// 3. TÍNH TOÁN LỘ TRÌNH & DỊCH THUẬT
// ===================================
window.calculateRoute = function (destLat, destLng) {
    if (userLat === null || userLng === null) {
        alert("Đang tìm vị trí của bạn... Vui lòng bật GPS và thử lại sau giây lát.");
        getUserLocation();
        return;
    }

    // Mở Modal Loading ngay lập tức
    var summaryBox = document.getElementById("route-summary");
    var instructionList = document.getElementById("route-instructions");
    if (summaryBox && instructionList) {
        summaryBox.innerHTML = '<div style="text-align:center; padding: 20px; color: #666;">⏳ Đang tìm đường...</div>';
        instructionList.innerHTML = "";
        openModal(); 
    }

    if (currentRoute) map.removeControl(currentRoute);

    currentRoute = L.Routing.control({
        waypoints: [L.latLng(userLat, userLng), L.latLng(destLat, destLng)],
        routeWhileDragging: false,
        showAlternatives: false,
        show: false,
        lineOptions: { styles: [{ color: "#007bff", opacity: 0.7, weight: 6 }] },
        createMarker: function () { return null; },
    })
    .on("routesfound", function (e) {
        var route = e.routes[0];
        var summary = route.summary;
        var distanceInKm = (summary.totalDistance / 1000).toFixed(2);
        var timeInMinutes = Math.round(summary.totalTime / 60);
        var shipCost = Math.round(distanceInKm * 30000).toLocaleString("vi-VN");

        var summaryHTML = `
        <div style="font-family: 'Segoe UI', sans-serif;">
            <div style="margin-bottom: 8px; display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 10px;">🏁</span> 
                <div><div style="font-size: 13px; color: #666;">Quãng đường</div><strong style="font-size: 16px;">${distanceInKm} km</strong></div>
            </div>
            <div style="margin-bottom: 8px; display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 10px;">⏳</span> 
                <div><div style="font-size: 13px; color: #666;">Thời gian</div><strong style="font-size: 16px;">${timeInMinutes} phút</strong></div>
            </div>
            <div style="margin-top: 12px; padding-top: 10px; border-top: 1px dashed #ccc; display: flex; align-items: center;">
                <span style="font-size: 20px; margin-right: 10px;">🚚</span> 
                <div><div style="font-size: 13px; color: #666;">Phí giao xe (30k/km)</div><strong style="font-size: 18px; color: #d63031;">${shipCost}đ</strong></div>
            </div>
        </div>
      `;
        document.getElementById("route-summary").innerHTML = summaryHTML;

        // BỘ DỊCH THUẬT
        var instructions = route.instructions;
        var listHTML = "";

        instructions.forEach(function (step) {
            var icon = "⬆️";
            var text = step.text;

            var translatedText = text
                .replace(/Enter (.*?) and take the (\d+)(?:st|nd|rd|th) exit/gi, "Vào $1 và đi theo lối ra thứ $2")
                .replace(/Enter (.*?) and take the exit/gi, "Vào $1 và đi theo lối ra")
                .replace(/Exit the (?:traffic circle|roundabout)/gi, "Ra khỏi vòng xoay")
                .replace(/Into the (?:traffic circle|roundabout)/gi, "Vào vòng xoay")
                .replace(/Make a U-turn/gi, "Quay đầu xe")
                .replace(/Make a (?:sharp|slight) right/gi, "Cua sang phải")
                .replace(/Make a (?:sharp|slight) left/gi, "Cua sang trái")
                .replace(/Make a right/gi, "Rẽ phải")
                .replace(/Make a left/gi, "Rẽ trái")
                .replace(/Turn left/gi, "Rẽ trái")
                .replace(/Turn right/gi, "Rẽ phải")
                .replace(/Keep left/gi, "Đi sang làn trái")
                .replace(/Keep right/gi, "Đi sang làn phải")
                .replace(/Go straight/gi, "Đi thẳng")
                .replace(/Take the ramp/gi, "Đi vào đường dẫn")
                .replace(/slightly left/gi, "chếch sang trái")
                .replace(/slightly right/gi, "chếch sang phải")
                .replace(/sharp left/gi, "ngoặt gấp sang trái")
                .replace(/sharp right/gi, "ngoặt gấp sang phải")
                .replace(/towards/gi, "về hướng")
                .replace(/stay on/gi, "tiếp tục đi trên")
                .replace(/ and /gi, " và ")
                .replace(/ onto /gi, " vào đường ")
                .replace(/ on /gi, " trên đường ")
                .replace(/ to /gi, " đến ")
                .replace(/ at /gi, " tại ")
                .replace(/ your /gi, " của bạn ")
                .replace(/\bNorth\b/gi, "Bắc")
                .replace(/\bSouth\b/gi, "Nam")
                .replace(/\bEast\b/gi, "Đông")
                .replace(/\bWest\b/gi, "Tây")
                .replace(/\bNortheast\b/gi, "Đông Bắc")
                .replace(/\bNorthwest\b/gi, "Tây Bắc")
                .replace(/\bSoutheast\b/gi, "Đông Nam")
                .replace(/\bSouthwest\b/gi, "Tây Nam")
                .replace(/Enter /gi, "Đi vào ")
                .replace(/Head /gi, "Đi về hướng ")
                .replace(/Continue/gi, "Tiếp tục đi")
                .replace(/Arrive at/gi, "Đến")
                .replace(/You have arrived/gi, "Bạn đã đến nơi")
                .replace(/destination/gi, "điểm đến")
                .replace(/\bright\b/gi, "bên phải")
                .replace(/\bleft\b/gi, "bên trái")
                .replace(/\s+/g, " ")
                .trim();

            if (text.match(/Left|left/)) icon = "⬅️";
            if (text.match(/Right|right/)) icon = "➡️";
            if (text.match(/U-turn/)) icon = "↩️";
            if (text.match(/roundabout|circle/)) icon = "🔄";
            if (text.match(/Arrive|destination/)) icon = "🎯";

            listHTML += `
            <li style="padding: 10px 0; border-bottom: 1px solid #eee; display: flex; align-items: start;">
                <span style="font-size: 20px; margin-right: 10px; min-width: 25px;">${icon}</span>
                <div><div style="font-weight: 500; color: #333;">${translatedText}</div><small style="color: #888;">${step.distance > 0 ? Math.round(step.distance) + " mét" : ""}</small></div>
            </li>
          `;
        });
        document.getElementById("route-instructions").innerHTML = listHTML;
    })
    .on("routingerror", function (e) {
        document.getElementById("route-summary").innerHTML = '<div style="color: red;">❌ Không tìm thấy đường đi.</div>';
    })
    .addTo(map);
};

// =================
// 4. QUẢN LÝ MODAL
// =================

// Modal Lộ trình
window.openModal = function () {
    var modal = document.getElementById("routeModal");
    if (modal) modal.style.display = "flex";
};

window.closeModal = function () {
    var modal = document.getElementById("routeModal");
    if (modal) modal.style.display = "none";
};

// Modal Hợp đồng
window.openTermsModal = function (name, price) {
    var modal = document.getElementById("termsModal");
    if (modal) {
        var nameEl = document.getElementById("term-car-name");
        var priceEl = document.getElementById("term-car-price");
        
        if (nameEl) nameEl.innerText = name;
        if (priceEl) {
            var priceFormatted = parseInt(price).toLocaleString("vi-VN");
            priceEl.innerText = priceFormatted + "đ/ngày";
        }
        
        modal.style.display = "flex";
    }
};

window.closeTermsModal = function () {
    var modal = document.getElementById("termsModal");
    if (modal) modal.style.display = "none";
};

// Modal Vị trí
window.openLocationModal = function (name, lat, lng) {
    var modal = document.getElementById("locationModal");
    if (modal) {
        var nameEl = document.getElementById("loc-car-name");
        if (nameEl) nameEl.innerText = name;

        var btnMap = document.getElementById("btn-view-map");
        if (btnMap) {
            btnMap.onclick = function () {
                modal.style.display = "none";
                if (map) map.flyTo([lat, lng], 18, { duration: 2.0 });
            };
        }

        var btnRoute = document.getElementById("btn-start-route");
        if (btnRoute) {
            btnRoute.onclick = function () {
                modal.style.display = "none";
                if (typeof calculateRoute === 'function') calculateRoute(lat, lng);
            };
        }

        modal.style.display = "flex";
    }
};

window.closeLocationModal = function () {
    var modal = document.getElementById("locationModal");
    if (modal) modal.style.display = "none";
};

// Xử lý đóng khi click ra ngoài
window.addEventListener("click", function (event) {
    if (event.target.classList.contains("modal-overlay") || 
        event.target.classList.contains("custom-modal")) {
        event.target.style.display = "none";
    }
});

// ===============================
// 5. HÀM TIỆN ÍCH (UTILITIES)
// ===============================

// Focus vào một xe cụ thể trên bản đồ
window.focusVehicle = function(lat, lng) {
    if (typeof map !== 'undefined' && lat && lng) { 
        map.flyTo([lat, lng], 17, { duration: 1.5 }); 
    } else {
        console.error("Lỗi tọa độ hoặc map chưa khởi tạo", lat, lng);
    }
};

// =====================================
// 6. XỬ LÝ SỰ KIỆN (TÌM KIẾM & BỘ LỌC)
// =====================================
document.addEventListener("DOMContentLoaded", function () {
    // ==================
    // A. KHỞI TẠO BẢN ĐỒ
    // ==================
    const dataScript = document.getElementById("vehicles-data");
    if (dataScript) {
        try {
            var vehicleData = JSON.parse(dataScript.textContent);
            if (typeof vehicleData === "string") vehicleData = JSON.parse(vehicleData);
            
            console.log("Dữ liệu xe chuẩn:", vehicleData);
            
            if (Array.isArray(vehicleData)) {
                initMap(vehicleData);
            } else {
                console.error("Lỗi: Dữ liệu xe không đúng định dạng danh sách.");
            }
        } catch (e) {
            console.error("Lỗi dữ liệu:", e);
        }
    } else {
        console.warn("Không tìm thấy dữ liệu xe (ID: vehicles-data)");
    }

    // ========================
    // B. TÌM KIẾM ĐỊA ĐIỂM
    // ========================
    const searchInput = document.getElementById("location-search");
    if (searchInput) {
        L.DomEvent.disableClickPropagation(searchInput);
        L.DomEvent.disableScrollPropagation(searchInput);

        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                const address = this.value;
                if (!address) return;

                fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`)
                    .then((res) => res.json())
                    .then((data) => {
                        if (data.length > 0) {
                            const lat = parseFloat(data[0].lat);
                            const lon = parseFloat(data[0].lon);

                            if (searchMarker) map.removeLayer(searchMarker);
                            searchMarker = L.marker([lat, lon])
                                .addTo(map)
                                .bindPopup(`<b>Vị trí tìm thấy:</b><br>${address}`)
                                .openPopup();

                            // Xóa marker khi đóng popup
                            searchMarker.on("popupclose", function () {
                                if (searchMarker) {
                                    map.removeLayer(searchMarker);
                                    searchMarker = null;
                                }
                            });

                            map.flyTo([lat, lon], 16, { duration: 1.5 });
                        } else {
                            alert("Không tìm thấy địa chỉ này!");
                        }
                    })
                    .catch((err) => console.error("Lỗi tìm kiếm:", err));
            }
        });
    }

    // ======================
    // C. BỘ LỌC XE (FILTER)
    // ======================
    
    // Lọc trên Bản đồ và Sidebar
    document.addEventListener("click", function (e) {
        const filterBtn = e.target.closest(".filter-btn");
        if (filterBtn) {
            e.preventDefault();
            const filterValue = filterBtn.getAttribute("data-filter").toLowerCase().trim();

            // Cập nhật màu nút (Active: Xanh, Inactive: Xám)
            document.querySelectorAll(".filter-btn").forEach((btn) => {
                btn.classList.remove("bg-primary", "text-white");
                btn.classList.add("bg-slate-100", "text-slate-600");
            });
            filterBtn.classList.remove("bg-slate-100", "text-slate-600");
            filterBtn.classList.add("bg-primary", "text-white");

            // Lọc Marker và Danh sách Sidebar
            allMarkers.forEach((marker) => {
                const vehicleStatus = (marker.status || "").toLowerCase().trim();
                const sidebarItem = document.querySelector(`.vehicle-item[data-id="${marker.id}"]`);

                if (filterValue === "all" || vehicleStatus === filterValue) {
                    if (!map.hasLayer(marker)) map.addLayer(marker);
                    if (sidebarItem) sidebarItem.style.display = "flex";
                } else {
                    if (map.hasLayer(marker)) map.removeLayer(marker);
                    if (sidebarItem) sidebarItem.style.display = "none";
                }
            });
            return;
        }

        const gpsBtn = e.target.closest("#locate-me-btn");
        if (gpsBtn) {
            isUserAction = true;
            getUserLocation();
        }
    });

    // Lọc trên Danh sách Xe (Vehicle Cards)
    const vehiclesDataEl = document.getElementById("vehicles-data");
    if (vehiclesDataEl) {
        const vehicles = JSON.parse(vehiclesDataEl.textContent);
        const vehicleCards = document.querySelectorAll(".vehicle-card");
        const filterButtons = document.querySelectorAll(".filter-btn");
        const vehicleCount = document.getElementById("vehicle-count");

        function applyFilter(filter) {
            let visibleCount = 0;

            vehicleCards.forEach((card, index) => {
                const vehicle = vehicles[index];
                if (!vehicle) return;

                const status = vehicle.status ? vehicle.status.toString() : "";
                const statusLower = status.toLowerCase();
                const filterLower = filter.toLowerCase();

                let show = false;

                if (filterLower === "all") {
                    show = true;
                } else if (filterLower === "available" && statusLower === "available") {
                    show = true;
                } else if (filterLower === "booked" && (statusLower === "booked" || statusLower === "in_use")) {
                    show = true;
                }

                card.style.display = show ? "block" : "none";
                if (show) visibleCount++;
            });

            if (vehicleCount) {
                vehicleCount.textContent = `${visibleCount} xe tìm thấy`;
            }
        }

        filterButtons.forEach(btn => {
            btn.addEventListener("click", function () {
                filterButtons.forEach(b => {
                    b.classList.remove("bg-primary", "text-white");
                    b.classList.add("bg-slate-100");
                });
                this.classList.add("bg-primary", "text-white");

                const filter = this.dataset.filter;
                applyFilter(filter);
            });
        });
    }

    // =========================
    // D. VÔ HIỆU HÓA SIDEBAR LEAFLET
    // =========================
    const sidebar = document.querySelector('.sidebar-container');
    if (sidebar && typeof L !== 'undefined') { 
        L.DomEvent.disableClickPropagation(sidebar); 
    }
});