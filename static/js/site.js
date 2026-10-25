document.addEventListener('DOMContentLoaded', () => {
    const lightbox = document.getElementById('image-lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const closeButton = document.getElementById('image-lightbox-close');

    if (!lightbox || !lightboxImg || !closeButton) return;

    let activeImage = null;

    const closeLightbox = () => {
        lightbox.classList.add('hidden');
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('overflow-hidden');
        if (activeImage) activeImage.focus();
        activeImage = null;
    };

    const openLightbox = image => {
        activeImage = image;
        lightboxImg.src = image.currentSrc || image.src;
        lightboxImg.alt = image.alt || 'Full resolution preview';
        lightbox.classList.remove('hidden');
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.classList.add('overflow-hidden');
        closeButton.focus();
    };

    document.querySelectorAll('section img').forEach(image => {
        image.classList.add('cursor-zoom-in');
        image.tabIndex = 0;
        image.setAttribute('role', 'button');
        image.setAttribute('aria-label', `Open image preview: ${image.alt || 'image'}`);
        image.addEventListener('click', () => openLightbox(image));
        image.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openLightbox(image);
            }
        });
    });

    closeButton.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', event => {
        if (event.target === lightbox) closeLightbox();
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !lightbox.classList.contains('hidden')) {
            closeLightbox();
        }
    });
});
