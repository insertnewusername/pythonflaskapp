
// IMPORTANT: THIS JAVASCRIPT IS ONLY FOR THE OLD STATIC HTML PAGES. THE JAVASCRIPT FOR THE FLASK IS IN SCRIPT.JS, did this so no conflicting code




let slideIndex = 1;

function showslides(n) {
  let slides = document.getElementsByClassName("slide");

  if (slides.length === 0) return;
  if (n > slides.length) { slideIndex = 1 }
  if (n < 1) { slideIndex = slides.length }

  for (let i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  slides[slideIndex - 1].style.display = "block";
}

showslides(slideIndex);

function plusslides(n) {
  showslides(slideIndex += n);
}

function currentslide(n) {
  showslides(slideIndex = n);
}
