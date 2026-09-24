

var body = document.body;  /* Targets document body */
var toggler = document.getElementById('toggler');
document.getElementById('toggler').addEventListener('change', (event) => {
  event.target.checked ? darkmode()/* If checked, set datatheme to dark */ : lightmode()/* if unchecked, remove dark datatheme (changes to light default) */
});



const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
  darkmode();   // call datatheme and get chosen theme
} else {
  lightmode();  // otherwise goes to lightmode, which is why lightmode is default
}

function darkmode() {
  document.getElementById("toggleicon").src = "/static/images/moon.png"
  body.setAttribute('data-theme', 'dark')
  localStorage.setItem('theme', 'dark');/* localstorage so that the theme persists even if you leave page, enter another page etc*/
  toggler.checked = true; /* Fix checkbox problem*/
}

function lightmode() {
  document.getElementById("toggleicon").src = "/static/images/sun.png"
   body.removeAttribute('data-theme');
   localStorage.setItem('theme', 'light');
  toggler.checked = false;

}
 



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
