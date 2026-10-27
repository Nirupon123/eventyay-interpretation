document.addEventListener("DOMContentLoaded", function () {
    const bodyEl = document.getElementById("oauth-callback-body") || document.getElementById("oauth-error-body");
    const redirectUrl = bodyEl ? bodyEl.getAttribute("data-redirect-url") : "";

    // 1. Notify listeners via BroadcastChannel
    try {
        if (typeof BroadcastChannel !== "undefined") {
            const bc = new BroadcastChannel("oauth_channel");
            bc.postMessage("oauth_complete");
        }
    } catch (e) {
        console.error("BroadcastChannel error:", e);
    }

    // 2. Notify opener window via postMessage and trigger reload
    try {
        if (window.opener && !window.opener.closed) {
            window.opener.postMessage("oauth_complete", window.location.origin);
            try {
                window.opener.location.reload();
            } catch (e) {
                // Cross-origin opener error ignore
            }
        }
    } catch (e) {
        console.error("Opener notification error:", e);
    }

    // 3. Attach click handler to Close Window button
    const closeBtn = document.getElementById("btn-close-window");
    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            window.close();
            setTimeout(function () {
                if (!window.closed && redirectUrl) {
                    window.location.href = redirectUrl;
                }
            }, 300);
        });
    }

    // 4. If this is a successful callback in a popup, auto-close after 800ms
    if (bodyEl && bodyEl.id === "oauth-callback-body" && bodyEl.getAttribute("data-success") === "true") {
        setTimeout(function () {
            try {
                window.close();
            } catch (e) {}

            // Fallback for full tabs where window.close is forbidden: navigate to redirectUrl
            setTimeout(function () {
                if (!window.closed && redirectUrl) {
                    window.location.href = redirectUrl;
                }
            }, 800);
        }, 600);
    }
});
