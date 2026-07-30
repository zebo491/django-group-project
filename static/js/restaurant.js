(function () {
    "use strict";

    // ============ CART STATE (in-memory, resets on page reload) ============
    // Each entry: {id, type, name, price, image, qty}
    var cart = [];

    function findInCart(id, type) {
        for (var i = 0; i < cart.length; i++) {
            if (cart[i].id == id && cart[i].type === type) return i;
        }
        return -1;
    }

    function addToCart(item, qty) {
        qty = qty || 1;
        var idx = findInCart(item.id, item.type);
        if (idx === -1) {
            item.qty = qty;
            cart.push(item);
        } else {
            cart[idx].qty += qty;
        }
        renderCart();
    }

    function changeQty(id, type, delta) {
        var idx = findInCart(id, type);
        if (idx === -1) return;
        cart[idx].qty += delta;
        if (cart[idx].qty <= 0) {
            cart.splice(idx, 1);
        }
        renderCart();
    }

    function removeFromCart(id, type) {
        var idx = findInCart(id, type);
        if (idx !== -1) {
            cart.splice(idx, 1);
            renderCart();
        }
    }

    function cartTotal() {
        var total = 0;
        cart.forEach(function (item) {
            var price = parseFloat(item.price) || 0;
            total += price * item.qty;
        });
        return total.toFixed(2);
    }

    function renderCart() {
        var countEl = document.getElementById("cart-count");
        var totalQty = cart.reduce(function (sum, i) { return sum + i.qty; }, 0);
        if (countEl) countEl.textContent = totalQty;

        renderCartInto("cart-items-list");
        renderCartInto("cart-sidebar-list");
    }

    function renderCartInto(containerId) {
        var container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = "";

        if (cart.length === 0) {
            var empty = document.createElement("li");
            empty.className = "cart-empty";
            empty.textContent = "Hali hech narsa tanlanmagan";
            container.appendChild(empty);
            return;
        }

        cart.forEach(function (item) {
            var li = document.createElement("li");
            li.className = "cart-item";
            var lineTotal = item.price ? (parseFloat(item.price) * item.qty).toFixed(2) : "";
            li.innerHTML =
                '<img src="' + item.image + '" alt="' + item.name + '">' +
                '<span class="cart-item-name">' + item.name + "</span>" +
                '<span class="cart-item-qty">' +
                    '<button type="button" class="qty-btn-small qty-minus" data-id="' + item.id + '" data-type="' + item.type + '">-</button>' +
                    '<span class="qty-num">' + item.qty + "</span>" +
                    '<button type="button" class="qty-btn-small qty-plus" data-id="' + item.id + '" data-type="' + item.type + '">+</button>' +
                "</span>" +
                (lineTotal ? '<span class="cart-item-price">$' + lineTotal + "</span>" : "") +
                '<span class="cart-item-remove" data-id="' + item.id + '" data-type="' + item.type + '">&times;</span>';
            container.appendChild(li);
        });

        // Jami summa qatori
        var totalLi = document.createElement("li");
        totalLi.className = "cart-total-line";
        totalLi.innerHTML = "<strong>Jami: $" + cartTotal() + "</strong>";
        container.appendChild(totalLi);

        container.querySelectorAll(".cart-item-remove").forEach(function (btn) {
            btn.addEventListener("click", function () {
                removeFromCart(this.getAttribute("data-id"), this.getAttribute("data-type"));
            });
        });
        container.querySelectorAll(".qty-minus").forEach(function (btn) {
            btn.addEventListener("click", function () {
                changeQty(this.getAttribute("data-id"), this.getAttribute("data-type"), -1);
            });
        });
        container.querySelectorAll(".qty-plus").forEach(function (btn) {
            btn.addEventListener("click", function () {
                changeQty(this.getAttribute("data-id"), this.getAttribute("data-type"), 1);
            });
        });
    }

    function cartSummaryText() {
        if (cart.length === 0) return "";
        return cart.map(function (item) {
            return item.qty + "x " + item.name;
        }).join(", ");
    }

    // ============ ABOUT US: BATAFSIL TOGGLE ============
    var aboutToggleBtn = document.getElementById("about-toggle-btn");
    var aboutShort = document.getElementById("about-short");
    var aboutFull = document.getElementById("about-full");

    if (aboutToggleBtn && aboutShort && aboutFull) {
        aboutToggleBtn.addEventListener("click", function () {
            var isFullOpen = aboutFull.style.display !== "none";
            if (isFullOpen) {
                aboutFull.style.display = "none";
                aboutShort.style.display = "block";
                aboutToggleBtn.textContent = "Batafsil";
            } else {
                aboutFull.style.display = "block";
                aboutShort.style.display = "none";
                aboutToggleBtn.textContent = "Qisqartirish";
            }
        });
    }

    // ============ ITEM DETAIL MODAL (custom, not Bootstrap) ============
    var modal = document.getElementById("itemModal");
    var modalImage = document.getElementById("itemModal-image");
    var modalName = document.getElementById("itemModal-name");
    var modalPrice = document.getElementById("itemModal-price");
    var modalDesc = document.getElementById("itemModal-desc");
    var modalAddBtn = document.getElementById("itemModal-add-btn");
    var qtyValueEl = document.getElementById("itemModal-qty-value");
    var qtyMinusBtn = document.getElementById("itemModal-qty-minus");
    var qtyPlusBtn = document.getElementById("itemModal-qty-plus");
    var currentModalItem = null;
    var currentModalQty = 1;

    function openModalFromElement(el) {
        var data = {
            id: el.getAttribute("data-id"),
            type: el.getAttribute("data-type"),
            name: el.getAttribute("data-name"),
            price: el.getAttribute("data-price"),
            image: el.getAttribute("data-image"),
            desc: el.getAttribute("data-desc"),
        };
        currentModalItem = data;
        currentModalQty = 1;
        if (qtyValueEl) qtyValueEl.textContent = "1";
        if (modalImage) modalImage.src = data.image;
        if (modalName) modalName.textContent = data.name;
        if (modalPrice) modalPrice.textContent = data.price ? "$" + data.price : "";
        if (modalDesc) modalDesc.textContent = data.desc;
        if (modal) modal.classList.add("open");
    }

    function closeModal() {
        if (modal) modal.classList.remove("open");
        currentModalItem = null;
    }

    document.querySelectorAll("#portfolio .item, .beer-card-inner").forEach(function (el) {
        el.addEventListener("click", function () {
            openModalFromElement(this);
        });
    });

    var modalCloseBtn = document.getElementById("itemModal-close");
    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
    if (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) closeModal();
        });
    }
    if (qtyMinusBtn) {
        qtyMinusBtn.addEventListener("click", function () {
            if (currentModalQty > 1) {
                currentModalQty -= 1;
                qtyValueEl.textContent = currentModalQty;
            }
        });
    }
    if (qtyPlusBtn) {
        qtyPlusBtn.addEventListener("click", function () {
            currentModalQty += 1;
            qtyValueEl.textContent = currentModalQty;
        });
    }
    if (modalAddBtn) {
        modalAddBtn.addEventListener("click", function () {
            if (currentModalItem) {
                addToCart(currentModalItem, currentModalQty);
                closeModal();
            }
        });
    }

    // ============ BREAKFAST CATEGORY EXPAND ============
    var breakfastCategoryCards = document.querySelectorAll(".breakfast-cat-card");
    var breakfastPanel = document.getElementById("breakfast-items-panel");
    var breakfastTitle = document.getElementById("breakfast-items-title");
    var breakfastList = document.getElementById("breakfast-items-list");

    breakfastCategoryCards.forEach(function (card) {
        card.addEventListener("click", function () {
            var catId = this.getAttribute("data-cat-id");
            var data = window.BREAKFAST_DATA ? window.BREAKFAST_DATA[catId] : null;
            if (!data || !breakfastPanel) return;

            breakfastTitle.textContent = data.title;
            breakfastList.innerHTML = "";

            if (!data.items || data.items.length === 0) {
                breakfastList.innerHTML = '<p class="text-center">Bu kategoriyada hozircha taom qoshilmagan.</p>';
            }

            data.items.forEach(function (item) {
                var col = document.createElement("div");
                col.className = "col-md-3 col-sm-6 breakfast-item-card";
                col.innerHTML =
                    '<div class="breakfast-item-inner hover-zoom">' +
                    '<img src="' + item.image + '" alt="' + item.name + '">' +
                    "<h4>" + item.name + "</h4>" +
                    '<p class="price-tag">$' + item.price + "</p>" +
                    '<button class="btn-readmore breakfast-add-btn">Qoshish</button>' +
                    "</div>";

                col.querySelector(".breakfast-add-btn").addEventListener("click", function () {
                    addToCart({
                        id: item.id,
                        type: "breakfast",
                        name: item.name,
                        price: item.price,
                        image: item.image,
                    }, 1);
                });

                breakfastList.appendChild(col);
            });

            breakfastPanel.style.display = "block";
            breakfastPanel.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });

    // ============ CART SIDEBAR TOGGLE ============
    var cartToggle = document.getElementById("cart-toggle");
    var cartSidebar = document.getElementById("cart-sidebar");
    var cartSidebarClose = document.getElementById("cart-sidebar-close");
    var cartGoToReservation = document.getElementById("cart-go-to-reservation");

    if (cartToggle) {
        cartToggle.addEventListener("click", function (e) {
            e.preventDefault();
            if (cartSidebar) cartSidebar.classList.add("open");
        });
    }
    if (cartSidebarClose) {
        cartSidebarClose.addEventListener("click", function () {
            cartSidebar.classList.remove("open");
        });
    }
    if (cartGoToReservation) {
        cartGoToReservation.addEventListener("click", function () {
            cartSidebar.classList.remove("open");
            var reservationSection = document.getElementById("reservation");
            if (reservationSection) reservationSection.scrollIntoView({ behavior: "smooth" });
        });
    }

    // ============ WORKING HOURS CHECK ============
    var dateInput = document.getElementById("reservation_date");
    var timeInput = document.getElementById("reservation_time");
    var warningBox = document.getElementById("working-hours-warning");

    function checkWorkingHours() {
        if (!dateInput || !dateInput.value || !window.CHECK_HOURS_URL) return;
        var url = window.CHECK_HOURS_URL + "?date=" + encodeURIComponent(dateInput.value);
        if (timeInput && timeInput.value) {
            url += "&time=" + encodeURIComponent(timeInput.value);
        }
        fetch(url)
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (!warningBox) return;
                if (!data.ok) {
                    warningBox.style.display = "block";
                    warningBox.textContent = data.message || "Bu vaqtda biz ishlamaymiz.";
                } else {
                    warningBox.style.display = "none";
                    warningBox.textContent = "";
                }
            })
            .catch(function () {});
    }

    if (dateInput) dateInput.addEventListener("change", checkWorkingHours);
    if (timeInput) timeInput.addEventListener("change", checkWorkingHours);

    // ============ RESERVATION FORM SUBMIT (AJAX) ============
    var reservationForm = document.getElementById("reservation-form");
    var alertBox = document.getElementById("reservation-alert");

    if (reservationForm) {
        reservationForm.addEventListener("submit", function (e) {
            e.preventDefault();

            if (cart.length === 0) {
                showAlert("Iltimos, kamida bitta taom tanlang.", "error");
                return;
            }

            var formData = new FormData(reservationForm);

            // Har bir taom turini backendga unikal ID sifatida yuboramiz
            cart.forEach(function (item) {
                if (item.type === "menu") formData.append("menu_items", item.id);
                if (item.type === "beer") formData.append("beer_items", item.id);
                if (item.type === "breakfast") formData.append("breakfast_items", item.id);
            });

            // Miqdorlar (necha ta) haqida malumotni sharh maydoniga qoshamiz,
            // shunda admin panelda aniq nechta buyurtma qilinganini korish mumkin
            var existingComment = formData.get("comment") || "";
            var summary = "Buyurtma: " + cartSummaryText() + ".";
            formData.set("comment", (existingComment ? existingComment + " | " : "") + summary);

            fetch(window.CREATE_RESERVATION_URL, {
                method: "POST",
                headers: { "X-CSRFToken": window.CSRF_TOKEN },
                body: formData,
            })
                .then(function (res) { return res.json().then(function (data) { return { status: res.status, data: data }; }); })
                .then(function (result) {
                    if (result.data.success) {
                        showAlert(result.data.message, "success");
                        reservationForm.reset();
                        cart = [];
                        renderCart();
                    } else {
                        var msgs = [];
                        for (var field in result.data.errors) {
                            var label = field === "__all__" ? "Xatolik" : field;
                            result.data.errors[field].forEach(function (err) {
                                msgs.push(label + ": " + err);
                            });
                        }
                        showAlert(msgs.join(" | ") || "Xatolik yuz berdi.", "error");
                    }
                })
                .catch(function () {
                    showAlert("Server bilan bogliqlik xatosi. Qaytadan urinib koring.", "error");
                });
        });
    }

    function showAlert(message, type) {
        if (!alertBox) return;
        alertBox.textContent = message;
        alertBox.className = type === "success" ? "reservation-alert-success" : "reservation-alert-error";
        alertBox.style.display = "block";
        alertBox.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    renderCart();
})();
