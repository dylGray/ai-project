'use strict';

document.addEventListener("DOMContentLoaded", () => {
  const helpButton = document.getElementById('help-button');
  const helpModal = document.getElementById('help-modal');
  const closeModal = document.getElementById('close-modal');

  if (helpButton && helpModal && closeModal) {
    helpButton.addEventListener('click', () => {
        helpModal.classList.remove('hidden');
    });

    closeModal.addEventListener('click', () => {
        helpModal.classList.add('hidden');
    });

    window.addEventListener('click', (e) => {
      if (e.target === helpModal) {
        helpModal.classList.add('hidden');
      }
    });
  }
});
