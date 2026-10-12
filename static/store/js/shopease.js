/* ShopEase template interactions, wired to the live Northstar store.
   Search submits the real catalog form. Newsletter confirmation is the
   template's on-page message only — addresses are not stored. */
document.addEventListener("DOMContentLoaded", function () {
    var searchForm = document.getElementById("searchForm");
    var searchInput = document.getElementById("searchInput");
    var notificationBox = document.getElementById("notification");
    var notificationMsg = document.getElementById("notificationMsg");
    var newsletterForm = document.getElementById("newsletterForm");
    var newsletterMsg = document.getElementById("newsletterMsg");

    function showNotification(message) {
        if (!notificationBox || !notificationMsg) return;
        notificationMsg.textContent = message;
        notificationBox.classList.add("show");
        window.setTimeout(function () {
            notificationBox.classList.remove("show");
        }, 2500);
    }

    if (searchForm && searchInput) {
        searchForm.addEventListener("submit", function (event) {
            if (searchInput.value.trim() === "") {
                event.preventDefault();
                showNotification("Please enter a product name to search.");
            }
        });
    }

    if (newsletterForm) {
        newsletterForm.addEventListener("submit", function (event) {
            event.preventDefault();
            var emailInput = document.getElementById("emailInput");
            var email = emailInput ? emailInput.value.trim() : "";
            if (!email) {
                if (newsletterMsg) {
                    newsletterMsg.textContent = "Please enter a valid email address.";
                    newsletterMsg.style.color = "#DC2626";
                }
                return;
            }
            if (newsletterMsg) {
                newsletterMsg.textContent = "Thank you for subscribing!";
                newsletterMsg.style.color = "#16A34A";
            }
            if (emailInput) emailInput.value = "";
            showNotification("Thank you for subscribing!");
        });
    }
});
