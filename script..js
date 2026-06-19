document.addEventListener("DOMContentLoaded", function() {
    const enlaces = document.querySelectorAll(".navbar a");

    enlaces.forEach(function(enlace) {
        enlace.addEventListener("click", function(event) {
            event.preventDefault();
            const destino = document.querySelector(this.getAttribute("href"));
            if (destino) {
                destino.scrollIntoView({ behavior: "smooth" });
            }
        });
    });
});

const btnArriba = document.getElementById("btn-arriba");

window.addEventListener("scroll", function() {
    if (window.scrollY > 300) {
        btnArriba.style.display = "block";
    } else {
        btnArriba.style.display = "none";
    }
});

btnArriba.addEventListener("click", function() {
    window.scrollTo({ top: 0, behavior: "smooth" });
});