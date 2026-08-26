document.addEventListener("DOMContentLoaded", function() {
    var input = document.getElementById("deleteEventNameInput");
    var btn = document.getElementById("confirmDeleteEventBtn");

    if (input && btn) {
        var targetName = input.getAttribute("data-target-name") || "";
        
        input.addEventListener("input", function() {
            // Ignore case and leading/trailing spaces for better UX
            btn.disabled = (input.value.trim().toLowerCase() !== targetName.trim().toLowerCase());
        });
        btn.addEventListener("click", function() {
            var form = document.getElementById("deleteVoxBentoForm_voxbento");
            if (form) {
                var submitInput = document.createElement("input");
                submitInput.type = "hidden";
                submitInput.name = "interpretation_interpreter_action";
                submitInput.value = "delete_event";
                form.appendChild(submitInput);
                form.submit();
            } else {
                console.error("Delete form not found");
            }
        });
        
        // Clear input when modal is shown (using standard DOM events in case jQuery isn't loaded)
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === "class") {
                    var modal = document.getElementById('deleteVoxBentoEventModal');
                    if (modal && modal.classList.contains('in')) {
                        input.value = "";
                        btn.disabled = true;
                        setTimeout(function() { input.focus(); }, 100);
                    }
                }
            });
        });
        var modalEl = document.getElementById('deleteVoxBentoEventModal');
        if (modalEl) {
            observer.observe(modalEl, { attributes: true });
        }
    }
});
