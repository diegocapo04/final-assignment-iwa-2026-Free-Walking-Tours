document.addEventListener("DOMContentLoaded", function () {
    const participantRadio = document.getElementById("role_participant");
    const guideRadio = document.getElementById("role_guide");
    const guideBlock = document.getElementById("guide_languages_block");
    const guideCheckboxes = document.querySelectorAll(".guide-language-checkbox");

    function updateRegistrationForm() {
        const isGuide = guideRadio && guideRadio.checked;
        if (guideBlock) {
            guideBlock.style.display = isGuide ? "block" : "none";
            guideCheckboxes.forEach((cb) => {
                if (!isGuide) cb.checked = false;
            });
        }
    }

    if (participantRadio && guideRadio && guideBlock) {
        participantRadio.addEventListener("change", updateRegistrationForm);
        guideRadio.addEventListener("change", updateRegistrationForm);
        updateRegistrationForm();
    }

    const stopsContainer = document.getElementById("stops-container");
    const addStopButton = document.getElementById("add-stop");

    function updateStopNumbers() {
        if (!stopsContainer) return;
        stopsContainer.querySelectorAll(".stop-row").forEach((row, index) => {
            const label = row.querySelector(".stop-number");
            if (label) label.textContent = index + 1;
        });
    }

    function createStopRow(index) {
        const div = document.createElement("div");
        div.className = "input-group mb-2 stop-row";
        div.innerHTML = `
            <span class="input-group-text stop-number">${index}</span>
            <input type="text" class="form-control" name="stop_name"
                   placeholder="Stop name" maxlength="100">
            <button type="button" class="btn btn-outline-danger remove-stop"
                    aria-label="Remove stop">✕</button>
        `;
        div.querySelector(".remove-stop").addEventListener("click", () => {
            div.remove();
            updateStopNumbers();
        });
        return div;
    }

    if (addStopButton && stopsContainer) {
        stopsContainer.querySelectorAll(".remove-stop").forEach((btn) => {
            btn.addEventListener("click", () => {
                btn.closest(".stop-row").remove();
                updateStopNumbers();
            });
        });

        addStopButton.addEventListener("click", () => {
            const currentCount = stopsContainer.querySelectorAll(".stop-row").length;
            stopsContainer.appendChild(createStopRow(currentCount + 1));
        });
    }

    const photosInput = document.getElementById("photos");
    const photoPreview = document.getElementById("photo-preview");

    if (photosInput && photoPreview) {
        photosInput.addEventListener("change", () => {
            photoPreview.innerHTML = "";
            const files = Array.from(photosInput.files);

            files.forEach((file) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = document.createElement("img");
                    img.src = e.target.result;
                    img.style.cssText = "width:80px;height:80px;object-fit:cover;border-radius:4px;";
                    img.alt = file.name;
                    photoPreview.appendChild(img);
                };
                reader.readAsDataURL(file);
            });

            if (files.length !== 5) {
                const warning = document.createElement("p");
                warning.className = "text-danger small mt-1 w-100";
                warning.textContent = `${files.length} file(s) selected. Please select exactly 5.`;
                photoPreview.appendChild(warning);
            }
        });
    }

    const guestList = document.getElementById("guest-list");
    const addGuestBtn = document.getElementById("add-guest-btn");
    const limitMsg = document.getElementById("guest-limit-msg");

    if (!guestList || !addGuestBtn) return;

    const MAX_GUESTS = 3;

    function getGuestCount() {
        return guestList.querySelectorAll(".guest-row").length;
    }

    function updateGuestUI() {
        const count = getGuestCount();
        addGuestBtn.style.display = count >= MAX_GUESTS ? "none" : "inline-block";
        if (limitMsg) limitMsg.style.display = count >= MAX_GUESTS ? "block" : "none";
    }

    addGuestBtn.addEventListener("click", function () {
        if (getGuestCount() >= MAX_GUESTS) return;

        const index = getGuestCount();
        const row = document.createElement("div");
        row.classList.add("guest-row", "row", "g-2", "mb-2", "align-items-center");
        row.innerHTML = `
            <div class="col-5">
                <input
                    type="text"
                    name="guest_first_name"
                    class="form-control form-control-sm"
                    placeholder="First name"
                    aria-label="Guest ${index + 1} first name"
                >
            </div>
            <div class="col-5">
                <input
                    type="text"
                    name="guest_last_name"
                    class="form-control form-control-sm"
                    placeholder="Last name"
                    aria-label="Guest ${index + 1} last name"
                >
            </div>
            <div class="col-2">
                <button
                    type="button"
                    class="btn btn-outline-danger btn-sm remove-guest-btn"
                    aria-label="Remove this participant"
                >&times;</button>
            </div>
        `;

        row.querySelector(".remove-guest-btn").addEventListener("click", function () {
            row.remove();
            updateGuestUI();
        });

        guestList.appendChild(row);
        updateGuestUI();
    });

});