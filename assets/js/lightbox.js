document.addEventListener("DOMContentLoaded", () => {
  let currentIndex = null;

  const images = Array.from(document.querySelectorAll("img.cursor-zoom-in"));

  const lightbox = document.getElementById("lightbox");
  const lightboxCaption = lightbox.querySelector("figcaption");
  const lightboxImage = lightbox.querySelector("img");
  const lightboxLink = lightbox.querySelector("a");
  const lightboxClose = lightbox.querySelector("#lightboxClose");
  const lightboxPrev = lightbox.querySelector("#lightboxPrev");
  const lightboxNext = lightbox.querySelector("#lightboxNext");

  // Functions
  function openLightbox(image) {
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    lightboxCaption.textContent = image.getAttribute("data-exif") || "";
    lightboxLink.href = "https://verify.contentauthenticity.org?source=" + encodeURIComponent(image.src);
    lightboxPrev.disabled = currentIndex === 0;
    lightboxNext.disabled = currentIndex === images.length - 1;
    if (image.getAttribute("data-orientation") === "portrait") {
      lightboxImage.parentElement.classList.remove("aspect-[3/2]");
      lightboxImage.parentElement.classList.add("aspect-[2/3]");
    } else {
      lightboxImage.parentElement.classList.remove("aspect-[2/3]");
      lightboxImage.parentElement.classList.add("aspect-[3/2]");
    }
    lightbox.showModal();
    document.body.classList.add("overflow-hidden"); // Prevent background scroll
  }

  function closeLightbox() {
    lightbox.close();
    document.body.classList.remove("overflow-hidden"); // Allow background scroll
  }

  lightboxImage.onclick = closeLightbox;
  lightboxClose.onclick = closeLightbox;

  // Event listeners
  document.addEventListener("keydown", (e) => {
    if (!lightbox.open) return;

    if (e.key === "Escape") {
      closeLightbox();
    } else if ((e.key === "ArrowLeft" || e.key === "ArrowUp") && currentIndex > 0) {
      openLightbox(images[--currentIndex]);
    } else if ((e.key === "ArrowRight" || e.key === "ArrowDown") && currentIndex < images.length - 1) {
      openLightbox(images[++currentIndex]);
    }
  });

  images.forEach((image, index) => {
    image.addEventListener("click", () => {
      currentIndex = index;
      openLightbox(images[currentIndex]);
    });
  });

  lightboxPrev.onclick = () => {
    if (currentIndex > 0) {
      openLightbox(images[--currentIndex]);
    }
  };

  lightboxNext.onclick = () => {
    if (currentIndex < images.length - 1) {
      openLightbox(images[++currentIndex]);
    }
  };
});
