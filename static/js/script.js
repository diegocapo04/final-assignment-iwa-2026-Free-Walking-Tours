document.addEventListener("DOMContentLoaded", () => {
    const participantRadio = document.getElementById("role_participant");
    const guideRadio = document.getElementById("role_guide");
    const guideBlock = document.getElementById("guide_languages_block");
    const guideCheckboxes = document.querySelectorAll(".guide-language-checkbox");

    function updateRegistrationForm() {
        const isGuide = guideRadio && guideRadio.checked;

        if (guideBlock) {
            guideBlock.style.display = isGuide ? "block" : "none";
            guideBlock.disabled = !isGuide;
        }

        guideCheckboxes.forEach((checkbox) => {
            checkbox.required = false;

            if (!isGuide) {
                checkbox.checked = false;
            }
        });
    }

    if (participantRadio && guideRadio && guideBlock) {
        participantRadio.addEventListener("change", updateRegistrationForm);
        guideRadio.addEventListener("change", updateRegistrationForm);
        updateRegistrationForm();
    }
});